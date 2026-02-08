"""
Terra Pravah - Analysis API
============================
Drainage analysis processing and job management.
"""

from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token, verify_jwt_in_request
from pathlib import Path
import threading
import uuid

from backend.models.models import db, Project, AnalysisJob, User
from backend.services.drainage_service import DrainageAnalysisService


def jwt_required_with_query_param():
    """
    Custom decorator that accepts JWT token from either:
    1. Authorization header (standard)
    2. Query parameter 'token' (for iframe/embed use cases)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # First try to get token from query parameter
            token = request.args.get('token')
            if token:
                try:
                    # Decode and verify the token
                    decoded = decode_token(token)
                    # Store the identity for get_jwt_identity() to work
                    request.jwt_identity = decoded.get('sub')
                    return fn(*args, **kwargs)
                except Exception as e:
                    current_app.logger.error(f"Token validation failed: {e}")
                    return jsonify({'error': 'Invalid token'}), 401
            
            # Fall back to standard JWT verification
            try:
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'Authorization Required',
                    'message': 'Authentication token is missing.'
                }), 401
        
        return wrapper
    return decorator


def get_current_user_id():
    """Get user ID from either custom jwt_identity or standard JWT."""
    if hasattr(request, 'jwt_identity') and request.jwt_identity:
        return request.jwt_identity
    return get_jwt_identity()

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/start', methods=['POST'])
@jwt_required()
def start_analysis():
    """Start a new drainage analysis job."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        # Check if user is collaborator with edit permission
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.dtm_file_path:
        return jsonify({'error': 'No DTM file uploaded for this project'}), 400
    
    # Check if there's already a running job
    running_job = AnalysisJob.query.filter_by(
        project_id=project_id,
        status='processing'
    ).first()
    
    if running_job:
        return jsonify({
            'error': 'Analysis already in progress',
            'job_id': running_job.id
        }), 409
    
    # Create job
    job = AnalysisJob(
        project_id=project_id,
        job_type=data.get('job_type', 'full_analysis'),
        config={
            'runoff_coefficient': data.get('runoff_coefficient', project.runoff_coefficient),
            'design_storm_years': data.get('design_storm_years', project.design_storm_years),
            'flow_algorithm': data.get('flow_algorithm', project.flow_algorithm),
            'stream_threshold_pct': data.get('stream_threshold_pct', 1.0)
        },
        created_by_id=user_id
    )
    
    db.session.add(job)
    
    # Update project status
    project.status = 'processing'
    
    db.session.commit()
    
    # Start background analysis
    thread = threading.Thread(
        target=run_analysis_background,
        args=(current_app._get_current_object(), job.id, project_id)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Analysis started',
        'job': job.to_dict()
    }), 202


def run_analysis_background(app, job_id, project_id):
    """Run analysis in background thread."""
    with app.app_context():
        job = AnalysisJob.query.get(job_id)
        project = Project.query.get(project_id)
        
        if not job or not project:
            return
        
        try:
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            # Run analysis using service
            service = DrainageAnalysisService(
                dtm_path=project.dtm_file_path,
                output_dir=str(Path(app.config['RESULTS_FOLDER']) / project_id),
                config=job.config
            )
            
            # Progress callback
            def update_progress(progress, step):
                job.progress = progress
                job.current_step = step
                db.session.commit()
            
            result = service.run_full_analysis(progress_callback=update_progress)
            
            # Update project with results
            project.status = 'completed'
            project.total_channels = result.get('total_channels', 0)
            project.total_length_km = result.get('total_length_km', 0)
            project.total_outlets = result.get('total_outlets', 0)
            project.peak_flow_m3s = result.get('peak_flow_m3s')
            project.primary_count = result.get('primary_count', 0)
            project.secondary_count = result.get('secondary_count', 0)
            project.tertiary_count = result.get('tertiary_count', 0)
            project.results_path = result.get('results_path')
            project.geojson_path = result.get('geojson_path')
            project.visualization_path = result.get('visualization_path')
            project.processed_at = datetime.utcnow()
            
            # Update job
            job.status = 'completed'
            job.progress = 100
            job.current_step = 'Complete'
            job.completed_at = datetime.utcnow()
            job.result = result
            
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f"Analysis failed: {e}")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            project.status = 'failed'
            
            db.session.commit()


@analysis_bp.route('/jobs/<job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """Get analysis job status."""
    user_id = get_jwt_identity()
    job = AnalysisJob.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Check access through project
    project = Project.query.get(job.project_id)
    if not project or project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'job': job.to_dict()
    })


