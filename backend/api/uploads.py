"""
Terra Pravah - Uploads API
==========================
File upload handling for DTM and other geospatial files.
Auto-generates DTM visualization after upload.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import os
import threading

from backend.models.models import db, Project, User
from backend.services.dtm_builder_service import DTMBuilderService

uploads_bp = Blueprint('uploads', __name__)


def generate_dtm_visualization_async(project_id: str, dtm_path: str, app):
    """
    Generate DTM visualization in background thread.
    Creates both raw DTM and ready-for-drainage visualizations.
    """
    with app.app_context():
        try:
            from backend.services.visualization_service import VisualizationService
            
            # Create output directory
            results_dir = Path(app.config.get('RESULTS_FOLDER', 'results')) / project_id
            results_dir.mkdir(parents=True, exist_ok=True)
            
            vis_dir = results_dir / 'visualizations'
            vis_dir.mkdir(exist_ok=True)
            
            # Generate raw DTM visualization
            vis_service = VisualizationService(dtm_path, str(vis_dir))
            vis_service.load_terrain()
            
            # Create raw DTM visualization
            raw_dtm_path = vis_service.create_raw_dtm_visualization()
            
            # Update project with visualization path
            project = Project.query.get(project_id)
            if project:
                project.visualization_path = raw_dtm_path
                project.status = 'dtm_ready'
                db.session.commit()
                
            app.logger.info(f"DTM visualization generated for project {project_id}")
            
        except Exception as e:
            app.logger.error(f"DTM visualization failed for project {project_id}: {e}")
            # Update project status
            project = Project.query.get(project_id)
            if project:
                project.status = 'dtm_error'
                db.session.commit()


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'tif', 'tiff'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def allowed_lidar_file(filename):
    """Check if LiDAR file extension is allowed for DTM generation."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'las', 'laz'}


def get_file_info(file_path):
    """Get information about an uploaded file."""
    path = Path(file_path)
    
    info = {
        'name': path.name,
        'size_bytes': path.stat().st_size,
        'size_mb': path.stat().st_size / (1024 * 1024),
        'extension': path.suffix.lower()
    }
    
    # Try to get geospatial info if it's a GeoTIFF
    if path.suffix.lower() in ['.tif', '.tiff']:
        try:
            import rasterio
            with rasterio.open(str(path)) as src:
                info.update({
                    'width': src.width,
                    'height': src.height,
                    'crs': str(src.crs) if src.crs else None,
                    'bounds': list(src.bounds) if src.bounds else None,
                    'resolution': src.res,
                    'dtype': str(src.dtypes[0]),
                    'band_count': src.count
                })
        except Exception as e:
            current_app.logger.warning(f"Could not read raster info: {e}")
    
    return info


@uploads_bp.route('/dtm', methods=['POST'])
@jwt_required()
def upload_dtm():
    """Upload a DTM file for a project."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check file presence
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported formats: GeoTIFF (.tif, .tiff)'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    plan = current_app.config['PLANS'].get(user.subscription_plan, {})
    max_size = plan.get('max_file_size_mb', 100) * 1024 * 1024
    
    if file_size > max_size:
        return jsonify({
            'error': f'File too large. Maximum size for your plan: {plan.get("max_file_size_mb", 100)}MB'
        }), 413
    
    # Get project ID from form or query
    project_id = request.form.get('project_id') or request.args.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Create unique filename
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())[:8]
    save_filename = f"{file_id}_{filename}"
    
    # Create project upload directory
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    save_path = upload_dir / save_filename
    file.save(str(save_path))
    
    # Get file info
    file_info = get_file_info(save_path)
    
    # Update project
    project.dtm_file_path = str(save_path)
    project.dtm_file_size = file_size
    
    # Update bounding box if available
    if file_info.get('bounds'):
        project.bounding_box = file_info['bounds']
    
    # Update user storage
    user.storage_used_bytes += file_size
    
    db.session.commit()
    
    # Start background generation of DTM visualization
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=generate_dtm_visualization_async,
        args=(project_id, str(save_path), app)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'File uploaded successfully. DTM visualization is being generated.',
        'file': {
            'path': str(save_path),
            **file_info
        },
        'project_id': project_id,
        'visualization_status': 'generating'
    })


@uploads_bp.route('/las', methods=['POST'])
@jwt_required()
def upload_las():
    """Upload a LAS/LAZ file for built-in DTM generation."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_lidar_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported formats: LAS/LAZ (.las, .laz)'}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    plan = current_app.config['PLANS'].get(user.subscription_plan, {})
    max_size = plan.get('max_file_size_mb', 100) * 1024 * 1024
    if file_size > max_size:
        return jsonify({
            'error': f'File too large. Maximum size for your plan: {plan.get("max_file_size_mb", 100)}MB'
        }), 413

    project_id = request.form.get('project_id') or request.args.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())[:8]
    save_filename = f"{file_id}_{filename}"

    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_path = upload_dir / save_filename
    file.save(str(save_path))

    user.storage_used_bytes += file_size
    project.status = 'draft'
    db.session.commit()

    return jsonify({
        'message': 'LAS/LAZ file uploaded successfully.',
        'file': {
            'name': save_path.name,
            'path': str(save_path),
            'size_bytes': file_size,
            'size_mb': file_size / (1024 * 1024),
            'extension': save_path.suffix.lower()
        },
        'project_id': project_id
    })


