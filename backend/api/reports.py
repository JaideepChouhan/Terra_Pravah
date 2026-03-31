"""
Terra Pravah - Reports API
==========================
Report generation and export.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path
import json

from backend.models.models import db, Project, AnalysisJob, User

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/templates', methods=['GET'])
def list_templates():
    """List available report templates."""
    return jsonify({
        'templates': [
            {
                'id': 'engineering',
                'name': 'Engineering Design Report',
                'description': 'Comprehensive technical report with calculations and specifications',
                'sections': ['executive_summary', 'design_parameters', 'hydrological_analysis', 
                           'hydraulic_design', 'materials', 'cost_estimate', 'drawings']
            },
            {
                'id': 'construction',
                'name': 'Construction Documentation',
                'description': 'Detailed construction plans and specifications',
                'sections': ['project_overview', 'site_preparation', 'materials_list',
                           'construction_sequence', 'quality_control', 'safety']
            },
            {
                'id': 'environmental',
                'name': 'Environmental Assessment',
                'description': 'Environmental impact analysis and mitigation measures',
                'sections': ['existing_conditions', 'impact_analysis', 'mitigation_measures',
                           'monitoring_plan', 'compliance']
            },
            {
                'id': 'permit',
                'name': 'Permit Application Package',
                'description': 'Documentation for regulatory permit applications',
                'sections': ['application_form', 'project_description', 'design_drawings',
                           'calculations', 'environmental_review']
            },
            {
                'id': 'client',
                'name': 'Client Presentation',
                'description': 'Executive summary for client presentations',
                'sections': ['overview', 'key_findings', 'recommendations', 'cost_summary']
            },
            {
                'id': 'maintenance',
                'name': 'Maintenance Manual',
                'description': 'Operation and maintenance guidelines',
                'sections': ['system_overview', 'inspection_schedule', 'maintenance_procedures',
                           'troubleshooting', 'contact_information']
            }
        ]
    })


@reports_bp.route('/projects/<project_id>/generate', methods=['POST'])
@jwt_required()
def generate_report(project_id):
    """Generate a report for a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if project.status != 'completed':
        return jsonify({'error': 'Project analysis must be completed first'}), 400
    
    data = request.get_json() or {}
    
    template_id = data.get('template', 'engineering')
    format_type = data.get('format', 'pdf')
    sections = data.get('sections', [])
    options = data.get('options', {})
    
    if format_type not in ['pdf', 'docx', 'html', 'json']:
        return jsonify({'error': 'Unsupported format'}), 400
    
    # Get analysis results
    job = AnalysisJob.query.filter_by(
        project_id=project_id,
        status='completed'
    ).order_by(AnalysisJob.completed_at.desc()).first()
    
    if not job or not job.result:
        return jsonify({'error': 'No analysis results available'}), 404
    
    # Generate report
    try:
        report_path = generate_report_file(
            project=project,
            results=job.result,
            template_id=template_id,
            format_type=format_type,
            sections=sections,
            options=options
        )
        
        return jsonify({
            'message': 'Report generated successfully',
            'report_path': str(report_path),
            'download_url': f'/api/reports/download/{project_id}/{Path(report_path).name}'
        })
        
    except Exception as e:
        current_app.logger.error(f"Report generation failed: {e}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


def generate_report_file(project, results, template_id, format_type, sections, options):
    """Generate report file based on template and format."""
    
    # Create reports directory
    reports_dir = Path(current_app.config['RESULTS_FOLDER']) / project.id / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{project.name.replace(' ', '_')}_{template_id}_{timestamp}"
    
    if format_type == 'json':
        # JSON report
        report_data = {
            'project': project.to_dict(include_details=True),
            'results': results,
            'generated_at': datetime.utcnow().isoformat(),
            'template': template_id
        }
        
        output_path = reports_dir / f"{filename}.json"
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_path
    
    elif format_type == 'html':
        # HTML report
        html_content = generate_html_report(project, results, template_id, options)
        
        output_path = reports_dir / f"{filename}.html"
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path
    
    elif format_type == 'pdf':
        # For PDF, first generate HTML then convert
        # This is a placeholder - in production, use weasyprint or similar
        html_content = generate_html_report(project, results, template_id, options)
        
        output_path = reports_dir / f"{filename}.html"  # Return HTML for now
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path
    
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def generate_html_report(project, results, template_id, options):
    """Generate HTML report content."""
    
    # Get company branding
    logo_url = options.get('logo_url', '')
    company_name = options.get('company_name', 'Terra Pravah')
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project.name} - Drainage Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #4ade80; padding-bottom: 20px; }}
        .header h1 {{ font-size: 28px; color: #1a1a1a; margin-bottom: 10px; }}
        .header .subtitle {{ color: #666; font-size: 16px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ font-size: 20px; color: #1a1a1a; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
        .section h3 {{ font-size: 16px; color: #333; margin: 15px 0 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #4ade80; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }}
        @media print {{ .container {{ max-width: 100%; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project.name}</h1>
            <div class="subtitle">Drainage Network Analysis Report</div>
            <div class="subtitle">Generated: {datetime.utcnow().strftime('%B %d, %Y')}</div>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{project.description or 'This report presents the results of a comprehensive drainage network analysis.'}</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{results.get('total_channels', 0)}</div>
                    <div class="stat-label">Total Channels</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{results.get('total_length_km', 0):.2f} km</div>
                    <div class="stat-label">Network Length</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{results.get('total_outlets', 0)}</div>
                    <div class="stat-label">Outlet Points</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{results.get('peak_flow_m3s', 0):.2f}</div>
                    <div class="stat-label">Peak Flow (m³/s)</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Project Information</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Project Name</td><td>{project.name}</td></tr>
                <tr><td>Location</td><td>{project.location_name or 'Not specified'}</td></tr>
                <tr><td>Coordinate System</td><td>EPSG:{project.epsg_code or 'Not specified'}</td></tr>
                <tr><td>Units</td><td>{project.units.capitalize()}</td></tr>
                <tr><td>Design Storm</td><td>{project.design_storm_years}-Year Return Period</td></tr>
                <tr><td>Runoff Coefficient</td><td>{project.runoff_coefficient}</td></tr>
                <tr><td>Flow Algorithm</td><td>{project.flow_algorithm.upper()}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Network Summary</h2>
            <h3>Channel Classification</h3>
            <table>
                <tr><th>Type</th><th>Count</th><th>Length (m)</th></tr>
                <tr><td>Primary Channels</td><td>{results.get('primary_count', 0)}</td><td>{results.get('primary_length_m', 0):.1f}</td></tr>
                <tr><td>Secondary Channels</td><td>{results.get('secondary_count', 0)}</td><td>{results.get('secondary_length_m', 0):.1f}</td></tr>
                <tr><td>Tertiary Channels</td><td>{results.get('tertiary_count', 0)}</td><td>{results.get('tertiary_length_m', 0):.1f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Design Recommendations</h2>
            <p>Based on the terrain analysis and hydrological calculations, the following design recommendations are provided:</p>
            <ul style="margin: 15px 0; padding-left: 30px;">
                <li>Primary drainage channels should be designed for capacity of at least {results.get('peak_flow_m3s', 0):.2f} m³/s</li>
                <li>Minimum channel slope of 0.5% recommended to ensure self-cleaning velocity</li>
                <li>Consider erosion protection at high-velocity sections</li>
                <li>Outlet structures should include energy dissipation</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by {company_name} | Terra Pravah Drainage Analysis Platform</p>
            <p>Report ID: {project.id}</p>
        </div>
    </div>
</body>
</html>
"""
    return html


@reports_bp.route('/download/<project_id>/<filename>', methods=['GET'])
@jwt_required()
def download_report(project_id, filename):
    """Download a generated report."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Secure the filename
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(filename)
    
    report_path = Path(current_app.config['RESULTS_FOLDER']) / project_id / 'reports' / safe_filename
    
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    # Determine mime type
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.html': 'text/html',
        '.json': 'application/json'
    }
    
    mime_type = mime_types.get(report_path.suffix.lower(), 'application/octet-stream')
    
    return send_file(
        str(report_path),
        mimetype=mime_type,
        as_attachment=True,
        download_name=safe_filename
    )


@reports_bp.route('/projects/<project_id>/list', methods=['GET'])
@jwt_required()
def list_project_reports(project_id):
    """List all reports generated for a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    reports_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id / 'reports'
    
    if not reports_dir.exists():
        return jsonify({'reports': []})
    
    reports = []
    for f in reports_dir.iterdir():
        if f.is_file():
            reports.append({
                'filename': f.name,
                'size_bytes': f.stat().st_size,
                'created_at': datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
                'download_url': f'/api/reports/download/{project_id}/{f.name}'
            })
    
    # Sort by creation date, newest first
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'reports': reports
    })