@analysis_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_job(job_id):
    """Cancel a running analysis job."""
    user_id = get_jwt_identity()
    job = AnalysisJob.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    project = Project.query.get(job.project_id)
    if not project or project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if job.status not in ['queued', 'processing']:
        return jsonify({'error': 'Job cannot be cancelled'}), 400
    
    job.status = 'cancelled'
    job.completed_at = datetime.utcnow()
    
    project.status = 'draft'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Job cancelled',
        'job': job.to_dict()
    })


@analysis_bp.route('/projects/<project_id>/results', methods=['GET'])
@jwt_required()
def get_analysis_results(project_id):
    """Get analysis results for a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if project.status != 'completed':
        return jsonify({'error': 'Analysis not complete'}), 400
    
    # Get latest completed job
    job = AnalysisJob.query.filter_by(
        project_id=project_id,
        status='completed'
    ).order_by(AnalysisJob.completed_at.desc()).first()
    
    if not job or not job.result:
        return jsonify({'error': 'No results available'}), 404
    
    return jsonify({
        'results': job.result,
        'project': project.to_dict(include_details=True)
    })


@analysis_bp.route('/projects/<project_id>/visualization', methods=['GET'])
@jwt_required_with_query_param()
def get_visualization(project_id):
    """
    Get visualization HTML for a project with drainage network overlay.
    If analysis is complete, shows DTM with drainage network.
    If not, shows raw DTM.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id / 'visualizations'
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if analysis is complete and GeoJSON exists
    geojson_path = project.geojson_path
    has_drainage = geojson_path and Path(geojson_path).exists()
    
    # Check for cached visualization with drainage
    drainage_vis_path = results_dir / 'drainage_network.html'
    
    if has_drainage and drainage_vis_path.exists():
        return send_file(str(drainage_vis_path), mimetype='text/html')
    
    # If we have drainage data, generate the visualization
    if has_drainage and project.dtm_file_path:
        try:
            from backend.services.visualization_service import VisualizationService
            
            vis_service = VisualizationService(project.dtm_file_path, str(results_dir))
            vis_service.load_terrain()
            
            # Load drainage lines from GeoJSON
            drainage_lines = []
            outlets = []
            
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)
                
            for feature in geojson_data.get('features', []):
                geom_type = feature.get('geometry', {}).get('type', '')
                coords = feature.get('geometry', {}).get('coordinates', [])
                props = feature.get('properties', {})
                
                if geom_type == 'LineString':
                    channel_type = props.get('type', 'tertiary')
                    # Convert coords to tuple format with elevation
                    coord_tuples = []
                    for c in coords:
                        if len(c) >= 3:
                            coord_tuples.append((c[0], c[1], c[2]))
                        else:
                            coord_tuples.append((c[0], c[1], 0))
                    
                    if len(coord_tuples) >= 2:
                        drainage_lines.append((channel_type, coord_tuples, props))
                        
                elif geom_type == 'Point' and props.get('type') == 'outlet':
                    if len(coords) >= 3:
                        outlets.append({'x': coords[0], 'y': coords[1], 'z': coords[2]})
            
            # Create the drainage visualization
            path = vis_service.create_drainage_visualization(drainage_lines, outlets)
            
            return send_file(path, mimetype='text/html')
            
        except Exception as e:
            current_app.logger.error(f"Failed to generate drainage visualization: {e}")
            # Fall back to basic visualization
    
    # Fall back to stored visualization or generate raw DTM
    if project.visualization_path and Path(project.visualization_path).exists():
        return send_file(str(project.visualization_path), mimetype='text/html')
    
    # Generate raw DTM visualization if nothing else available
    if project.dtm_file_path:
        try:
            from backend.services.visualization_service import VisualizationService
            vis_service = VisualizationService(project.dtm_file_path, str(results_dir))
            path = vis_service.create_raw_dtm_visualization()
            return send_file(path, mimetype='text/html')
        except Exception as e:
            current_app.logger.error(f"Failed to generate DTM visualization: {e}")
    
    return jsonify({'error': 'Visualization not available'}), 404