@uploads_bp.route('/build-dtm', methods=['POST'])
@jwt_required()
def build_dtm_from_las():
    """
    Build a hydrologically conditioned DTM from a LAS/LAZ file.

    Body (JSON):
    {
      "project_id": "...",               # required
      "filename": "survey_site.las",     # required
      "resolution": 1.0,                   # optional
      "epsg": "EPSG:32644"               # optional
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    project_id = data.get('project_id')
    filename = data.get('filename')
    epsg = data.get('epsg')

    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    if not filename:
        return jsonify({'error': 'filename is required'}), 400

    try:
        resolution = float(data.get('resolution', 1.0))
    except (TypeError, ValueError):
        return jsonify({'error': 'resolution must be a number'}), 400

    if resolution <= 0:
        return jsonify({'error': 'resolution must be greater than 0'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    safe_name = secure_filename(filename)
    if not allowed_lidar_file(safe_name):
        return jsonify({'error': 'filename must be a .las or .laz file'}), 400

    project_results_folder = Path(current_app.config['RESULTS_FOLDER']) / project_id
    project_results_folder.mkdir(parents=True, exist_ok=True)

    try:
        service = DTMBuilderService(
            upload_folder=str(current_app.config['UPLOAD_FOLDER']),
            results_folder=str(project_results_folder),
        )

        project.status = 'processing'
        db.session.commit()

        relative_las_path = os.path.join(project_id, safe_name)
        result = service.process_las(
            las_filename=relative_las_path,
            resolution=resolution,
            epsg=epsg,
        )

        dtm_path = result.get('dtm_path')
        metadata = result.get('metadata', {})
        bounds = metadata.get('bounds')

        if dtm_path and os.path.exists(dtm_path):
            project.dtm_file_path = dtm_path
            project.dtm_file_size = os.path.getsize(dtm_path)
            project.results_path = str(project_results_folder)

        if bounds and len(bounds) == 4:
            xmin, xmax, ymin, ymax = bounds
            project.bounding_box = [xmin, ymin, xmax, ymax]

        project.processed_at = datetime.utcnow()
        project.status = 'completed'
        db.session.commit()

        return jsonify(result), 200

    except FileNotFoundError as exc:
        project.status = 'failed'
        db.session.commit()
        return jsonify({'error': str(exc)}), 404
    except Exception as exc:
        current_app.logger.exception('DTM build failed')
        project.status = 'failed'
        db.session.commit()
        return jsonify({'error': str(exc)}), 500


@uploads_bp.route('/preview/<project_id>', methods=['GET'])
@jwt_required()
def get_preview(project_id):
    """Get preview image of uploaded DTM."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.dtm_file_path:
        return jsonify({'error': 'No DTM file uploaded'}), 404
    
    # Generate or return cached preview
    preview_path = Path(project.dtm_file_path).parent / 'preview.png'
    
    if not preview_path.exists():
        try:
            generate_preview(project.dtm_file_path, str(preview_path))
        except Exception as e:
            current_app.logger.error(f"Preview generation failed: {e}")
            return jsonify({'error': 'Could not generate preview'}), 500
    
    return send_file(str(preview_path), mimetype='image/png')


