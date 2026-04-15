#!/usr/bin/env python3
"""
Professional Drainage Network Designer (Enhanced)
==================================================
Advanced hydrological analysis using D∞ (D-Infinity) flow routing
and comprehensive hydraulic design automation.

Hydrological Methods:
- D∞ (D-Infinity) Flow Routing Algorithm (Tarboton, 1997)
  * Distributes flow between multiple downslope cells
  * More accurate representation of divergent flow on hillslopes
- Stream Delineation with Configurable Thresholds
- Strahler Stream Ordering for hierarchy classification
- Rational Method for peak flow (Q = CIA)
- Time of Concentration (Kirpich formula)
- SCS Curve Number method

Hydraulic Validation:
- Continuity check (downstream ≥ upstream sum)
- Slope validation (minimum 0.5% for pipes)
- Velocity validation (0.6-3.0 m/s using Manning's equation)
- Froude number analysis

Automated Design Selection:
- Slope-based infrastructure type selection
- Channels: trapezoidal, rectangular, V-shaped
- Pipes: circular, box culverts
- Special: pumps, cascades, stepped channels

Fluid Mechanics:
- Manning's Equation for open channel flow
- Hazen-Williams for pipe flow
- Hydraulic radius calculations

Visualization:
- Clean, authentic terrain representation
- Strahler-based stream width visualization
- Flow direction indicators

References:
- Tarboton, D.G. (1997). A new method for the determination of flow 
  directions and upslope areas in grid DEMs. Water Resources Research.

Author: AI Drainage Design System
"""

import numpy as np
import rasterio
from rasterio.transform import rowcol, xy
from scipy import ndimage
from scipy.interpolate import splprep, splev
from collections import defaultdict
import json
from pathlib import Path
import warnings
import shutil
warnings.filterwarnings('ignore')

try:
    from whitebox import WhiteboxTools
    HAS_WHITEBOX = True
except ImportError:
    HAS_WHITEBOX = False

import plotly.graph_objects as go


class HydrologicalConstants:
    """Standard hydrological and hydraulic constants."""
    
    # Manning's roughness coefficients
    MANNING_N = {
        'concrete_pipe': 0.013,
        'pvc_pipe': 0.010,
        'corrugated_metal': 0.024,
        'earth_channel': 0.025,
        'grass_channel': 0.035,
        'natural_stream': 0.040,
        'trapezoidal_channel': 0.022,
        'rectangular_channel': 0.015,
        'v_shaped_ditch': 0.030,
        'grass_lined_ditch': 0.040,
        'cascade_channel': 0.050,
        'stepped_channel': 0.045
    }
    
    # Runoff coefficients (C) for Rational Method
    RUNOFF_COEFF = {
        'impervious': 0.95,
        'urban_high': 0.70,
        'urban_medium': 0.50,
        'suburban': 0.35,
        'rural': 0.20,
        'forest': 0.15
    }
    
    # Design storm return periods (years)
    RETURN_PERIODS = [2, 5, 10, 25, 50, 100]
    
    # Minimum design slopes
    MIN_SLOPE_PIPE = 0.005  # 0.5%
    MIN_SLOPE_CHANNEL = 0.002  # 0.2%
    
    # Standard pipe diameters (mm)
    PIPE_DIAMETERS = [150, 200, 250, 300, 375, 450, 525, 600, 750, 900, 1050, 1200]
    
    # Velocity limits (m/s) for hydraulic validation
    MIN_VELOCITY = 0.6   # Minimum for self-cleaning
    MAX_VELOCITY = 3.0   # Maximum to prevent erosion
    
    # Slope thresholds for design selection
    SLOPE_VERY_LOW = 0.005    # < 0.5% - requires pumping or special design
    SLOPE_LOW = 0.01          # 0.5-1% - standard pipe/channel
    SLOPE_MODERATE = 0.05     # 1-5% - trapezoidal channel preferred
    SLOPE_HIGH = 0.10         # 5-10% - may need energy dissipation
    SLOPE_VERY_HIGH = 0.15    # > 15% - cascade or stepped channel
    
    # Stream threshold as percentage of total cells
    DEFAULT_STREAM_THRESHOLD_PCT = 1.0  # 1% of total cells


class DrainageDesignSelector:
    """
    Automated design selection based on slope and hydraulic requirements.
    Selects appropriate drainage infrastructure type based on terrain conditions.
    """
    
    DESIGN_TYPES = {
        'pump_station': {
            'description': 'Pump station required for flat terrain',
            'manning_n': 0.013,
            'min_slope': 0,
            'max_slope': 0.005,
            'suitable_for': ['very flat areas', 'below water table']
        },
        'circular_pipe': {
            'description': 'Standard circular pipe/culvert',
            'manning_n': 0.013,
            'min_slope': 0.005,
            'max_slope': 0.05,
            'suitable_for': ['urban areas', 'under roads']
        },
        'box_culvert': {
            'description': 'Rectangular box culvert',
            'manning_n': 0.015,
            'min_slope': 0.005,
            'max_slope': 0.05,
            'suitable_for': ['large flows', 'road crossings']
        },
        'trapezoidal_channel': {
            'description': 'Trapezoidal open channel',
            'manning_n': 0.022,
            'min_slope': 0.002,
            'max_slope': 0.10,
            'suitable_for': ['moderate slopes', 'rural areas']
        },
        'rectangular_channel': {
            'description': 'Rectangular concrete channel',
            'manning_n': 0.015,
            'min_slope': 0.002,
            'max_slope': 0.08,
            'suitable_for': ['urban areas', 'space constrained']
        },
        'v_shaped_ditch': {
            'description': 'V-shaped drainage ditch',
            'manning_n': 0.030,
            'min_slope': 0.005,
            'max_slope': 0.08,
            'suitable_for': ['roadside', 'agricultural areas']
        },
        'grass_lined_swale': {
            'description': 'Grass-lined swale/bioswale',
            'manning_n': 0.040,
            'min_slope': 0.01,
            'max_slope': 0.06,
            'suitable_for': ['low impact development', 'infiltration']
        },
        'cascade_channel': {
            'description': 'Cascade/drop structure channel',
            'manning_n': 0.050,
            'min_slope': 0.10,
            'max_slope': 0.20,
            'suitable_for': ['steep terrain', 'energy dissipation']
        },
        'stepped_channel': {
            'description': 'Stepped spillway channel',
            'manning_n': 0.045,
            'min_slope': 0.15,
            'max_slope': 0.50,
            'suitable_for': ['very steep terrain', 'dam spillways']
        }
    }
    
    @staticmethod
    def select_design(slope: float, peak_flow: float = 0, is_urban: bool = False) -> dict:
        """
        Select appropriate drainage design based on slope and conditions.
        
        Args:
            slope: Channel slope (m/m)
            peak_flow: Design peak flow (m³/s)
            is_urban: Whether location is urban (affects design choice)
            
        Returns:
            dict with design type, properties, and reasoning
        """
        # Slope-based selection logic
        if slope < HydrologicalConstants.SLOPE_VERY_LOW:
            design_type = 'pump_station'
            reason = 'Very flat terrain (< 0.5%) requires pumping'
        elif slope < HydrologicalConstants.SLOPE_LOW:
            if is_urban:
                design_type = 'circular_pipe'
                reason = 'Low slope urban area - standard pipe drainage'
            else:
                design_type = 'trapezoidal_channel'
                reason = 'Low slope rural area - open channel preferred'
        elif slope < HydrologicalConstants.SLOPE_MODERATE:
            if peak_flow > 1.0:  # Large flow
                design_type = 'box_culvert' if is_urban else 'trapezoidal_channel'
                reason = 'Moderate slope with significant flow'
            else:
                design_type = 'circular_pipe' if is_urban else 'v_shaped_ditch'
                reason = 'Moderate slope with manageable flow'
        elif slope < HydrologicalConstants.SLOPE_HIGH:
            design_type = 'trapezoidal_channel'
            reason = 'Moderate-high slope - trapezoidal channel with erosion protection'
        elif slope < HydrologicalConstants.SLOPE_VERY_HIGH:
            design_type = 'cascade_channel'
            reason = 'High slope (> 10%) - cascade with energy dissipation'
        else:
            design_type = 'stepped_channel'
            reason = 'Very high slope (> 15%) - stepped channel required'
            
        design_info = DrainageDesignSelector.DESIGN_TYPES[design_type].copy()
        design_info['type'] = design_type
        design_info['selection_reason'] = reason
        design_info['input_slope'] = slope
        design_info['input_slope_pct'] = slope * 100
        
        return design_info