@analysis_bp.route('/projects/<project_id>/comparison', methods=['GET'])
@jwt_required_with_query_param()
def get_comparison_visualization(project_id):
    """
    Get side-by-side comparison visualization for a project.
    Shows raw DTM next to DTM with drainage network overlay.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check for existing comparison visualization
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id / 'visualizations'
    comparison_path = results_dir / 'dtm_comparison.html'
    
    if comparison_path.exists():
        return send_file(str(comparison_path), mimetype='text/html')
    
    # Generate on-demand if not exists but project has DTM
    if not project.dtm_file_path:
        return jsonify({'error': 'No DTM file available for this project'}), 400
    
    try:
        from backend.services.drainage_service import DrainageAnalysisService
        
        service = DrainageAnalysisService(
            dtm_path=project.dtm_file_path,
            output_dir=str(results_dir.parent)
        )
        
        geojson_path = project.geojson_path
        if geojson_path and Path(geojson_path).exists():
            path = service.create_standalone_comparison(geojson_path)
        else:
            # Just show raw DTM comparison (without drainage)
            from backend.services.visualization_service import VisualizationService
            vis_service = VisualizationService(project.dtm_file_path, str(results_dir))
            vis_service.load_terrain()
            path = vis_service.create_side_by_side_visualization([], [])
        
        return send_file(path, mimetype='text/html')
        
    except Exception as e:
        current_app.logger.error(f"Failed to generate comparison: {e}")
        return jsonify({'error': 'Failed to generate comparison visualization'}), 500


@analysis_bp.route('/projects/<project_id>/raw-dtm', methods=['GET'])
@jwt_required_with_query_param()
def get_raw_dtm_visualization(project_id):
    """
    Get raw DTM visualization without drainage overlay.
    Useful for comparing before/after analysis.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.dtm_file_path:
        return jsonify({'error': 'No DTM file available for this project'}), 400
    
    try:
        from backend.services.visualization_service import VisualizationService
        
        results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id / 'visualizations'
        vis_service = VisualizationService(project.dtm_file_path, str(results_dir))
        path = vis_service.create_raw_dtm_visualization()
        
        return send_file(path, mimetype='text/html')
        
    except Exception as e:
        current_app.logger.error(f"Failed to generate raw DTM visualization: {e}")
        return jsonify({'error': 'Failed to generate visualization'}), 500


@analysis_bp.route('/projects/<project_id>/geojson', methods=['GET'])
@jwt_required()
def get_geojson(project_id):
    """Get GeoJSON drainage network for a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.geojson_path:
        return jsonify({'error': 'GeoJSON not available'}), 404
    
    geojson_path = Path(project.geojson_path)
    if not geojson_path.exists():
        return jsonify({'error': 'GeoJSON file not found'}), 404
    
    return send_file(
        str(geojson_path),
        mimetype='application/geo+json'
    )


@analysis_bp.route('/algorithms', methods=['GET'])
def list_algorithms():
    """List available flow algorithms."""
    return jsonify({
        'algorithms': [
            {
                'id': 'd8',
                'name': 'D8',
                'description': 'Standard 8-direction flow routing. Fast but may produce parallel flows.',
                'suitable_for': 'Quick analysis, flat terrain'
            },
            {
                'id': 'dinf',
                'name': 'D-Infinity (D∞)',
                'description': 'Distributes flow between multiple downslope cells. More accurate for divergent flow.',
                'suitable_for': 'Detailed analysis, hillslopes, professional use'
            },
            {
                'id': 'mfd',
                'name': 'Multiple Flow Direction',
                'description': 'Distributes flow proportionally to all downslope neighbors.',
                'suitable_for': 'Diffuse flow patterns, groundwater analysis'
            }
        ]
    })


@analysis_bp.route('/design-standards', methods=['GET'])
def list_design_standards():
    """List available design standards."""
    return jsonify({
        'standards': [
            {
                'id': 'asce',
                'name': 'ASCE Manual of Practice',
                'region': 'USA',
                'description': 'American Society of Civil Engineers drainage design standards'
            },
            {
                'id': 'hec',
                'name': 'HEC-HMS/HEC-RAS',
                'region': 'USA',
                'description': 'US Army Corps of Engineers hydrological modeling standards'
            },
            {
                'id': 'ciria',
                'name': 'CIRIA SuDS Manual',
                'region': 'UK',
                'description': 'Construction Industry Research and Information Association SuDS guidance'
            },
            {
                'id': 'australian',
                'name': 'Australian Rainfall and Runoff',
                'region': 'Australia',
                'description': 'Australian national guidelines for flood estimation'
            },
            {
                'id': 'indian',
                'name': 'IRC/IS Standards',
                'region': 'India',
                'description': 'Indian Roads Congress and Bureau of Indian Standards'
            },
            {
                'id': 'custom',
                'name': 'Custom Standards',
                'region': 'Global',
                'description': 'Define custom design parameters'
            }
        ]
    })


@analysis_bp.route('/projects/<project_id>/report', methods=['GET'])
@jwt_required()
def get_detailed_report(project_id):
    """
    Get detailed drainage network report for a project.
    Returns comprehensive analysis with channel details, hydraulics, and recommendations.
    """
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Look for the report JSON file
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id
    report_path = results_dir / 'drainage_report.json'
    
    if report_path.exists():
        import json
        with open(report_path, 'r') as f:
            report = json.load(f)
        return jsonify({
            'report': report,
            'project': project.to_dict()
        })
    
    # If no report exists, return basic info from project
    return jsonify({
        'report': {
            'project': {
                'name': project.name,
                'description': project.description,
                'location': project.location_name,
                'design_storm_years': project.design_storm_years,
                'runoff_coefficient': project.runoff_coefficient,
                'flow_algorithm': project.flow_algorithm
            },
            'network_summary': {
                'total_channels': project.total_channels or 0,
                'total_length_km': project.total_length_km or 0,
                'outlets': project.total_outlets or 0
            },
            'hydraulics': {
                'peak_flow_m3s': project.peak_flow_m3s or 0
            },
            'status': project.status
        },
        'project': project.to_dict()
    })


@analysis_bp.route('/projects/<project_id>/status', methods=['GET'])
@jwt_required()
def get_project_analysis_status(project_id):
    """
    Get quick status check for project analysis.
    Used by frontend to poll for completion.
    """
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get latest job if any
    latest_job = AnalysisJob.query.filter_by(
        project_id=project_id
    ).order_by(AnalysisJob.created_at.desc()).first()
    
    return jsonify({
        'project_id': project_id,
        'status': project.status,
        'has_dtm': bool(project.dtm_file_path),
        'has_visualization': bool(project.visualization_path),
        'has_analysis': project.status == 'completed',
        'latest_job': latest_job.to_dict() if latest_job else None,
        'summary': {
            'total_channels': project.total_channels,
            'total_length_km': project.total_length_km,
            'total_outlets': project.total_outlets,
            'peak_flow_m3s': project.peak_flow_m3s
        } if project.status == 'completed' else None
    })


@analysis_bp.route('/projects/<project_id>/download/report', methods=['GET'])
@jwt_required_with_query_param()
def download_report_json(project_id):
    """
    Download the drainage analysis report as JSON.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id
    report_path = results_dir / 'drainage_report.json'
    
    if report_path.exists():
        return send_file(
            str(report_path),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{project.name.replace(" ", "_")}_drainage_report.json'
        )
    
    # Generate report on-the-fly if not available
    report_data = {
        'project': {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'location': project.location_name,
            'design_storm_years': project.design_storm_years,
            'runoff_coefficient': project.runoff_coefficient,
            'flow_algorithm': project.flow_algorithm,
            'created_at': str(project.created_at),
            'processed_at': str(project.processed_at) if project.processed_at else None
        },
        'network_summary': {
            'total_channels': project.total_channels or 0,
            'primary_channels': project.primary_count or 0,
            'secondary_channels': project.secondary_count or 0,
            'tertiary_channels': project.tertiary_count or 0,
            'total_length_km': project.total_length_km or 0,
            'outlets': project.total_outlets or 0
        },
        'hydraulics': {
            'peak_flow_m3s': project.peak_flow_m3s or 0
        },
        'status': project.status
    }
    
    from flask import Response
    return Response(
        json.dumps(report_data, indent=2),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename={project.name.replace(" ", "_")}_drainage_report.json'
        }
    )