def generate_preview(dtm_path, output_path, width=400):
    """Generate a preview image from DTM."""
    try:
        import rasterio
        import numpy as np
        from PIL import Image
        
        with rasterio.open(dtm_path) as src:
            # Read data with reduced resolution
            data = src.read(1, out_shape=(
                int(src.height * width / src.width),
                width
            ))
            
            # Normalize to 0-255
            valid_data = data[data != src.nodata] if src.nodata else data
            min_val = np.min(valid_data)
            max_val = np.max(valid_data)
            
            if max_val > min_val:
                normalized = ((data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                normalized = np.zeros_like(data, dtype=np.uint8)
            
            # Apply hillshade-like effect
            img = Image.fromarray(normalized)
            img.save(output_path, 'PNG')
            
    except ImportError:
        raise Exception("Required libraries (rasterio, PIL) not available")


@uploads_bp.route('/<project_id>/files', methods=['GET'])
@jwt_required()
def list_project_files(project_id):
    """List all files in a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    files = []
    
    # Check upload directory
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / project_id
    if upload_dir.exists():
        for f in upload_dir.iterdir():
            if f.is_file():
                files.append({
                    'name': f.name,
                    'size_bytes': f.stat().st_size,
                    'size_mb': f.stat().st_size / (1024 * 1024),
                    'type': 'upload',
                    'path': str(f)
                })
    
    # Check results directory
    results_dir = Path(current_app.config['RESULTS_FOLDER']) / project_id
    if results_dir.exists():
        for f in results_dir.rglob('*'):
            if f.is_file():
                files.append({
                    'name': f.name,
                    'size_bytes': f.stat().st_size,
                    'size_mb': f.stat().st_size / (1024 * 1024),
                    'type': 'result',
                    'path': str(f)
                })
    
    return jsonify({
        'files': files,
        'total_count': len(files),
        'total_size_mb': sum(f['size_mb'] for f in files)
    })


@uploads_bp.route('/<project_id>/files/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(project_id, filename):
    """Delete a specific file from a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Look for file in upload directory
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / project_id
    file_path = upload_dir / secure_filename(filename)
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    # Get file size before deletion
    file_size = file_path.stat().st_size
    
    # Delete file
    file_path.unlink()
    
    # Update project if it was the DTM
    if str(file_path) == project.dtm_file_path:
        project.dtm_file_path = None
        project.dtm_file_size = None
    
    # Update user storage
    user = User.query.get(user_id)
    if user:
        user.storage_used_bytes = max(0, user.storage_used_bytes - file_size)
    
    db.session.commit()
    
    return jsonify({
        'message': 'File deleted successfully'
    })


@uploads_bp.route('/samples', methods=['GET'])
def list_sample_files():
    """List available sample DTM files."""
    samples = []
    
    # Check for sample data directories
    sample_dirs = [
        Path(current_app.config.get('BASE_DIR', '.')) / 'Kitchener_lidar',
        Path(current_app.config.get('BASE_DIR', '.')) / 'sample_data'
    ]
    
    for sample_dir in sample_dirs:
        if sample_dir.exists():
            for f in sample_dir.glob('*.tif'):
                samples.append({
                    'name': f.name,
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024),
                    'location': sample_dir.name
                })
            for f in sample_dir.glob('*.las'):
                samples.append({
                    'name': f.name,
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024),
                    'location': sample_dir.name
                })
            for f in sample_dir.glob('*.laz'):
                samples.append({
                    'name': f.name,
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024),
                    'location': sample_dir.name
                })
    
    return jsonify({
        'samples': samples
    })


@uploads_bp.route('/samples/<filename>/use', methods=['POST'])
@jwt_required()
def use_sample_file(filename):
    """Use a sample file for a project."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Find sample file
    sample_file = None
    sample_dirs = [
        Path(current_app.config.get('BASE_DIR', '.')) / 'Kitchener_lidar',
        Path(current_app.config.get('BASE_DIR', '.')) / 'sample_data'
    ]
    
    for sample_dir in sample_dirs:
        potential_path = sample_dir / secure_filename(filename)
        if potential_path.exists():
            sample_file = potential_path
            break
    
    if not sample_file:
        return jsonify({'error': 'Sample file not found'}), 404
    
    # Copy to project directory
    import shutil
    
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = upload_dir / sample_file.name
    shutil.copy(str(sample_file), str(dest_path))
    
    # Get file info
    file_info = get_file_info(dest_path)
    
    # Update project only when sample is an existing GeoTIFF DTM
    if dest_path.suffix.lower() in {'.tif', '.tiff'}:
        project.dtm_file_path = str(dest_path)
        project.dtm_file_size = dest_path.stat().st_size

        if file_info.get('bounds'):
            project.bounding_box = file_info['bounds']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Sample file loaded successfully',
        'file': {
            'path': str(dest_path),
            **file_info
        }
    })
