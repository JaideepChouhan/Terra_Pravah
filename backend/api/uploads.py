"""
Terra Pravah - Uploads API
==========================
File upload handling for DTM and other geospatial files.
Auto-generates DTM visualization after upload.
Uses smart file format detection instead of extension-only validation.
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
from backend.services.dtm_builder_ai import DTMBuilderServiceAI
from backend.utils.file_validator import FileFormatDetector, validate_uploaded_file

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


def validate_and_get_file_info(file_path):
    """
    Validate file and get comprehensive information using smart detection.
    
    Returns:
        tuple: (is_valid, file_info_or_error_dict)
    """
    path = Path(file_path)
    
    # Get max file size from config
    max_size_mb = int(current_app.config.get('MAX_FILE_SIZE_MB', 500))
    
    # Perform comprehensive validation
    validation_result = validate_uploaded_file(path, max_size_mb)
    
    if not validation_result['is_valid']:
        return False, {
            'errors': validation_result['errors'],
            'warnings': validation_result.get('warnings', [])
        }
    
    # Build file info from validation result
    format_info = validation_result['format_info']
    
    info = {
        'name': path.name,
        'size_bytes': path.stat().st_size,
        'size_mb': path.stat().st_size / (1024 * 1024),
        'extension': format_info['extension'],
        'format_type': format_info['format_type'],
        'mime_type': format_info.get('mime_type'),
        'is_cog': format_info.get('is_cog', False),
        **format_info.get('details', {})
    }
    
    # Add warnings if any
    if validation_result.get('warnings'):
        info['warnings'] = validation_result['warnings']
    
    return True, info


@uploads_bp.route('/dtm', methods=['POST'])
@jwt_required()
def upload_dtm():
    """
    Upload a raster DTM file for a project.
    Supports GeoTIFF, Cloud Optimized GeoTIFF (COG), and other raster formats.
    Uses smart file format detection.
    """
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
    
    # Save file temporarily
    file.save(str(save_path))
    
    # Validate file and get comprehensive info
    is_valid, file_info = validate_and_get_file_info(save_path)
    
    if not is_valid:
        # Delete invalid file
        save_path.unlink(missing_ok=True)
        return jsonify({
            'error': 'File validation failed',
            'details': file_info.get('errors', ['Unknown error'])
        }), 400
    
    # Check if format is raster
    if file_info['format_type'] != 'raster':
        save_path.unlink(missing_ok=True)
        return jsonify({
            'error': f'Invalid file type. Expected raster format (GeoTIFF, COG, TIFF), got {file_info["format_type"]}'
        }), 400
    
    file_size = file_info['size_bytes']
    
    # Update project
    project.dtm_file_path = str(save_path)
    project.dtm_file_size = file_size
    
    # Update bounding box if available
    if file_info.get('bounds'):
        project.bounding_box = file_info['bounds']
    
    # Update user storage
    user.storage_used_bytes += file_size
    
    db.session.commit()
    
    # Log COG detection
    if file_info.get('is_cog'):
        current_app.logger.info(f"Cloud Optimized GeoTIFF detected for project {project_id}")
    
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
        'file': file_info,
        'project_id': project_id,
        'visualization_status': 'generating'
    })


@uploads_bp.route('/las', methods=['POST'])
@jwt_required()
def upload_las():
    """
    Upload a LAS/LAZ file for built-in DTM generation.
    Uses smart file format detection.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

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

    # Validate file and get info
    is_valid, file_info = validate_and_get_file_info(save_path)
    
    if not is_valid:
        # Delete invalid file
        save_path.unlink(missing_ok=True)
        return jsonify({
            'error': 'File validation failed',
            'details': file_info.get('errors', ['Unknown error'])
        }), 400
    
    # Check if format is LiDAR
    if file_info['format_type'] != 'lidar':
        save_path.unlink(missing_ok=True)
        return jsonify({
            'error': f'Invalid file type. Expected LiDAR format (LAS, LAZ), got {file_info["format_type"]}'
        }), 400

    file_size = file_info['size_bytes']
    user.storage_used_bytes += file_size
    db.session.commit()

    return jsonify({
        'message': 'LAS/LAZ file uploaded successfully',
        'file': {
            'name': file_info['name'],
            'path': str(save_path),
            'size_mb': file_info['size_mb'],
            **file_info
        },
        'project_id': project_id
    })


