"""
Terra Pravah - Visualization Service
=====================================
Service for generating DTM and drainage network visualizations.
Supports side-by-side comparison views.
"""

import numpy as np
import rasterio
from rasterio.transform import xy
from pathlib import Path
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class VisualizationService:
    """
    Service for creating professional DTM and drainage visualizations.
    Supports side-by-side comparison of raw terrain vs drainage overlay.
    """
    
    def __init__(self, dtm_path: str, output_dir: str):
        """
        Initialize visualization service.
        
        Args:
            dtm_path: Path to DTM raster file
            output_dir: Output directory for generated visualizations
        """
        self.dtm_path = Path(dtm_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.dtm = None
        self.transform = None
        self.crs = None
        self.nodata_mask = None
        self.resolution = None
        
        # Optimized sampling settings for faster rendering
        self.max_points = 100  # Reduced from 150 for faster loading
        
    def load_terrain(self):
        """Load terrain data from DTM file."""
        with rasterio.open(self.dtm_path) as src:
            self.dtm = src.read(1).astype(np.float64)
            self.transform = src.transform
            self.crs = src.crs
            self.resolution = src.res[0]
            nodata = src.nodata
            
        if nodata is not None:
            self.dtm[self.dtm == nodata] = np.nan
            
        self.nodata_mask = np.isnan(self.dtm)
        
        return self
    
    def _sample_terrain(self):
        """Sample terrain for performant rendering."""
        rows, cols = self.dtm.shape
        sample_step = max(1, min(rows, cols) // self.max_points)
        
        z_sampled = self.dtm[::sample_step, ::sample_step].copy()
        
        x_grid = np.zeros_like(z_sampled)
        y_grid = np.zeros_like(z_sampled)
        
        for i, r in enumerate(range(0, rows, sample_step)):
            for j, c in enumerate(range(0, cols, sample_step)):
                if i < z_sampled.shape[0] and j < z_sampled.shape[1]:
                    x, y = xy(self.transform, r, c)
                    x_grid[i, j] = x
                    y_grid[i, j] = y
                    
        z_display = np.where(np.isnan(z_sampled), None, z_sampled)
        
        return x_grid, y_grid, z_display, z_sampled
    
    def create_terrain_surface(self, colorscale='earth'):
        """
        Create a Plotly surface for terrain visualization.
        
        Args:
            colorscale: Color scheme - 'earth', 'viridis', 'terrain'
            
        Returns:
            go.Surface trace
        """
        x_grid, y_grid, z_display, z_sampled = self._sample_terrain()
        
        colorscales = {
            'earth': [
                [0.0, 'rgb(34, 139, 34)'],
                [0.25, 'rgb(144, 238, 144)'],
                [0.5, 'rgb(210, 180, 140)'],
                [0.75, 'rgb(139, 90, 43)'],
                [1.0, 'rgb(105, 105, 105)']
            ],
            'terrain': [
                [0.0, 'rgb(0, 100, 0)'],
                [0.2, 'rgb(34, 139, 34)'],
                [0.4, 'rgb(245, 245, 220)'],
                [0.6, 'rgb(139, 119, 101)'],
                [0.8, 'rgb(128, 128, 128)'],
                [1.0, 'rgb(255, 255, 255)']
            ],
            'viridis': 'Viridis'
        }
        
        return go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_display,
            colorscale=colorscales.get(colorscale, colorscales['earth']),
            opacity=0.95,
            showscale=True,
            colorbar=dict(
                title=dict(text='Elevation (m)', side='right'),
                thickness=15,
                len=0.6,
                x=1.02,
                tickformat='.0f'
            ),
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                specular=0.2,
                roughness=0.8
            ),
            hovertemplate='<b>Terrain</b><br>Elevation: %{z:.1f}m<extra></extra>',
            name='Terrain'
        )
    
    def create_raw_dtm_visualization(self) -> str:
        """
        Create visualization of raw DTM data without drainage overlay.
        
        Returns:
            Path to generated HTML file
        """
        if self.dtm is None:
            self.load_terrain()
            
        fig = go.Figure()
        fig.add_trace(self.create_terrain_surface('earth'))
        
        # Layout
        x_grid, y_grid, z_display, z_sampled = self._sample_terrain()
        valid_z = z_sampled[~np.isnan(z_sampled)]
        z_range = valid_z.max() - valid_z.min() if len(valid_z) > 0 else 1
        
        fig.update_layout(
            title=dict(
                text='<b>Digital Terrain Model</b>',
                x=0.5,
                font=dict(size=16, color='#333')
            ),
            scene=dict(
                xaxis=dict(
                    title='Easting (m)',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)',
                    showbackground=False
                ),
                yaxis=dict(
                    title='Northing (m)',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)',
                    showbackground=False
                ),
                zaxis=dict(
                    title='Elevation (m)',
                    showgrid=True,
                    gridcolor='rgba(200,200,200,0.3)',
                    showbackground=False
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.3),
                camera=dict(
                    eye=dict(x=1.4, y=1.4, z=0.8),
                    up=dict(x=0, y=0, z=1)
                ),
                bgcolor='rgba(248,248,255,1)'
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor='white'
        )
        
        output_path = self.output_dir / 'dtm_raw.html'
        self._write_html(fig, output_path, 'Digital Terrain Model')
        
        return str(output_path)
    
    def create_drainage_visualization(self, drainage_lines: list = None, outlets: list = None) -> str:
        """
        Create DTM visualization with drainage network overlay.
        
        Args:
            drainage_lines: List of (type, coords, props) drainage lines
            outlets: List of outlet points
            
        Returns:
            Path to generated HTML file
        """
        if self.dtm is None:
            self.load_terrain()
            
        fig = go.Figure()
        
        # Add terrain surface
        fig.add_trace(self.create_terrain_surface('earth'))
        
        # Add drainage lines
        if drainage_lines:
            self._add_drainage_traces(fig, drainage_lines)
        
        # Add outlets
        if outlets:
            outlet_xs = [o['x'] for o in outlets if 'x' in o]
            outlet_ys = [o['y'] for o in outlets if 'y' in o]
            outlet_zs = [o.get('z', 0) + 2 for o in outlets]
            
            if outlet_xs:
                fig.add_trace(go.Scatter3d(
                    x=outlet_xs,
                    y=outlet_ys,
                    z=outlet_zs,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='rgba(220, 20, 60, 0.9)',
                        symbol='diamond',
                        line=dict(width=2, color='white')
                    ),
                    name='Outlets',
                    hovertemplate='<b>Outlet</b><br>Elev: %{z:.1f}m<extra></extra>'
                ))
        
        # Calculate channel stats for title
        total_channels = len(drainage_lines) if drainage_lines else 0
        primary_count = sum(1 for d in drainage_lines if d[0] == 'primary') if drainage_lines else 0
        secondary_count = sum(1 for d in drainage_lines if d[0] == 'secondary') if drainage_lines else 0
        tertiary_count = sum(1 for d in drainage_lines if d[0] == 'tertiary') if drainage_lines else 0
        
        title_text = f'<b>Drainage Network Analysis</b><br><span style="font-size:12px">Total: {total_channels} channels | Primary: {primary_count} | Secondary: {secondary_count} | Tertiary: {tertiary_count}</span>'
        
        # Layout
        fig.update_layout(
            title=dict(
                text=title_text,
                x=0.5,
                font=dict(size=16, color='white')
            ),
            scene=dict(
                xaxis=dict(
                    title='Easting (m)',
                    showgrid=True,
                    gridcolor='rgba(100,100,100,0.3)',
                    showbackground=False,
                    color='white'
                ),
                yaxis=dict(
                    title='Northing (m)',
                    showgrid=True,
                    gridcolor='rgba(100,100,100,0.3)',
                    showbackground=False,
                    color='white'
                ),
                zaxis=dict(
                    title='Elevation (m)',
                    showgrid=True,
                    gridcolor='rgba(100,100,100,0.3)',
                    showbackground=False,
                    color='white'
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.3),
                camera=dict(
                    eye=dict(x=1.4, y=1.4, z=0.8),
                    up=dict(x=0, y=0, z=1)
                ),
                bgcolor='rgba(26,26,46,1)'
            ),
            margin=dict(l=10, r=10, t=60, b=10),
            paper_bgcolor='#1a1a2e',
            legend=dict(
                yanchor='top', y=0.95,
                xanchor='left', x=0.02,
                bgcolor='rgba(30,30,50,0.9)',
                bordercolor='rgba(100,100,150,0.5)',
                borderwidth=1,
                font=dict(size=11, color='white')
            )
        )
        
        output_path = self.output_dir / 'drainage_network.html'
        self._write_html(fig, output_path, 'Drainage Network Analysis')
        
        return str(output_path)
    
    def create_side_by_side_visualization(self, drainage_lines: list = None, outlets: list = None) -> str:
        """
        Create side-by-side visualization: Raw DTM | DTM + Drainage Network.
        
        Args:
            drainage_lines: List of (type, coords, props) drainage lines
            outlets: List of outlet points
            
        Returns:
            Path to generated HTML file
        """
        if self.dtm is None:
            self.load_terrain()
            
        # Generate the split view HTML with two separate 3D canvases
        output_path = self.output_dir / 'dtm_comparison.html'
        
        # Create terrain data for both views
        x_grid, y_grid, z_display, z_sampled = self._sample_terrain()
        valid_z = z_sampled[~np.isnan(z_sampled)]
        
        # Create left figure (raw terrain)
        fig_left = go.Figure()
        fig_left.add_trace(self.create_terrain_surface('earth'))
        
        # Create right figure (terrain + drainage)
        fig_right = go.Figure()
        fig_right.add_trace(self.create_terrain_surface('earth'))
        
        # Add drainage lines to right figure
        if drainage_lines:
            self._add_drainage_traces(fig_right, drainage_lines)
            
        # Add outlets to right figure
        if outlets:
            fig_right.add_trace(go.Scatter3d(
                x=[o['x'] for o in outlets],
                y=[o['y'] for o in outlets],
                z=[o['z'] + 1.5 for o in outlets],
                mode='markers',
                marker=dict(
                    size=6,
                    color='rgba(220, 20, 60, 0.8)',
                    symbol='diamond',
                    line=dict(width=1, color='white')
                ),
                name='Outlets',
                hovertemplate='<b>Outlet</b><br>Elev: %{z:.1f}m<extra></extra>'
            ))
        
        # Common scene settings
        scene_settings = dict(
            xaxis=dict(
                title='Easting (m)',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                showbackground=False
            ),
            yaxis=dict(
                title='Northing (m)',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                showbackground=False
            ),
            zaxis=dict(
                title='Elevation (m)',
                showgrid=True,
                gridcolor='rgba(200,200,200,0.3)',
                showbackground=False
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.3),
            camera=dict(
                eye=dict(x=1.4, y=1.4, z=0.8),
                up=dict(x=0, y=0, z=1)
            ),
            bgcolor='rgba(248,248,255,1)'
        )
        
        fig_left.update_layout(
            title=dict(text='<b>Raw DTM</b>', x=0.5, font=dict(size=14)),
            scene=scene_settings,
            margin=dict(l=5, r=5, t=40, b=5),
            paper_bgcolor='white',
            showlegend=False
        )
        
        fig_right.update_layout(
            title=dict(text='<b>DTM + Drainage Network</b>', x=0.5, font=dict(size=14)),
            scene=scene_settings,
            margin=dict(l=5, r=5, t=40, b=5),
            paper_bgcolor='white',
            legend=dict(
                yanchor='top', y=0.95,
                xanchor='left', x=0.02,
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='rgba(200,200,200,0.5)',
                borderwidth=1,
                font=dict(size=9)
            )
        )
        
        # Generate split-view HTML
        self._write_split_view_html(fig_left, fig_right, output_path, drainage_lines, outlets)
        
        return str(output_path)
    
    def _add_drainage_traces(self, fig, drainage_lines):
        """Add drainage network traces to a figure."""
        base_colors = {
            'primary': {'light': (100, 180, 255), 'dark': (0, 50, 150)},
            'secondary': {'light': (130, 210, 255), 'dark': (20, 100, 180)},
            'tertiary': {'light': (170, 230, 255), 'dark': (60, 140, 200)}
        }
        
        widths = {'primary': 6, 'secondary': 4, 'tertiary': 2.5}
        legend_added = set()
        
        for channel_type, coords, props in drainage_lines:
            if len(coords) < 2:
                continue
                
            # Sort by elevation for proper flow direction
            elevs = [c[2] for c in coords]
            if elevs[0] < elevs[-1]:
                coords = coords[::-1]
                
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            zs = [c[2] + 0.5 for c in coords]
            
            # Create gradient colors
            n_points = len(coords)
            light = base_colors.get(channel_type, base_colors['tertiary'])['light']
            dark = base_colors.get(channel_type, base_colors['tertiary'])['dark']
            
            colors = []
            for i in range(n_points):
                t = i / max(n_points - 1, 1)
                r = int(light[0] + t * (dark[0] - light[0]))
                g = int(light[1] + t * (dark[1] - light[1]))
                b = int(light[2] + t * (dark[2] - light[2]))
                colors.append(f'rgb({r},{g},{b})')
            
            show_legend = channel_type not in legend_added
            legend_added.add(channel_type)
            
            flow = props.get('peak_flow_m3s', 0)
            pipe = props.get('pipe_diameter_mm', 0)
            length = props.get('length_m', 0)
            
            # Add line segments
            for i in range(len(xs) - 1):
                fig.add_trace(go.Scatter3d(
                    x=[xs[i], xs[i+1]],
                    y=[ys[i], ys[i+1]],
                    z=[zs[i], zs[i+1]],
                    mode='lines',
                    line=dict(color=colors[i], width=widths.get(channel_type, 2)),
                    name=f'{channel_type.title()} Channel' if (show_legend and i == 0) else None,
                    legendgroup=channel_type,
                    showlegend=(show_legend and i == 0),
                    hovertemplate=(
                        f'<b>{channel_type.title()} Drainage</b><br>'
                        f'Flow: {flow:.3f} m³/s<br>'
                        f'Pipe: {pipe} mm<br>'
                        f'Length: {length:.0f} m<br>'
                        f'Elev: %{{z:.1f}}m<extra></extra>'
                    )
                ))
    
    def _write_html(self, fig, output_path, title):
        """Write a single figure to optimized HTML for fast loading."""
        fig_json = fig.to_json()
        config_json = json.dumps({
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True,
            'staticPlot': False
        })
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-gl3d-2.27.0.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            overflow: hidden;
        }}
        #chart {{ width: 100vw; height: 100vh; }}
        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 1.2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}
        .spinner {{
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <div class="spinner"></div>
        <span>Loading 3D visualization...</span>
    </div>
    <div id="chart"></div>
    <script>
        const figureData = {fig_json};
        const chartConfig = {config_json};
        
        // Render immediately
        Plotly.newPlot('chart', figureData.data, figureData.layout, chartConfig)
            .then(function() {{
                document.getElementById('loading').classList.add('hidden');
            }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _write_split_view_html(self, fig_left, fig_right, output_path, drainage_lines=None, outlets=None):
        """Write split-view comparison HTML."""
        fig_left_json = fig_left.to_json()
        fig_right_json = fig_right.to_json()
        
        config_json = json.dumps({
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True
        })
        
        # Calculate statistics
        total_channels = len(drainage_lines) if drainage_lines else 0
        primary_count = sum(1 for d in drainage_lines if d[0] == 'primary') if drainage_lines else 0
        secondary_count = sum(1 for d in drainage_lines if d[0] == 'secondary') if drainage_lines else 0
        tertiary_count = sum(1 for d in drainage_lines if d[0] == 'tertiary') if drainage_lines else 0
        total_length = sum(d[2].get('length_m', 0) for d in drainage_lines) / 1000 if drainage_lines else 0
        outlet_count = len(outlets) if outlets else 0
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terra Pravah - DTM Comparison</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" defer></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .header h1 {{
            color: #333;
            font-size: 1.8rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 0.95rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-top: 15px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 1.4rem;
            font-weight: bold;
            color: #4a5568;
        }}
        
        .stat-card .label {{
            font-size: 0.75rem;
            color: #718096;
            margin-top: 4px;
        }}
        
        .stat-card.primary .value {{ color: #3182ce; }}
        .stat-card.secondary .value {{ color: #38a169; }}
        .stat-card.tertiary .value {{ color: #805ad5; }}
        
        .comparison-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        @media (max-width: 1200px) {{
            .comparison-container {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .chart-panel {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            position: relative;
        }}
        
        .chart-panel h2 {{
            position: absolute;
            top: 10px;
            left: 20px;
            z-index: 100;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 1rem;
            color: #333;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart {{
            width: 100%;
            height: 70vh;
            min-height: 450px;
        }}
        
        .sync-controls {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 1000;
        }}
        
        .sync-controls label {{
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            color: #333;
        }}
        
        .sync-controls input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.85rem;
            margin-top: 20px;
        }}
        
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 50;
        }}
        
        .loading.hidden {{ display: none; }}
        
        .spinner {{
            width: 40px;
            height: 40px;
            border: 3px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🌊 Terra Pravah - DTM Analysis</h1>
            <p class="subtitle">Side-by-side comparison: Raw terrain data vs. Drainage network overlay</p>
            
            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="value">{primary_count}</div>
                    <div class="label">Primary Channels</div>
                </div>
                <div class="stat-card secondary">
                    <div class="value">{secondary_count}</div>
                    <div class="label">Secondary Channels</div>
                </div>
                <div class="stat-card tertiary">
                    <div class="value">{tertiary_count}</div>
                    <div class="label">Tertiary Channels</div>
                </div>
                <div class="stat-card">
                    <div class="value">{total_length:.1f} km</div>
                    <div class="label">Total Length</div>
                </div>
                <div class="stat-card">
                    <div class="value">{outlet_count}</div>
                    <div class="label">Outlets</div>
                </div>
            </div>
        </header>
        
        <div class="comparison-container">
            <div class="chart-panel">
                <h2>📍 Raw DTM Data</h2>
                <div class="loading" id="loading-left">
                    <div class="spinner"></div>
                    <span style="color: #666;">Loading...</span>
                </div>
                <div id="chart-left" class="chart"></div>
            </div>
            
            <div class="chart-panel">
                <h2>🌊 DTM + Drainage Network</h2>
                <div class="loading" id="loading-right">
                    <div class="spinner"></div>
                    <span style="color: #666;">Loading...</span>
                </div>
                <div id="chart-right" class="chart"></div>
            </div>
        </div>
        
        <div class="sync-controls">
            <label>
                <input type="checkbox" id="sync-cameras" checked>
                Sync camera views
            </label>
            <label>
                <input type="checkbox" id="sync-zoom" checked>
                Sync zoom
            </label>
        </div>
        
        <footer class="footer">
            Generated by Terra Pravah | D∞ (D-Infinity) Flow Routing Algorithm
        </footer>
    </div>
    
    <script>
        const figLeftData = {fig_left_json};
        const figRightData = {fig_right_json};
        const chartConfig = {config_json};
        
        let syncCameras = true;
        let syncZoom = true;
        let isUpdating = false;
        
        document.addEventListener('DOMContentLoaded', function() {{
            const loadingLeft = document.getElementById('loading-left');
            const loadingRight = document.getElementById('loading-right');
            
            // Check for Plotly
            function waitForPlotly(callback) {{
                if (typeof Plotly !== 'undefined') {{
                    callback();
                }} else {{
                    setTimeout(() => waitForPlotly(callback), 100);
                }}
            }}
            
            waitForPlotly(function() {{
                // Render left chart (raw DTM)
                Plotly.newPlot('chart-left', figLeftData.data, figLeftData.layout, chartConfig)
                    .then(() => loadingLeft.classList.add('hidden'));
                
                // Render right chart (DTM + drainage)
                Plotly.newPlot('chart-right', figRightData.data, figRightData.layout, chartConfig)
                    .then(() => loadingRight.classList.add('hidden'));
                
                // Camera sync functionality
                const chartLeft = document.getElementById('chart-left');
                const chartRight = document.getElementById('chart-right');
                
                function syncCamera(sourceChart, targetChart) {{
                    if (isUpdating || !syncCameras) return;
                    isUpdating = true;
                    
                    const sourceLayout = sourceChart.layout;
                    if (sourceLayout && sourceLayout.scene && sourceLayout.scene.camera) {{
                        const camera = sourceLayout.scene.camera;
                        Plotly.relayout(targetChart, {{'scene.camera': camera}});
                    }}
                    
                    setTimeout(() => {{ isUpdating = false; }}, 50);
                }}
                
                chartLeft.on('plotly_relayout', function(eventData) {{
                    if (eventData['scene.camera']) {{
                        syncCamera(chartLeft, chartRight);
                    }}
                }});
                
                chartRight.on('plotly_relayout', function(eventData) {{
                    if (eventData['scene.camera']) {{
                        syncCamera(chartRight, chartLeft);
                    }}
                }});
                
                // Control handlers
                document.getElementById('sync-cameras').addEventListener('change', function(e) {{
                    syncCameras = e.target.checked;
                }});
                
                document.getElementById('sync-zoom').addEventListener('change', function(e) {{
                    syncZoom = e.target.checked;
                }});
            }});
        }});
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            if (typeof Plotly !== 'undefined') {{
                Plotly.Plots.resize('chart-left');
                Plotly.Plots.resize('chart-right');
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def create_comparison_visualization(dtm_path: str, output_dir: str, 
                                    drainage_lines: list = None, 
                                    outlets: list = None) -> dict:
    """
    Convenience function to create comparison visualizations.
    
    Args:
        dtm_path: Path to DTM file
        output_dir: Output directory
        drainage_lines: Optional drainage line data
        outlets: Optional outlet data
        
    Returns:
        dict with paths to generated visualizations
    """
    service = VisualizationService(dtm_path, output_dir)
    service.load_terrain()
    
    results = {
        'raw_dtm': service.create_raw_dtm_visualization()
    }
    
    if drainage_lines is not None:
        results['comparison'] = service.create_side_by_side_visualization(
            drainage_lines, outlets
        )
    
    return results