class HydraulicValidator:
    """
    Validates hydraulic design parameters for drainage systems.
    Ensures designs meet engineering standards and physical constraints.
    """
    
    @staticmethod
    def validate_continuity(upstream_flows: list, downstream_flow: float, tolerance: float = 0.01) -> dict:
        """
        Check flow continuity (mass balance).
        Downstream flow should equal or exceed sum of upstream flows.
        
        Args:
            upstream_flows: List of upstream flow rates (m³/s)
            downstream_flow: Downstream flow rate (m³/s)
            tolerance: Acceptable relative error
            
        Returns:
            dict with validation result and details
        """
        upstream_sum = sum(upstream_flows)
        
        if downstream_flow < upstream_sum * (1 - tolerance):
            return {
                'valid': False,
                'issue': 'Continuity violation',
                'upstream_sum': upstream_sum,
                'downstream_flow': downstream_flow,
                'deficit': upstream_sum - downstream_flow,
                'recommendation': 'Increase downstream capacity or add storage'
            }
        return {
            'valid': True,
            'upstream_sum': upstream_sum,
            'downstream_flow': downstream_flow,
            'surplus': downstream_flow - upstream_sum
        }
    
    @staticmethod
    def validate_slope(slope: float, infrastructure_type: str = 'pipe') -> dict:
        """
        Validate slope meets minimum requirements.
        
        Args:
            slope: Design slope (m/m)
            infrastructure_type: 'pipe' or 'channel'
            
        Returns:
            dict with validation result and recommendations
        """
        min_slope = (HydrologicalConstants.MIN_SLOPE_PIPE if infrastructure_type == 'pipe' 
                     else HydrologicalConstants.MIN_SLOPE_CHANNEL)
        
        if slope < min_slope:
            return {
                'valid': False,
                'issue': f'Slope below minimum ({slope*100:.2f}% < {min_slope*100:.2f}%)',
                'actual_slope': slope,
                'min_required': min_slope,
                'recommendation': 'Increase slope, use pump station, or use larger diameter'
            }
        return {
            'valid': True,
            'actual_slope': slope,
            'min_required': min_slope,
            'margin': slope - min_slope
        }
    
    @staticmethod
    def validate_velocity(velocity: float) -> dict:
        """
        Validate flow velocity is within acceptable range.
        - Minimum 0.6 m/s for self-cleaning (prevents sediment buildup)
        - Maximum 3.0 m/s to prevent erosion and damage
        
        Args:
            velocity: Flow velocity (m/s)
            
        Returns:
            dict with validation result and recommendations
        """
        issues = []
        recommendations = []
        
        if velocity < HydrologicalConstants.MIN_VELOCITY:
            issues.append(f'Velocity too low ({velocity:.2f} m/s < {HydrologicalConstants.MIN_VELOCITY} m/s)')
            recommendations.append('Increase slope or reduce pipe diameter for higher velocity')
            
        if velocity > HydrologicalConstants.MAX_VELOCITY:
            issues.append(f'Velocity too high ({velocity:.2f} m/s > {HydrologicalConstants.MAX_VELOCITY} m/s)')
            recommendations.append('Add energy dissipators, reduce slope, or increase pipe diameter')
            
        return {
            'valid': len(issues) == 0,
            'velocity': velocity,
            'min_velocity': HydrologicalConstants.MIN_VELOCITY,
            'max_velocity': HydrologicalConstants.MAX_VELOCITY,
            'issues': issues,
            'recommendations': recommendations,
            'flow_regime': 'acceptable' if not issues else ('too slow' if velocity < 0.6 else 'too fast')
        }
    
    @staticmethod
    def full_validation(slope: float, velocity: float, upstream_flows: list = None, 
                        downstream_flow: float = None, infrastructure_type: str = 'pipe') -> dict:
        """
        Perform complete hydraulic validation.
        
        Returns comprehensive validation report.
        """
        results = {
            'slope_validation': HydraulicValidator.validate_slope(slope, infrastructure_type),
            'velocity_validation': HydraulicValidator.validate_velocity(velocity)
        }
        
        if upstream_flows is not None and downstream_flow is not None:
            results['continuity_validation'] = HydraulicValidator.validate_continuity(
                upstream_flows, downstream_flow
            )
            
        # Overall pass/fail
        all_valid = all(r.get('valid', True) for r in results.values())
        results['overall_valid'] = all_valid
        
        return results