@analysis_bp.route('/projects/<project_id>/download/geojson', methods=['GET'])
@jwt_required_with_query_param()
def download_geojson(project_id):
    """
    Download the drainage network as GeoJSON.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.geojson_path or not Path(project.geojson_path).exists():
        return jsonify({'error': 'GeoJSON not available for this project'}), 404
    
    return send_file(
        project.geojson_path,
        mimetype='application/geo+json',
        as_attachment=True,
        download_name=f'{project.name.replace(" ", "_")}_drainage_network.geojson'
    )


@analysis_bp.route('/projects/<project_id>/download/csv', methods=['GET'])
@jwt_required_with_query_param()
def download_csv(project_id):
    """
    Download the channel data as CSV.
    """
    user_id = get_current_user_id()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id
    report_path = results_dir / 'drainage_report.json'
    
    if not report_path.exists():
        return jsonify({'error': 'Report not available for CSV export'}), 404
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    channels = report.get('channels', [])
    if not channels:
        return jsonify({'error': 'No channel data available'}), 404
    
    # Build CSV content
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Channel ID', 'Type', 'Length (m)', 'Slope', 'Upstream Elevation (m)',
        'Downstream Elevation (m)', 'Flow (m³/s)', 'Velocity (m/s)', 
        'Pipe Diameter (mm)', 'Catchment Area (km²)'
    ])
    
    # Data rows
    for i, ch in enumerate(channels):
        writer.writerow([
            i + 1,
            ch.get('type', 'unknown'),
            round(ch.get('length_m', 0), 2),
            round(ch.get('slope', 0), 4),
            round(ch.get('upstream_elev', 0), 2),
            round(ch.get('downstream_elev', 0), 2),
            round(ch.get('flow_m3s', 0), 4),
            round(ch.get('velocity_ms', 0), 2),
            ch.get('pipe_diameter_mm', 'N/A'),
            round(ch.get('catchment_area_km2', 0), 4)
        ])
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={project.name.replace(" ", "_")}_channels.csv'
        }
    )