@uploads_bp.route('/build-dtm', methods=['POST'])
@jwt_required()
def build_dtm_from_las():
    """
    Build a hydrologically conditioned AI-powered DTM from a LAS/LAZ file.
    Uses the DTMPointNet2 AI model for ground classification.

    Body (JSON):
    {
      "project_id": "...",               # required
      "filename": "survey_site.las",     # required
      "resolution": 1.0,                 # optional (default 1.0)
      "epsg": "EPSG:32644"               # optional
    }
    
    Returns:
    {
      "dtm_path": "results/.../file.cog.tif",
      "validation": {...},
      "metadata": {...},
      "ai_classification": {...}
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    project_id = data.get('project_id')
    filename = data.get('filename')
    epsg = data.get('epsg')

    # Input validation
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

    # Project validation
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    if project.owner_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    safe_name = secure_filename(filename)
    if not (safe_name.lower().endswith('.las') or safe_name.lower().endswith('.laz')):
        return jsonify({'error': 'filename must be a .las or .laz file'}), 400

    project_results_folder = Path(current_app.config['RESULTS_FOLDER']) / project_id
    project_results_folder.mkdir(parents=True, exist_ok=True)

    try:
        # Get absolute paths for AI model
        base_dir = Path(__file__).parent.parent.parent  # Go up to project root
        model_path = str(base_dir / 'backend' / 'models' / 'dtm_outputs_finetuned' / 'best_model.pth')
        threshold_json = str(base_dir / 'backend' / 'models' / 'dtm_outputs_finetuned' / 'threshold.json')

        # Initialize AI-powered DTM builder
        service = DTMBuilderServiceAI(
            upload_folder=str(current_app.config['UPLOAD_FOLDER']),
            results_folder=str(project_results_folder),
            model_path=model_path,
            threshold_json=threshold_json,
        )

        project.status = 'processing'
        db.session.commit()

        # Process the LAS file with AI model
        relative_las_path = os.path.join(project_id, safe_name)
        result = service.process_las(
            las_filename=relative_las_path,
            resolution=resolution,
            epsg=epsg,
        )

        dtm_path = result.get('dtm_path')
        metadata = result.get('metadata', {})
        ai_stats = result.get('ai_classification', {})
        bounds = metadata.get('bounds')

        # Update project with DTM information
        if dtm_path and os.path.exists(dtm_path):
            project.dtm_file_path = dtm_path
            project.dtm_file_size = os.path.getsize(dtm_path)
            project.results_path = str(project_results_folder)

        if bounds and len(bounds) == 4:
            xmin, xmax, ymin, ymax = bounds
            project.bounding_box = [xmin, ymin, xmax, ymax]

        # Store AI classification stats
        project.metadata = {
            'ai_classification': ai_stats,
            'dtm_metadata': metadata,
            'created_with': 'DTMPointNet2'
        }

        project.processed_at = datetime.utcnow()
        project.status = 'completed'
        db.session.commit()

        current_app.logger.info(
            f"DTM build successful for project {project_id}. "
            f"Ground points: {ai_stats.get('ground_points', 'N/A')}, "
            f"Threshold: {ai_stats.get('threshold', 'N/A')}"
        )

        return jsonify(result), 200

    except FileNotFoundError as e:
        current_app.logger.error(f"File not found error: {e}")
        project.status = 'error'
        db.session.commit()
        return jsonify({
            'error': 'File not found',
            'details': str(e)
        }), 404

    except Exception as e:
        import traceback
        error_msg = f"Error building AI DTM: {e}\n{traceback.format_exc()}"
        current_app.logger.error(error_msg)
        
        project.status = 'error'
        project.metadata = {
            'error': str(e),
            'error_type': type(e).__name__
        }
        db.session.commit()
        
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__,
            'details': 'Check server logs for details'
        }), 500


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