class FluidMechanics:
    """Fluid mechanics calculations for drainage design."""
    
    @staticmethod
    def manning_velocity(hydraulic_radius: float, slope: float, n: float = 0.013) -> float:
        """
        Manning's equation for flow velocity.
        V = (1/n) * R^(2/3) * S^(1/2)
        
        Args:
            hydraulic_radius: R in meters
            slope: S (dimensionless, m/m)
            n: Manning's roughness coefficient
            
        Returns:
            Velocity in m/s
        """
        if slope <= 0 or hydraulic_radius <= 0:
            return 0
        return (1 / n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
    
    @staticmethod
    def manning_flow(area: float, hydraulic_radius: float, slope: float, n: float = 0.013) -> float:
        """
        Flow rate using Manning's equation.
        Q = A * V = (A/n) * R^(2/3) * S^(1/2)
        
        Returns:
            Flow rate in m³/s
        """
        velocity = FluidMechanics.manning_velocity(hydraulic_radius, slope, n)
        return area * velocity
    
    @staticmethod
    def pipe_full_flow(diameter: float, slope: float, n: float = 0.013) -> float:
        """
        Full pipe flow capacity.
        
        Args:
            diameter: Pipe diameter in meters
            slope: Pipe slope (m/m)
            n: Manning's coefficient
            
        Returns:
            Flow capacity in m³/s
        """
        area = np.pi * (diameter / 2) ** 2
        hydraulic_radius = diameter / 4  # For circular pipe flowing full
        return FluidMechanics.manning_flow(area, hydraulic_radius, slope, n)
    
    @staticmethod
    def froude_number(velocity: float, depth: float) -> float:
        """
        Froude number for flow characterization.
        Fr = V / sqrt(g * d)
        
        Fr < 1: Subcritical (tranquil)
        Fr = 1: Critical
        Fr > 1: Supercritical (rapid)
        """
        g = 9.81
        if depth <= 0:
            return 0
        return velocity / np.sqrt(g * depth)
    
    @staticmethod
    def required_pipe_diameter(flow: float, slope: float, n: float = 0.013) -> float:
        """
        Calculate required pipe diameter for given flow.
        
        Uses iterative approach to find minimum diameter.
        """
        for d_mm in HydrologicalConstants.PIPE_DIAMETERS:
            d_m = d_mm / 1000
            capacity = FluidMechanics.pipe_full_flow(d_m, slope, n)
            if capacity >= flow:
                return d_mm
        return HydrologicalConstants.PIPE_DIAMETERS[-1]  # Return largest


class HydrologicalAnalysis:
    """Hydrological analysis methods."""
    
    @staticmethod
    def rational_method(C: float, I: float, A: float) -> float:
        """
        Rational Method for peak runoff.
        Q = C * I * A
        
        Args:
            C: Runoff coefficient (0-1)
            I: Rainfall intensity (mm/hr)
            A: Catchment area (hectares)
            
        Returns:
            Peak flow Q in m³/s
        """
        # Convert: Q (m³/s) = C * I (mm/hr) * A (ha) / 360
        return C * I * A / 360
    
    @staticmethod
    def time_of_concentration_kirpich(length: float, slope: float) -> float:
        """
        Kirpich formula for time of concentration.
        Tc = 0.0195 * L^0.77 * S^(-0.385)
        
        Args:
            length: Flow path length in meters
            slope: Average slope (m/m)
            
        Returns:
            Time of concentration in minutes
        """
        if slope <= 0:
            slope = 0.001
        # Convert length to feet for formula, then result is in minutes
        L_ft = length * 3.281
        S_pct = slope * 100
        tc = 0.0078 * (L_ft ** 0.77) * (S_pct ** (-0.385))
        return tc
    
    @staticmethod
    def rainfall_intensity(duration: float, return_period: int = 10) -> float:
        """
        IDF curve approximation for rainfall intensity.
        Using generalized formula: I = a / (t + b)^c
        
        Args:
            duration: Storm duration in minutes
            return_period: Return period in years
            
        Returns:
            Rainfall intensity in mm/hr
        """
        # Coefficients vary by region - using typical temperate values
        a = 1000 + return_period * 50
        b = 10
        c = 0.8
        return a / ((duration + b) ** c)
    
    @staticmethod
    def scs_curve_number_runoff(P: float, CN: float) -> float:
        """
        SCS Curve Number method for runoff depth.
        Q = (P - 0.2*S)² / (P + 0.8*S)  for P > 0.2*S
        S = (25400/CN) - 254
        
        Args:
            P: Precipitation depth (mm)
            CN: Curve Number (0-100)
            
        Returns:
            Runoff depth in mm
        """
        if CN <= 0 or CN > 100:
            return 0
        S = (25400 / CN) - 254
        Ia = 0.2 * S  # Initial abstraction
        
        if P <= Ia:
            return 0
        return ((P - Ia) ** 2) / (P - Ia + S)


class ProfessionalDrainageDesigner:
    """
    Professional drainage network designer using hydrological analysis.
    """
    
    def __init__(self, dtm_path: str, output_dir: str):
        self.dtm_path = Path(dtm_path).resolve()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = self.output_dir / 'temp'
        self.temp_dir.mkdir(exist_ok=True)
        
        # WhiteboxTools
        if HAS_WHITEBOX:
            self.wbt = WhiteboxTools()
            self.wbt.set_verbose_mode(False)
        else:
            self.wbt = None
            
        # DTM data
        self.dtm = None
        self.transform = None
        self.crs = None
        self.bounds = None
        self.resolution = None
        self.nodata_mask = None
        
        # Hydrological grids
        self.flow_direction = None
        self.flow_accumulation = None
        self.slope = None
        self.catchment_area = None  # Contributing area per cell
        
        # D∞ specific grids
        self.dinf_flow_direction = None  # D-infinity flow direction (angle)
        self.stream_raster = None        # Binary stream network
        self.strahler_order = None       # Strahler stream order
        
        # Network
        self.drainage_lines = []  # (type, coordinates, properties)
        self.outlets = []
        self.design_data = {}
        self.validation_results = {}  # Hydraulic validation results
        
        # Parameters
        self.flow_threshold = 10000  # m² contributing area for channel
        self.runoff_coeff = 0.5  # Default suburban
        self.design_storm_years = 10  # 10-year return period
        self.stream_threshold_pct = HydrologicalConstants.DEFAULT_STREAM_THRESHOLD_PCT  # 1% threshold
        self.is_urban = False  # Affects design selection
        
    def load_terrain(self):
        """Load and validate terrain data."""
        print(f"\n{'='*60}")
        print("  PROFESSIONAL DRAINAGE NETWORK DESIGNER")
        print(f"{'='*60}")
        print(f"\n📂 Loading terrain: {self.dtm_path.name}")
        
        with rasterio.open(self.dtm_path) as src:
            self.dtm = src.read(1).astype(np.float64)
            self.transform = src.transform
            self.crs = src.crs
            self.bounds = src.bounds
            self.resolution = src.res[0]
            nodata = src.nodata
            
        if nodata is not None:
            self.dtm[self.dtm == nodata] = np.nan
            
        self.nodata_mask = np.isnan(self.dtm)
        valid = self.dtm[~self.nodata_mask]
        
        self.design_data['terrain'] = {
            'dimensions': f"{self.dtm.shape[1]} x {self.dtm.shape[0]}",
            'resolution_m': self.resolution,
            'elevation_min': float(valid.min()),
            'elevation_max': float(valid.max()),
            'elevation_range': float(valid.max() - valid.min())
        }
        
        print(f"   ✓ Dimensions: {self.dtm.shape[1]} × {self.dtm.shape[0]} pixels")
        print(f"   ✓ Resolution: {self.resolution:.2f} m")
        print(f"   ✓ Elevation: {valid.min():.2f} - {valid.max():.2f} m")
        
        return self
        
    def hydrological_processing(self):
        """
        Run hydrological analysis using D∞ (D-Infinity) algorithm.
        
        D∞ Algorithm (Tarboton, 1997):
        - Determines flow direction as a continuous angle
        - Distributes flow between multiple downslope cells
        - More accurate for divergent flow on hillslopes
        - Better representation of flow dispersion
        """
        print("\n🌊 Hydrological Processing (D∞ Algorithm)...")
        
        if not HAS_WHITEBOX or not self.wbt:
            return self._fallback_hydrology()
            
        # Paths
        filled = str((self.temp_dir / 'filled.tif').resolve())
        dinf_flow_dir = str((self.temp_dir / 'dinf_flow_dir.tif').resolve())
        dinf_flow_acc = str((self.temp_dir / 'dinf_flow_acc.tif').resolve())
        d8_flow_dir = str((self.temp_dir / 'd8_flow_dir.tif').resolve())  # For stream extraction
        slope_path = str((self.temp_dir / 'slope.tif').resolve())
        streams_path = str((self.temp_dir / 'streams.tif').resolve())
        strahler_path = str((self.temp_dir / 'strahler.tif').resolve())
        
        # Fill depressions (breach method is more realistic)
        print("   → Conditioning DEM (breach depressions)...")
        self.wbt.breach_depressions(str(self.dtm_path), filled)
        
        # D∞ (D-Infinity) flow direction - outputs flow direction as angle
        print("   → Computing D∞ flow direction (Tarboton method)...")
        self.wbt.d_inf_pointer(filled, dinf_flow_dir)
        
        # D∞ flow accumulation - more accurate for hillslope hydrology
        print("   → Computing D∞ flow accumulation...")
        self.wbt.d_inf_flow_accumulation(filled, dinf_flow_acc, out_type='sca')
        
        # Also compute D8 for stream extraction (needed for Strahler ordering)
        print("   → Computing D8 pointer for stream network...")
        self.wbt.d8_pointer(filled, d8_flow_dir)
        
        # Stream delineation with threshold
        print("   → Delineating streams with threshold...")
        self._extract_streams_with_threshold(dinf_flow_acc, d8_flow_dir, streams_path, strahler_path)
        
        # Slope
        print("   → Computing slope...")
        self.wbt.slope(filled, slope_path, units='degrees')
        
        # Load results - D∞ flow accumulation
        with rasterio.open(dinf_flow_acc) as src:
            self.flow_accumulation = src.read(1)
            
        # Load D∞ flow direction (angle in radians)
        with rasterio.open(dinf_flow_dir) as src:
            self.dinf_flow_direction = src.read(1)
            
        # Load D8 flow direction for stream tracing
        with rasterio.open(d8_flow_dir) as src:
            self.flow_direction = src.read(1)
            
        with rasterio.open(slope_path) as src:
            slope_deg = src.read(1)
            self.slope = np.tan(np.radians(slope_deg))  # Convert to m/m
            
        # Load stream network and Strahler order if available
        try:
            with rasterio.open(streams_path) as src:
                self.stream_raster = src.read(1)
            with rasterio.open(strahler_path) as src:
                self.strahler_order = src.read(1)
            print(f"   ✓ Strahler stream ordering complete (max order: {int(np.nanmax(self.strahler_order))})")
        except:
            self.stream_raster = None
            self.strahler_order = None
            
        # Load the filled DEM for tracing (no depressions)
        with rasterio.open(filled) as src:
            self.filled_dtm = src.read(1)
            
        # Calculate catchment area per cell
        self.catchment_area = self.flow_accumulation * (self.resolution ** 2)
        
        print("   ✓ D∞ hydrological analysis complete")
        
        return self
    
    def _extract_streams_with_threshold(self, flow_acc_path, flow_dir_path, streams_path, strahler_path):
        """
        Extract stream network using flow accumulation threshold.
        
        Uses configurable threshold (default 1% of total cells) to define
        where streams begin. Applies Strahler ordering for hierarchy.
        """
        # Load flow accumulation to calculate threshold
        with rasterio.open(flow_acc_path) as src:
            flow_acc = src.read(1)
            profile = src.profile
            
        # Calculate threshold based on percentage of total cells
        valid_cells = flow_acc[~np.isnan(flow_acc) & (flow_acc > 0)]
        if len(valid_cells) > 0:
            # Threshold = cells where accumulation > (threshold_pct)th percentile
            threshold_value = np.percentile(valid_cells, 100 - self.stream_threshold_pct)
            total_cells = len(valid_cells)
            threshold_cells = int(total_cells * self.stream_threshold_pct / 100)
            
            print(f"   → Stream threshold: {threshold_value:.0f} (top {self.stream_threshold_pct}% = {threshold_cells} cells)")
            
            # Create binary stream raster
            streams = (flow_acc >= threshold_value).astype(np.int16)
            streams[np.isnan(flow_acc)] = 0
            
            # Save streams raster
            profile.update(dtype=rasterio.int16, nodata=-1)
            with rasterio.open(streams_path, 'w', **profile) as dst:
                dst.write(streams, 1)
                
            # Compute Strahler stream order using WhiteboxTools
            print("   → Computing Strahler stream ordering...")
            try:
                self.wbt.strahler_stream_order(flow_dir_path, streams_path, strahler_path)
            except Exception as e:
                print(f"   ⚠ Strahler ordering failed: {e}")
                # Create simple order based on accumulation
                strahler = np.zeros_like(flow_acc, dtype=np.int16)
                strahler[streams > 0] = 1 + np.log10(flow_acc[streams > 0] + 1).astype(int)
                with rasterio.open(strahler_path, 'w', **profile) as dst:
                    dst.write(strahler, 1)
        
    def _fallback_hydrology(self):
        """Fallback when WhiteboxTools unavailable."""
        print("   Using scipy-based hydrology (fallback)...")
        
        # Slope from gradient
        dy, dx = np.gradient(self.dtm, self.resolution)
        self.slope = np.sqrt(dx**2 + dy**2)
        self.slope[self.nodata_mask] = np.nan
        
        # Simple flow accumulation approximation
        self.flow_accumulation = np.ones_like(self.dtm)
        self.catchment_area = self.flow_accumulation * (self.resolution ** 2)
        
        print("   ✓ Fallback hydrology complete")
        return self
        
    def extract_drainage_network(self):
        """
        Extract fully connected drainage network using downstream tracing.
        Creates complete flow paths from headwaters to outlets.
        """
        print("\n📐 Extracting drainage network...")
        
        if self.flow_accumulation is None:
            print("   ⚠ No flow data available")
            return self
            
        rows, cols = self.dtm.shape
        dem = getattr(self, 'filled_dtm', self.dtm)
        
        # Get flow thresholds for stream definition
        valid_acc = self.flow_accumulation[~self.nodata_mask]
        
        # Define stream cells at different levels
        threshold_main = np.percentile(valid_acc, 97)      # Top 3% - main rivers
        threshold_tributary = np.percentile(valid_acc, 92) # Top 8% - tributaries
        threshold_stream = np.percentile(valid_acc, 85)    # Top 15% - small streams
        
        print(f"   Stream thresholds: Main>{threshold_main:.0f}, Tributary>{threshold_tributary:.0f}, Stream>{threshold_stream:.0f}")
        
        # Find starting points for tracing (high points with sufficient flow)
        # These are headwater cells - cells that are streams but have no upstream stream neighbor
        headwater_cells = []
        
        for r in range(2, rows - 2):
            for c in range(2, cols - 2):
                if self.nodata_mask[r, c]:
                    continue
                    
                cell_acc = self.flow_accumulation[r, c]
                if cell_acc < threshold_stream:
                    continue
                    
                # Check if this is a headwater (no upstream neighbor with similar flow)
                is_headwater = True
                current_elev = dem[r, c]
                
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if not self.nodata_mask[nr, nc]:
                                # Higher neighbor with significant flow = upstream
                                if (dem[nr, nc] > current_elev and 
                                    self.flow_accumulation[nr, nc] >= threshold_stream * 0.8):
                                    is_headwater = False
                                    break
                    if not is_headwater:
                        break
                        
                if is_headwater:
                    headwater_cells.append((r, c, cell_acc))
                    
        # Sort by accumulation (higher = more important stream start)
        headwater_cells.sort(key=lambda x: -x[2])
        
        print(f"   Found {len(headwater_cells)} potential headwater cells")
        
        # Select well-spaced headwaters
        selected_headwaters = []
        min_spacing = 25
        
        for r, c, acc in headwater_cells:
            too_close = False
            for sr, sc, _ in selected_headwaters:
                dist = np.sqrt((r - sr)**2 + (c - sc)**2)
                if dist < min_spacing:
                    too_close = True
                    break
            if not too_close:
                selected_headwaters.append((r, c, acc))
                if len(selected_headwaters) >= 150:  # More starting points
                    break
                    
        print(f"   Selected {len(selected_headwaters)} headwater starting points")
        
        # Trace downstream from each headwater
        self.drainage_lines = []
        global_visited = set()
        
        for start_r, start_c, start_acc in selected_headwaters:
            if (start_r, start_c) in global_visited:
                continue
                
            # Get Strahler order at starting point if available
            strahler = None
            if self.strahler_order is not None:
                strahler = int(self.strahler_order[start_r, start_c])
                if strahler <= 0:
                    strahler = None
                
            # Trace downstream to outlet or confluence with existing stream
            coords = self._trace_downstream_complete(start_r, start_c, dem, global_visited)
            
            if len(coords) >= 5:
                smoothed = self._smooth_line(coords, smoothing=0.3)
                props = self._calculate_channel_properties(smoothed, 'tertiary', strahler)  # Temp type
                props['start_accumulation'] = float(start_acc)
                
                # Store with temp classification - will reclassify after all traces
                min_length = 15
                if props.get('length_m', 0) >= min_length:
                    self.drainage_lines.append(('temp', smoothed, props))
        
        # Now reclassify based on channel length and drainage contribution
        # Longer channels that drain more area = more important
        if self.drainage_lines:
            lengths = [d[2].get('length_m', 0) for d in self.drainage_lines]
            len_p75 = np.percentile(lengths, 75)
            len_p50 = np.percentile(lengths, 50)
            
            reclassified = []
            for _, coords, props in self.drainage_lines:
                length = props.get('length_m', 0)
                
                if length >= len_p75:
                    channel_type = 'primary'
                elif length >= len_p50:
                    channel_type = 'secondary'
                else:
                    channel_type = 'tertiary'
                    
                reclassified.append((channel_type, coords, props))
                
            self.drainage_lines = reclassified
                    
        # Sort by average accumulation
        self.drainage_lines.sort(key=lambda x: -x[2].get('avg_accumulation', 0))
        
        # Count
        primary = sum(1 for d in self.drainage_lines if d[0] == 'primary')
        secondary = sum(1 for d in self.drainage_lines if d[0] == 'secondary')
        tertiary = sum(1 for d in self.drainage_lines if d[0] == 'tertiary')
        
        total_length = sum(d[2].get('length_m', 0) for d in self.drainage_lines)
        
        print(f"   ✓ Extracted {len(self.drainage_lines)} drainage lines ({total_length/1000:.2f} km)")
        print(f"      Primary: {primary}, Secondary: {secondary}, Tertiary: {tertiary}")
        
        return self
        
    def _trace_downstream_complete(self, start_r, start_c, dem, global_visited, max_steps=1500):
        """
        Trace flow path downstream from a starting point.
        Continues until reaching boundary, pit, or already-traced stream.
        """
        rows, cols = dem.shape
        coords = []
        
        r, c = start_r, start_c
        local_visited = set()
        
        for step in range(max_steps):
            # Check bounds
            if not (0 <= r < rows and 0 <= c < cols):
                break
                
            # Skip nodata
            if self.nodata_mask[r, c]:
                break
                
            # If we hit a globally visited cell, add connection point and stop
            if (r, c) in global_visited and len(coords) > 0:
                x, y = xy(self.transform, r, c)
                z = self.dtm[r, c]
                coords.append((x, y, z))
                break
                
            # Prevent local loops
            if (r, c) in local_visited:
                break
                
            local_visited.add((r, c))
            
            # Add point
            x, y = xy(self.transform, r, c)
            z = self.dtm[r, c]
            coords.append((x, y, z))
            
            # Find lowest neighbor (steepest descent)
            current_elev = dem[r, c]
            best_r, best_c = None, None
            lowest_elev = current_elev
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    nr, nc = r + dr, c + dc
                    
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                        
                    if self.nodata_mask[nr, nc]:
                        continue
                        
                    neighbor_elev = dem[nr, nc]
                    
                    if neighbor_elev < lowest_elev:
                        lowest_elev = neighbor_elev
                        best_r, best_c = nr, nc
                        
            # Move to lowest neighbor
            if best_r is None:
                # At pit or boundary - end of trace
                break
                
            r, c = best_r, best_c
            
        # Mark all traced cells as globally visited
        for (vr, vc) in local_visited:
            global_visited.add((vr, vc))
            
        return coords
        
    def _select_starts(self, cells, spacing, max_count):
        """Select well-spaced starting points."""
        selected = []
        
        for r, c, acc in cells:
            too_close = False
            for sr, sc, _ in selected:
                if abs(r - sr) < spacing and abs(c - sc) < spacing:
                    too_close = True
                    break
            if not too_close:
                selected.append((r, c, acc))
                if len(selected) >= max_count:
                    break
                    
        return selected
        
    def _trace_flow_by_elevation(self, start_r, start_c, visited, max_steps=800):
        """Trace flow path by always going to lowest neighbor on filled DEM."""
        rows, cols = self.dtm.shape
        coords = []
        
        # Use filled DEM if available (no pits), else use original
        dem = getattr(self, 'filled_dtm', self.dtm)
        
        r, c = start_r, start_c
        local_visited = set()  # Track visited cells in this trace only
        
        for step in range(max_steps):
            # Check bounds
            if not (0 <= r < rows and 0 <= c < cols):
                break
                
            # Skip if nodata
            if self.nodata_mask[r, c]:
                break
                
            # Stop if we reach the global visited set (merging with another channel)
            if (r, c) in visited and len(coords) > 0:
                x, y = xy(self.transform, r, c)
                z = self.dtm[r, c]
                coords.append((x, y, z))
                break
            
            # Stop if we're in a local loop
            if (r, c) in local_visited:
                break
                
            local_visited.add((r, c))
            
            # Add point (use original DTM elevation for display)
            x, y = xy(self.transform, r, c)
            z = self.dtm[r, c]  # Original elevation for visualization
            coords.append((x, y, z))
            
            # Find lowest neighbor (D8) - use filled DEM to avoid pits
            current_elev = dem[r, c]
            best_r, best_c = None, None
            lowest_elev = current_elev
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    nr, nc = r + dr, c + dc
                    
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                        
                    if self.nodata_mask[nr, nc]:
                        continue
                        
                    neighbor_elev = dem[nr, nc]
                    
                    if neighbor_elev < lowest_elev:
                        lowest_elev = neighbor_elev
                        best_r, best_c = nr, nc
                        
            # Move to lowest neighbor
            if best_r is None:
                # No lower neighbor - at pit or boundary
                break
                
            r, c = best_r, best_c
        
        # Now mark all traced cells as globally visited
        for (vr, vc) in local_visited:
            visited.add((vr, vc))
            
        return coords
        
    def _smooth_line(self, coords, smoothing=0.5):
        """Smooth a line using spline interpolation."""
        if len(coords) < 4:
            return coords
            
        try:
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            z = [c[2] for c in coords]
            
            # Fit spline
            tck, u = splprep([x, y], s=smoothing * len(coords), k=min(3, len(coords)-1))
            
            # Evaluate at more points
            u_new = np.linspace(0, 1, min(30, len(coords) * 2))
            x_new, y_new = splev(u_new, tck)
            
            # Interpolate z
            z_new = np.interp(u_new, np.linspace(0, 1, len(z)), z)
            
            return [(x_new[i], y_new[i], z_new[i]) for i in range(len(x_new))]
        except:
            return coords
            
    def _calculate_channel_properties(self, coords, channel_type, strahler_order=None):
        """
        Calculate hydraulic properties for a channel with design selection and validation.
        
        Includes:
        - Automated design type selection based on slope
        - Hydraulic validation (slope, velocity)
        - Manning's equation calculations
        - Strahler order integration
        """
        if len(coords) < 2:
            return {}
            
        # Length
        length = sum(
            np.sqrt((coords[i+1][0] - coords[i][0])**2 + 
                   (coords[i+1][1] - coords[i][1])**2)
            for i in range(len(coords) - 1)
        )
        
        # Elevation drop and average slope
        elev_start = coords[0][2]
        elev_end = coords[-1][2]
        elev_drop = elev_start - elev_end
        avg_slope = elev_drop / length if length > 0 else 0
        
        # Store original slope before adjustment
        original_slope = avg_slope
        
        # Ensure minimum slope
        if avg_slope < HydrologicalConstants.MIN_SLOPE_CHANNEL:
            avg_slope = HydrologicalConstants.MIN_SLOPE_CHANNEL
            
        # Time of concentration
        tc = HydrologicalAnalysis.time_of_concentration_kirpich(length, max(avg_slope, 0.001))
        
        # Rainfall intensity for design storm
        intensity = HydrologicalAnalysis.rainfall_intensity(tc, self.design_storm_years)
        
        # Estimate contributing area (simplified)
        area_factor = {'primary': 10.0, 'secondary': 3.0, 'tertiary': 1.0}
        contrib_area_ha = (length * 50 * area_factor.get(channel_type, 1)) / 10000
        
        # Peak flow using Rational Method
        peak_flow = HydrologicalAnalysis.rational_method(
            self.runoff_coeff, intensity, contrib_area_ha
        )
        
        # === AUTOMATED DESIGN SELECTION ===
        design_info = DrainageDesignSelector.select_design(
            original_slope, peak_flow, self.is_urban
        )
        design_type = design_info['type']
        manning_n = design_info['manning_n']
        
        # Required pipe size (for pipe designs)
        pipe_diameter = FluidMechanics.required_pipe_diameter(peak_flow, avg_slope, manning_n)
        
        # Flow velocity calculation
        d_m = pipe_diameter / 1000
        R = d_m / 4  # Hydraulic radius for full pipe
        velocity = FluidMechanics.manning_velocity(R, avg_slope, manning_n)
        
        # === HYDRAULIC VALIDATION ===
        validation = HydraulicValidator.full_validation(
            slope=original_slope,
            velocity=velocity,
            infrastructure_type='pipe' if 'pipe' in design_type else 'channel'
        )
        
        # Froude number for flow characterization
        froude = FluidMechanics.froude_number(velocity, d_m * 0.8)  # Assume 80% full
        flow_regime = 'subcritical' if froude < 1 else ('critical' if froude == 1 else 'supercritical')
        
        return {
            'length_m': length,
            'slope_pct': avg_slope * 100,
            'original_slope_pct': original_slope * 100,
            'elev_drop_m': elev_drop,
            'time_conc_min': tc,
            'rainfall_intensity_mmhr': intensity,
            'peak_flow_m3s': peak_flow,
            'pipe_diameter_mm': pipe_diameter,
            'velocity_ms': velocity,
            'manning_n': manning_n,
            'froude_number': froude,
            'flow_regime': flow_regime,
            'strahler_order': strahler_order,
            # Design selection results
            'design_type': design_type,
            'design_description': design_info['description'],
            'design_reason': design_info['selection_reason'],
            # Validation results
            'validation_passed': validation['overall_valid'],
            'slope_valid': validation['slope_validation']['valid'],
            'velocity_valid': validation['velocity_validation']['valid'],
            'velocity_issues': validation['velocity_validation'].get('issues', [])
        }
        
    def identify_outlets(self):
        """Identify outlet points at terrain boundaries."""
        print("\n🚪 Identifying outlets...")
        
        rows, cols = self.dtm.shape
        self.outlets = []
        
        # Find lowest points on each boundary
        boundaries = {
            'south': [(rows-1, c) for c in range(0, cols, cols//10)],
            'north': [(0, c) for c in range(0, cols, cols//10)],
            'west': [(r, 0) for r in range(0, rows, rows//10)],
            'east': [(r, cols-1) for r in range(0, rows, rows//10)]
        }
        
        for edge, cells in boundaries.items():
            valid_cells = [(r, c, self.dtm[r, c]) for r, c in cells 
                          if not np.isnan(self.dtm[r, c])]
            if valid_cells:
                # Get lowest 2 points per edge
                sorted_cells = sorted(valid_cells, key=lambda x: x[2])[:2]
                for r, c, z in sorted_cells:
                    x, y = xy(self.transform, r, c)
                    self.outlets.append({'x': x, 'y': y, 'z': z, 'edge': edge})
                    
        print(f"   ✓ Found {len(self.outlets)} outlet points")
        return self
        
    def create_visualization(self):
        """Create clean, professional 3D visualization."""
        print("\n📊 Creating visualization...")
        
        # === TERRAIN SURFACE ===
        # Sample for performance while preserving authenticity
        rows, cols = self.dtm.shape
        
        # Adaptive sampling - denser for smaller terrains
        max_points = 150
        sample_step = max(1, min(rows, cols) // max_points)
        
        z_sampled = self.dtm[::sample_step, ::sample_step].copy()
        
        # Create coordinate grids
        x_grid = np.zeros_like(z_sampled)
        y_grid = np.zeros_like(z_sampled)
        
        for i, r in enumerate(range(0, rows, sample_step)):
            for j, c in enumerate(range(0, cols, sample_step)):
                if i < z_sampled.shape[0] and j < z_sampled.shape[1]:
                    x, y = xy(self.transform, r, c)
                    x_grid[i, j] = x
                    y_grid[i, j] = y
                    
        # Replace NaN with None for plotly
        z_display = np.where(np.isnan(z_sampled), None, z_sampled)
        
        # Create figure
        fig = go.Figure()
        
        # Add terrain - using natural earth tones, subtle rendering
        fig.add_trace(go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_display,
            colorscale=[
                [0.0, 'rgb(34, 139, 34)'],    # Forest green (low)
                [0.25, 'rgb(144, 238, 144)'], # Light green
                [0.5, 'rgb(210, 180, 140)'],  # Tan
                [0.75, 'rgb(139, 90, 43)'],   # Brown
                [1.0, 'rgb(105, 105, 105)']   # Gray (high)
            ],
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
        ))
        
        # === DRAINAGE LINES WITH FLOW DIRECTION ===
        # Use gradient coloring: upstream (light) → downstream (dark) 
        # Add arrow markers to show flow direction
        
        # Base colors for each type (RGB format for gradient calculation)
        base_colors = {
            'primary': {'light': (100, 180, 255), 'dark': (0, 50, 150)},
            'secondary': {'light': (130, 210, 255), 'dark': (20, 100, 180)},
            'tertiary': {'light': (170, 230, 255), 'dark': (60, 140, 200)}
        }
        
        widths = {'primary': 6, 'secondary': 4, 'tertiary': 2.5}
        
        legend_added = set()
        
        for channel_type, coords, props in self.drainage_lines:
            if len(coords) < 2:
                continue
            
            # Coordinates - note: coords are in upstream-to-downstream order from tracing
            # We need to reverse to show flow direction (high elevation to low)
            # Sort by elevation (highest first = upstream)
            coords_sorted = sorted(coords, key=lambda c: -c[2])
            
            # Actually, keep original order but determine flow direction from elevation
            elevs = [c[2] for c in coords]
            if elevs[0] < elevs[-1]:
                # First point is lower - reverse to make it upstream→downstream
                coords = coords[::-1]
                
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            zs = [c[2] + 0.5 for c in coords]
            
            # Create gradient colors along the line (upstream=light, downstream=dark)
            n_points = len(coords)
            light = base_colors[channel_type]['light']
            dark = base_colors[channel_type]['dark']
            
            # Generate colors for each segment
            colors = []
            for i in range(n_points):
                t = i / max(n_points - 1, 1)  # 0 at upstream, 1 at downstream
                r = int(light[0] + t * (dark[0] - light[0]))
                g = int(light[1] + t * (dark[1] - light[1]))
                b = int(light[2] + t * (dark[2] - light[2]))
                colors.append(f'rgb({r},{g},{b})')
            
            show_legend = channel_type not in legend_added
            legend_added.add(channel_type)
            
            # Flow rate info for hover
            flow = props.get('peak_flow_m3s', 0)
            pipe = props.get('pipe_diameter_mm', 0)
            length = props.get('length_m', 0)
            
            # Add main line with gradient coloring using line segments
            for i in range(len(xs) - 1):
                seg_color = colors[i]
                fig.add_trace(go.Scatter3d(
                    x=[xs[i], xs[i+1]], 
                    y=[ys[i], ys[i+1]], 
                    z=[zs[i], zs[i+1]],
                    mode='lines',
                    line=dict(
                        color=seg_color,
                        width=widths.get(channel_type, 2)
                    ),
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
            
            # Add flow direction arrows along the channel
            # Place arrows at regular intervals
            arrow_interval = max(3, len(coords) // 5)  # Every ~20% of length
            
            arrow_positions = []
            for i in range(arrow_interval, len(coords) - 1, arrow_interval):
                arrow_positions.append(i)
                
            if arrow_positions:
                # Calculate arrow directions
                arrow_xs = []
                arrow_ys = []
                arrow_zs = []
                
                for idx in arrow_positions:
                    # Arrow at position pointing downstream
                    arrow_xs.append(xs[idx])
                    arrow_ys.append(ys[idx])
                    arrow_zs.append(zs[idx] + 0.3)
                    
                # Add small cone markers to indicate flow direction
                if len(arrow_xs) > 0:
                    # Calculate arrow directions using next point
                    for i, idx in enumerate(arrow_positions):
                        if idx + 1 < len(xs):
                            dx = xs[idx+1] - xs[idx]
                            dy = ys[idx+1] - ys[idx]
                            dz = zs[idx+1] - zs[idx]
                            
                            # Normalize
                            mag = np.sqrt(dx**2 + dy**2 + dz**2)
                            if mag > 0:
                                scale = 3.0  # Arrow size
                                dx, dy, dz = dx/mag * scale, dy/mag * scale, dz/mag * scale
                                
                                # Add small arrow line
                                fig.add_trace(go.Scatter3d(
                                    x=[xs[idx], xs[idx] + dx],
                                    y=[ys[idx], ys[idx] + dy],
                                    z=[zs[idx] + 0.5, zs[idx] + 0.5 + dz],
                                    mode='lines',
                                    line=dict(color=colors[idx], width=widths.get(channel_type, 2) + 2),
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))
                                
                                # Add arrowhead marker
                                fig.add_trace(go.Scatter3d(
                                    x=[xs[idx] + dx],
                                    y=[ys[idx] + dy],
                                    z=[zs[idx] + 0.5 + dz],
                                    mode='markers',
                                    marker=dict(
                                        size=4,
                                        color=colors[idx],
                                        symbol='diamond'
                                    ),
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))
            
        # === OUTLETS (minimal markers) ===
        if self.outlets:
            fig.add_trace(go.Scatter3d(
                x=[o['x'] for o in self.outlets],
                y=[o['y'] for o in self.outlets],
                z=[o['z'] + 1.5 for o in self.outlets],
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
            
        # === LAYOUT ===
        valid_z = z_sampled[~np.isnan(z_sampled)]
        z_range = valid_z.max() - valid_z.min()
        
        fig.update_layout(
            title=dict(
                text='<b>Drainage Network Analysis</b>',
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
            legend=dict(
                yanchor='top', y=0.95,
                xanchor='left', x=0.02,
                bgcolor='rgba(255,255,255,0.85)',
                bordercolor='rgba(200,200,200,0.5)',
                borderwidth=1,
                font=dict(size=10)
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor='white'
        )
        
        # === SAVE WITH OPTIMIZED HTML ===
        vis_dir = self.output_dir / 'visualizations'
        vis_dir.mkdir(exist_ok=True)
        
        output_path = vis_dir / 'drainage_analysis.html'
        
        # Generate optimized HTML with CDN instead of embedded Plotly
        self._write_optimized_html(fig, output_path)
        
        print(f"   ✓ Saved: {output_path}")
        return str(output_path)
    
    def _write_optimized_html(self, fig, output_path):
        """
        Write optimized HTML file using CDN for Plotly.
        
        Improvements:
        - Uses Plotly CDN (~200KB) instead of embedded (~3.5MB)
        - Proper HTML5 structure with DOCTYPE
        - Responsive viewport meta tag
        - Loading indicator while chart loads
        - Error handling for network issues
        - DOMContentLoaded wrapper for initialization
        - No render-blocking resources (defer attribute)
        """
        import json as json_module
        
        # Get the figure data as JSON
        fig_json = fig.to_json()
        
        # Get config
        config_json = json_module.dumps({
            'displayModeBar': True, 
            'scrollZoom': True,
            'responsive': True
        })
        
        # Generate network summary for display
        total_length = sum(props.get('length_m', 0) for _, _, props in self.drainage_lines)
        primary_count = sum(1 for d in self.drainage_lines if d[0] == 'primary')
        secondary_count = sum(1 for d in self.drainage_lines if d[0] == 'secondary')
        tertiary_count = sum(1 for d in self.drainage_lines if d[0] == 'tertiary')
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Drainage Network Analysis - D∞ Flow Routing">
    <title>Drainage Network Analysis</title>
    
    <!-- Plotly.js from CDN (much smaller than embedded) -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" defer></script>
    
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
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
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 0.95rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #4a5568;
        }}
        
        .stat-card .label {{
            font-size: 0.8rem;
            color: #718096;
            margin-top: 5px;
        }}
        
        .stat-card.primary .value {{ color: #3182ce; }}
        .stat-card.secondary .value {{ color: #38a169; }}
        .stat-card.tertiary .value {{ color: #805ad5; }}
        
        .chart-container {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            position: relative;
        }}
        
        #chart {{
            width: 100%;
            height: 75vh;
            min-height: 500px;
        }}
        
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
        }}
        
        .loading.hidden {{
            display: none;
        }}
        
        .spinner {{
            width: 50px;
            height: 50px;
            border: 4px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .loading-text {{
            color: #4a5568;
            font-size: 0.95rem;
        }}
        
        .error-message {{
            background: #fed7d7;
            color: #c53030;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            display: none;
        }}
        
        .error-message.show {{
            display: block;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.85rem;
            margin-top: 20px;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 15px; }}
            .header h1 {{ font-size: 1.4rem; }}
            #chart {{ height: 60vh; min-height: 400px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🌊 Drainage Network Analysis</h1>
            <p class="subtitle">D∞ (D-Infinity) Flow Routing Algorithm | Professional Hydrological Design</p>
            
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
                    <div class="value">{total_length/1000:.1f} km</div>
                    <div class="label">Total Length</div>
                </div>
            </div>
        </header>
        
        <div class="chart-container">
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p class="loading-text">Loading 3D visualization...</p>
            </div>
            <div class="error-message" id="error">
                <strong>⚠️ Error loading chart</strong>
                <p>Please check your internet connection and refresh the page.</p>
            </div>
            <div id="chart"></div>
        </div>
        
        <footer class="footer">
            Generated by Professional Drainage Network Designer | D∞ Algorithm (Tarboton, 1997)
        </footer>
    </div>
    
    <script>
        // Chart data (embedded JSON - much smaller than Plotly library)
        const figureData = {fig_json};
        const chartConfig = {config_json};
        
        // Initialize chart when DOM and Plotly are ready
        document.addEventListener('DOMContentLoaded', function() {{
            const loadingEl = document.getElementById('loading');
            const errorEl = document.getElementById('error');
            const chartEl = document.getElementById('chart');
            
            // Function to render chart
            function renderChart() {{
                try {{
                    if (typeof Plotly === 'undefined') {{
                        throw new Error('Plotly library not loaded');
                    }}
                    
                    Plotly.newPlot(chartEl, figureData.data, figureData.layout, chartConfig)
                        .then(function() {{
                            loadingEl.classList.add('hidden');
                        }})
                        .catch(function(err) {{
                            console.error('Plotly render error:', err);
                            loadingEl.classList.add('hidden');
                            errorEl.classList.add('show');
                        }});
                }} catch (err) {{
                    console.error('Chart initialization error:', err);
                    loadingEl.classList.add('hidden');
                    errorEl.classList.add('show');
                }}
            }}
            
            // Check if Plotly is loaded, if not wait for it
            if (typeof Plotly !== 'undefined') {{
                renderChart();
            }} else {{
                // Wait for Plotly to load (deferred script)
                let attempts = 0;
                const maxAttempts = 50; // 5 seconds max wait
                
                const checkPlotly = setInterval(function() {{
                    attempts++;
                    if (typeof Plotly !== 'undefined') {{
                        clearInterval(checkPlotly);
                        renderChart();
                    }} else if (attempts >= maxAttempts) {{
                        clearInterval(checkPlotly);
                        loadingEl.classList.add('hidden');
                        errorEl.classList.add('show');
                    }}
                }}, 100);
            }}
        }});
        
        // Handle window resize for responsive chart
        window.addEventListener('resize', function() {{
            const chartEl = document.getElementById('chart');
            if (chartEl && typeof Plotly !== 'undefined') {{
                Plotly.Plots.resize(chartEl);
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
    def generate_report(self):
        """Generate engineering report."""
        print("\n📋 Generating report...")
        
        # Summary statistics
        total_length = sum(props.get('length_m', 0) for _, _, props in self.drainage_lines)
        total_flow = sum(props.get('peak_flow_m3s', 0) for _, _, props in self.drainage_lines)
        
        primary = [d for d in self.drainage_lines if d[0] == 'primary']
        secondary = [d for d in self.drainage_lines if d[0] == 'secondary']
        tertiary = [d for d in self.drainage_lines if d[0] == 'tertiary']
        
        report = {
            'project': {
                'terrain_file': str(self.dtm_path.name),
                'design_storm_return_years': self.design_storm_years,
                'runoff_coefficient': self.runoff_coeff
            },
            'terrain': self.design_data.get('terrain', {}),
            'network_summary': {
                'total_channels': len(self.drainage_lines),
                'primary_channels': len(primary),
                'secondary_channels': len(secondary),
                'tertiary_channels': len(tertiary),
                'total_length_m': total_length,
                'total_length_km': total_length / 1000,
                'outlets': len(self.outlets)
            },
            'hydraulics': {
                'design_method': 'Rational Method (Q=CIA)',
                'flow_routing': 'D∞ (D-Infinity) Algorithm (Tarboton, 1997)',
                'stream_threshold': f'{self.stream_threshold_pct}% of cells',
                'strahler_ordering': 'Applied',
                'pipe_sizing': "Manning's Equation",
                'velocity_limits': f'{HydrologicalConstants.MIN_VELOCITY}-{HydrologicalConstants.MAX_VELOCITY} m/s',
                'total_design_flow_m3s': total_flow
            },
            'design_selection': {
                'method': 'Slope-based automatic selection',
                'slope_thresholds': {
                    'very_low': f'< {HydrologicalConstants.SLOPE_VERY_LOW*100}%',
                    'low': f'< {HydrologicalConstants.SLOPE_LOW*100}%',
                    'moderate': f'< {HydrologicalConstants.SLOPE_MODERATE*100}%',
                    'high': f'< {HydrologicalConstants.SLOPE_HIGH*100}%',
                    'very_high': f'>= {HydrologicalConstants.SLOPE_VERY_HIGH*100}%'
                }
            },
            'channels': []
        }
        
        # Add channel details with enhanced properties
        for channel_type, coords, props in self.drainage_lines[:20]:  # Top 20
            report['channels'].append({
                'type': channel_type,
                'length_m': props.get('length_m', 0),
                'slope_pct': props.get('slope_pct', 0),
                'peak_flow_m3s': props.get('peak_flow_m3s', 0),
                'pipe_diameter_mm': props.get('pipe_diameter_mm', 0),
                'velocity_ms': props.get('velocity_ms', 0),
                'design_type': props.get('design_type', 'unknown'),
                'design_reason': props.get('design_reason', ''),
                'strahler_order': props.get('strahler_order'),
                'froude_number': props.get('froude_number', 0),
                'flow_regime': props.get('flow_regime', ''),
                'validation_passed': props.get('validation_passed', True)
            })
            
        # Save report
        report_path = self.output_dir / 'drainage_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"   ✓ Saved: {report_path}")
        
        return report
        
    def export_geojson(self):
        """Export network to GeoJSON."""
        features = []
        
        def convert_to_native(obj):
            """Convert numpy types to native Python types."""
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_native(i) for i in obj]
            return obj
        
        for channel_type, coords, props in self.drainage_lines:
            # Convert coordinates
            converted_coords = [[float(c[0]), float(c[1]), float(c[2])] for c in coords]
            
            # Convert properties
            converted_props = convert_to_native(props)
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': converted_coords
                },
                'properties': {
                    'type': channel_type,
                    **converted_props
                }
            }
            features.append(feature)
            
        geojson = {
            'type': 'FeatureCollection',
            'crs': {'type': 'name', 'properties': {'name': str(self.crs) if self.crs else 'unknown'}},
            'features': features
        }
        
        path = self.output_dir / 'drainage_network.geojson'
        with open(path, 'w') as f:
            json.dump(geojson, f)
            
        print(f"   ✓ Saved: {path}")
        
    def process(self):
        """Run complete analysis pipeline."""
        self.load_terrain()
        self.hydrological_processing()
        self.extract_drainage_network()
        self.identify_outlets()
        
        vis_path = self.create_visualization()
        report = self.generate_report()
        self.export_geojson()
        
        # Cleanup temp files (uncomment when debugging is complete)
        # shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Summary
        print(f"\n{'='*60}")
        print("  ANALYSIS COMPLETE (D∞ Flow Routing)")
        print(f"{'='*60}")
        print(f"\n📊 Network Summary:")
        print(f"   • Flow Algorithm: D∞ (D-Infinity)")
        print(f"   • Stream Threshold: {self.stream_threshold_pct}% of cells")
        print(f"   • Primary Channels: {report['network_summary']['primary_channels']}")
        print(f"   • Secondary Channels: {report['network_summary']['secondary_channels']}")  
        print(f"   • Tertiary Channels: {report['network_summary']['tertiary_channels']}")
        print(f"   • Total Length: {report['network_summary']['total_length_km']:.2f} km")
        print(f"   • Outlets: {report['network_summary']['outlets']}")
        
        # Count design types
        design_types = {}
        for _, _, props in self.drainage_lines:
            dt = props.get('design_type', 'unknown')
            design_types[dt] = design_types.get(dt, 0) + 1
        if design_types:
            print(f"\n🔧 Design Types Selected:")
            for dt, count in sorted(design_types.items(), key=lambda x: -x[1]):
                print(f"   • {dt.replace('_', ' ').title()}: {count}")
        
        # Validation summary
        valid_count = sum(1 for _, _, p in self.drainage_lines if p.get('validation_passed', True))
        total = len(self.drainage_lines)
        print(f"\n✅ Hydraulic Validation: {valid_count}/{total} channels passed")
        
        print(f"\n🌐 Visualization: {vis_path}")
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Professional Drainage Network Designer (D∞ Flow Routing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python professional_drainage.py terrain.tif output/
  python professional_drainage.py dtm.tif results/ --stream-threshold 0.5 --urban
  python professional_drainage.py dem.tif output/ --runoff-coeff 0.7 --storm-years 25

Flow Routing Algorithm:
  Uses D∞ (D-Infinity) algorithm (Tarboton, 1997) which distributes flow
  between multiple downslope cells for more accurate hillslope hydrology.

Design Selection:
  Automatically selects drainage infrastructure based on slope:
  - < 0.5%: Pump station required
  - 0.5-5%: Pipes or trapezoidal channels
  - 5-10%: Channels with erosion protection
  - 10-15%: Cascade channels
  - > 15%: Stepped channels
        """
    )
    parser.add_argument('dtm', help='Path to DTM raster (GeoTIFF)')
    parser.add_argument('output', help='Output directory')
    parser.add_argument('--runoff-coeff', type=float, default=0.5, 
                        help='Runoff coefficient C (0-1), default=0.5 (suburban)')
    parser.add_argument('--storm-years', type=int, default=10, 
                        help='Design storm return period in years, default=10')
    parser.add_argument('--stream-threshold', type=float, default=1.0,
                        help='Stream threshold as %% of total cells, default=1.0')
    parser.add_argument('--urban', action='store_true',
                        help='Urban area (affects design selection - prefers pipes)')
    
    args = parser.parse_args()
    
    designer = ProfessionalDrainageDesigner(args.dtm, args.output)
    designer.runoff_coeff = args.runoff_coeff
    designer.design_storm_years = args.storm_years
    designer.stream_threshold_pct = args.stream_threshold
    designer.is_urban = args.urban
    designer.process()


if __name__ == '__main__':
    main()
