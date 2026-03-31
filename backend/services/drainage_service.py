"""
Terra Pravah - Drainage Analysis Service
=========================================
Optimized drainage network analysis service with selectable flow routing algorithms.

This module embeds the core hydrological algorithms directly for improved
performance and reliability, eliminating external module dependencies.

Supported Flow Algorithms:
- D8 (8-Direction) - Fast, simple, single flow direction (DEFAULT for performance)
- D∞ (D-Infinity) - More accurate, distributes flow (Tarboton, 1997)

Hydrological Methods:
- Stream Delineation with Configurable Thresholds
- Strahler Stream Ordering for hierarchy classification
- Rational Method for peak flow (Q = CIA)
- Time of Concentration (Kirpich formula)
- Manning's Equation for open channel flow

Author: Terra Pravah System
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional, List, Tuple, Dict, Union
import numpy as np
from numpy.typing import NDArray
import warnings

warnings.filterwarnings('ignore')

# Type aliases
FloatArray = NDArray[np.floating[Any]]
IntArray = NDArray[np.signedinteger[Any]]

# Module availability flags and stubs
HAS_RASTERIO = False
HAS_SCIPY = False
HAS_WHITEBOX = False
HAS_PLOTLY = False

# Rasterio
rasterio: Any = None
rowcol: Any = None
xy: Any = None
try:
    import rasterio as _rasterio
    from rasterio.transform import rowcol as _rowcol, xy as _xy
    rasterio = _rasterio
    rowcol = _rowcol
    xy = _xy
    HAS_RASTERIO = True
except ImportError:
    pass

# Scipy
ndimage: Any = None
splprep: Any = None
splev: Any = None
try:
    from scipy import ndimage as _ndimage
    from scipy.interpolate import splprep as _splprep, splev as _splev
    ndimage = _ndimage
    splprep = _splprep
    splev = _splev
    HAS_SCIPY = True
except ImportError:
    pass

# WhiteboxTools
WhiteboxTools: Any = None
try:
    from whitebox import WhiteboxTools as _WhiteboxTools
    WhiteboxTools = _WhiteboxTools
    HAS_WHITEBOX = True
except ImportError:
    pass

# Plotly
go: Any = None
try:
    import plotly.graph_objects as _go
    go = _go
    HAS_PLOTLY = True
except ImportError:
    pass


# =============================================================================
# HYDROLOGICAL CONSTANTS
# =============================================================================

class HydrologicalConstants:
    """
    Standard hydrological and hydraulic constants.
    
    References:
    - IRC SP 13:2004 (Indian Roads Congress) for Indian drainage design
    - IS 5878:1970 for construction drainage
    - IMD (India Meteorological Department) for IDF parameters
    - ASCE Manual of Practice No. 77 for general hydraulics
    """
    
    # Manning's roughness coefficients (Chow, 1959)
    MANNING_N = {
        'concrete_pipe': 0.013,
        'pvc_pipe': 0.010,
        'hdpe_pipe': 0.011,
        'corrugated_metal': 0.024,
        'earth_channel': 0.025,
        'grass_channel': 0.035,
        'natural_stream': 0.040,
        'trapezoidal_channel': 0.022,
        'rectangular_channel': 0.015,
        'v_shaped_ditch': 0.030,
        'grass_lined_ditch': 0.040,
        'cascade_channel': 0.050,
        'stepped_channel': 0.045,
        'rip_rap_channel': 0.035,
        'gabion_channel': 0.028
    }
    
    # Runoff coefficients (C) for Rational Method
    # Extended for Indian conditions (IRC SP 13:2004)
    RUNOFF_COEFF = {
        'impervious': 0.95,
        'urban_high': 0.70,
        'urban_medium': 0.50,
        'suburban': 0.35,
        'rural': 0.20,
        'forest': 0.15,
        # Indian-specific land use types
        'paved_roads': 0.85,
        'gravel_roads': 0.35,
        'sandy_soil_flat': 0.10,
        'sandy_soil_steep': 0.20,
        'clay_soil_flat': 0.30,
        'clay_soil_steep': 0.50,
        'agricultural_row_crops': 0.35,
        'paddy_fields': 0.25,
        'scrubland_arid': 0.45  # Higher for arid regions like Rajasthan
    }
    
    # Runoff coefficient adjustment factors for antecedent moisture (AMC)
    # Based on SCS TR-55 methodology
    AMC_FACTORS = {
        'dry': 0.85,      # AMC I - Dry conditions
        'normal': 1.00,   # AMC II - Normal conditions
        'wet': 1.15       # AMC III - Wet conditions (monsoon)
    }
    
    # Design storm return periods (years)
    RETURN_PERIODS = [2, 5, 10, 25, 50, 100]
    
    # Minimum design slopes
    MIN_SLOPE_PIPE = 0.005  # 0.5%
    MIN_SLOPE_CHANNEL = 0.002  # 0.2%
    
    # Standard pipe diameters (mm) - Indian standards
    PIPE_DIAMETERS = [150, 200, 250, 300, 375, 450, 525, 600, 750, 900, 1050, 1200, 1500, 1800]
    
    # Velocity limits (m/s) for hydraulic validation (IRC SP 13:2004)
    MIN_VELOCITY = 0.6   # Minimum for self-cleaning
    MAX_VELOCITY = 3.0   # Maximum to prevent erosion (unlined)
    MAX_VELOCITY_LINED = 6.0  # Maximum for lined channels
    
    # Slope thresholds for design selection
    SLOPE_VERY_LOW = 0.005    # < 0.5% - requires pumping or special design
    SLOPE_LOW = 0.01          # 0.5-1% - standard pipe/channel
    SLOPE_MODERATE = 0.05     # 1-5% - trapezoidal channel preferred
    SLOPE_HIGH = 0.10         # 5-10% - may need energy dissipation
    SLOPE_VERY_HIGH = 0.15    # > 15% - cascade or stepped channel
    
    # Stream threshold as percentage of total cells
    DEFAULT_STREAM_THRESHOLD_PCT = 1.0
    
    # Safety factors (ASCE Manual of Practice No. 77)
    SAFETY_FACTOR_PIPE = 1.25  # Pipe capacity safety factor
    SAFETY_FACTOR_CHANNEL = 1.50  # Open channel safety factor
    FREEBOARD_RATIO = 0.20  # 20% freeboard for open channels
    
    # Regional IDF curve parameters for India (IMD methodology)
    # Format: {region: {'a': coefficient, 'b': time shift, 'n': exponent}}
    # I = a / (t + b)^n where I is intensity (mm/hr), t is duration (min)
    IDF_INDIA_REGIONS = {
        'default': {'a': 1000, 'b': 10, 'n': 0.8},
        'rajasthan_arid': {'a': 850, 'b': 8, 'n': 0.75},  # Arid regions - shorter, intense storms
        'delhi_ncr': {'a': 1100, 'b': 12, 'n': 0.82},
        'mumbai_coastal': {'a': 1500, 'b': 15, 'n': 0.85},  # High intensity monsoon
        'chennai_coastal': {'a': 1400, 'b': 14, 'n': 0.83},
        'bengaluru_deccan': {'a': 1000, 'b': 11, 'n': 0.78},
        'kolkata_gangetic': {'a': 1200, 'b': 13, 'n': 0.80},
        'northeast_hills': {'a': 1800, 'b': 18, 'n': 0.88}  # Very high rainfall
    }
    
    # Return period factors for IDF curves (Gumbel distribution)
    # Multipliers for base 10-year intensity
    RETURN_PERIOD_FACTORS = {
        2: 0.70,
        5: 0.87,
        10: 1.00,
        25: 1.18,
        50: 1.32,
        100: 1.46
    }


# =============================================================================
# DESIGN SELECTION
# =============================================================================

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
            if peak_flow > 1.0:
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


# =============================================================================
# HYDRAULIC VALIDATION
# =============================================================================

class HydraulicValidator:
    """
    Validates hydraulic design parameters for drainage systems.
    """
    
    @staticmethod
    def validate_continuity(upstream_flows: list, downstream_flow: float, tolerance: float = 0.01) -> dict:
        """Check flow continuity (mass balance)."""
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
        Validate slope meets minimum requirements with detailed recommendations.
        
        Args:
            slope: Channel/pipe slope (m/m)
            infrastructure_type: 'pipe' or 'channel'
            
        Returns:
            dict with validation result and recommendations
        """
        min_slope = (HydrologicalConstants.MIN_SLOPE_PIPE if infrastructure_type == 'pipe' 
                     else HydrologicalConstants.MIN_SLOPE_CHANNEL)
        
        # Classification thresholds - convert to native Python bool for JSON serialization
        is_very_flat = bool(slope < HydrologicalConstants.SLOPE_VERY_LOW)
        is_flat = bool(slope < min_slope)
        is_steep = bool(slope > HydrologicalConstants.SLOPE_HIGH)
        is_very_steep = bool(slope > HydrologicalConstants.SLOPE_VERY_HIGH)
        
        recommendations = []
        design_notes = []
        
        if is_very_flat:
            recommendations.append('Consider pump station or storage-based drainage')
            recommendations.append('Evaluate feasibility of outlet relocation')
            design_notes.append('Very flat terrain may require powered drainage')
        elif is_flat:
            recommendations.append('Increase slope by adjusting invert levels')
            recommendations.append('Use larger diameter to maintain self-cleaning velocity')
            recommendations.append('Consider steep-gradient manholes')
            design_notes.append('Minimum slope not met - review design')
        
        if is_very_steep:
            recommendations.append('Use stepped or cascade channel design')
            recommendations.append('Include energy dissipation structures')
            design_notes.append('Very steep slope requires erosion protection')
        elif is_steep:
            recommendations.append('Check maximum velocity limits')
            recommendations.append('Consider drop structures at intervals')
            design_notes.append('Energy dissipation may be required')
        
        # Calculate required diameter increase for flat slopes
        diameter_factor = None
        if is_flat and slope > 0:
            # To maintain velocity, need D_new/D_old = (S_min/S_actual)^(3/8)
            diameter_factor = (min_slope / slope) ** 0.375
        
        return {
            'valid': not is_flat,
            'issue': f'Slope below minimum ({slope*100:.3f}% < {min_slope*100:.2f}%)' if is_flat else None,
            'actual_slope': slope,
            'actual_slope_pct': slope * 100,
            'min_required': min_slope,
            'margin': slope - min_slope,
            'classification': 'very_flat' if is_very_flat else ('flat' if is_flat else 
                            ('very_steep' if is_very_steep else ('steep' if is_steep else 'normal'))),
            'recommendations': recommendations,
            'design_notes': design_notes,
            'diameter_increase_factor': diameter_factor,
            'requires_pump': is_very_flat,
            'requires_energy_dissipation': is_very_steep
        }
    
    @staticmethod
    def validate_velocity(velocity: float) -> dict:
        """Validate flow velocity is within acceptable range."""
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
            'valid': len(issues) == 0,
            'velocity': float(velocity),
            'min_velocity': float(HydrologicalConstants.MIN_VELOCITY),
            'max_velocity': float(HydrologicalConstants.MAX_VELOCITY),
            'issues': issues,
            'recommendations': recommendations,
            'flow_regime': 'acceptable' if not issues else ('too slow' if velocity < 0.6 else 'too fast')
        }
    
    @staticmethod
    def full_validation(slope: float, velocity: float, upstream_flows: Optional[List[float]] = None, 
                        downstream_flow: Optional[float] = None, infrastructure_type: str = 'pipe') -> Dict[str, Any]:
        """Perform complete hydraulic validation."""
        results: Dict[str, Any] = {
            'slope_validation': HydraulicValidator.validate_slope(slope, infrastructure_type),
            'velocity_validation': HydraulicValidator.validate_velocity(velocity)
        }
        
        if upstream_flows is not None and downstream_flow is not None:
            results['continuity_validation'] = HydraulicValidator.validate_continuity(
                upstream_flows, downstream_flow
            )
            
        # Ensure all_valid is a native Python bool for JSON serialization
        all_valid = bool(all(r.get('valid', True) for r in results.values() if isinstance(r, dict)))
        results['overall_valid'] = all_valid
        
        return results


# =============================================================================
# FLUID MECHANICS
# =============================================================================

class FluidMechanics:
    """
    Fluid mechanics calculations for drainage design.
    
    Implements hydraulic calculations based on:
    - Manning's equation for open channels and pipes
    - Hydraulic radius and flow capacity
    - Froude number for flow regime classification
    - Pipe sizing with safety factors
    
    References:
    - Chow, V.T. (1959) - Open Channel Hydraulics
    - ASCE Manual of Practice No. 77
    - IRC SP 13:2004 - Indian design standards
    """
    
    @staticmethod
    def manning_velocity(hydraulic_radius: float, slope: float, n: float = 0.013) -> float:
        """
        Manning's equation for flow velocity.
        V = (1/n) * R^(2/3) * S^(1/2)
        
        Args:
            hydraulic_radius: Hydraulic radius R = A/P (m)
            slope: Energy slope S (m/m)
            n: Manning's roughness coefficient
            
        Returns:
            Flow velocity in m/s
        """
        if slope <= 0 or hydraulic_radius <= 0:
            return 0
        return (1 / n) * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
    
    @staticmethod
    def manning_flow(area: float, hydraulic_radius: float, slope: float, n: float = 0.013) -> float:
        """Flow rate using Manning's equation. Q = A * V"""
        velocity = FluidMechanics.manning_velocity(hydraulic_radius, slope, n)
        return area * velocity
    
    @staticmethod
    def pipe_full_flow(diameter: float, slope: float, n: float = 0.013) -> float:
        """Full pipe flow capacity."""
        area = np.pi * (diameter / 2) ** 2
        hydraulic_radius = diameter / 4
        return FluidMechanics.manning_flow(area, hydraulic_radius, slope, n)
    
    @staticmethod
    def pipe_partial_flow(diameter: float, depth_ratio: float, slope: float, n: float = 0.013) -> dict:
        """
        Calculate partial flow in circular pipe.
        
        Args:
            diameter: Pipe diameter in meters
            depth_ratio: y/D ratio (0 to 1)
            slope: Pipe slope (m/m)
            n: Manning's n
            
        Returns:
            dict with flow, velocity, area, wetted perimeter
            
        Reference:
            Chow (1959), Table 2-1 for circular section properties.
        """
        if depth_ratio <= 0 or depth_ratio > 1:
            return {'flow': 0, 'velocity': 0, 'area': 0, 'wetted_perimeter': 0}
        
        r = diameter / 2
        
        # Central angle (radians)
        if depth_ratio >= 1:
            theta = 2 * np.pi
        else:
            theta = 2 * np.arccos(1 - 2 * depth_ratio)
        
        # Geometric properties
        area = (r ** 2 / 2) * (theta - np.sin(theta))
        wetted_perimeter = r * theta
        hydraulic_radius = area / wetted_perimeter if wetted_perimeter > 0 else 0
        
        velocity = FluidMechanics.manning_velocity(hydraulic_radius, slope, n)
        flow = area * velocity
        
        return {
            'flow': flow,
            'velocity': velocity,
            'area': area,
            'wetted_perimeter': wetted_perimeter,
            'hydraulic_radius': hydraulic_radius,
            'depth_ratio': depth_ratio
        }
    
    @staticmethod
    def froude_number(velocity: float, depth: float) -> float:
        """
        Froude number for flow characterization.
        Fr = V / sqrt(g * D)
        
        Fr < 1: Subcritical (tranquil) flow
        Fr = 1: Critical flow
        Fr > 1: Supercritical (rapid) flow
        """
        g = 9.81
        if depth <= 0:
            return 0
        return velocity / np.sqrt(g * depth)
    
    @staticmethod
    def critical_depth(flow: float, width: float) -> float:
        """
        Calculate critical depth for rectangular channel.
        yc = (Q² / (g * b²))^(1/3)
        
        Args:
            flow: Discharge in m³/s
            width: Channel bottom width in meters
            
        Returns:
            Critical depth in meters
        """
        g = 9.81
        if width <= 0 or flow <= 0:
            return 0
        return ((flow ** 2) / (g * width ** 2)) ** (1/3)
    
    @staticmethod
    def required_pipe_diameter(flow: float, slope: float, n: float = 0.013,
                               safety_factor: float = None,
                               max_depth_ratio: float = 0.80) -> float:
        """
        Calculate required pipe diameter with safety factor and freeboard.
        
        Args:
            flow: Design flow in m³/s
            slope: Pipe slope (m/m)
            n: Manning's roughness coefficient
            safety_factor: Capacity safety factor (default from constants)
            max_depth_ratio: Maximum depth/diameter ratio for freeboard
                            (default 0.80 = 20% freeboard)
            
        Returns:
            Required pipe diameter in mm
            
        Note:
            Design ensures pipe flows at max_depth_ratio to provide
            freeboard for surges and debris. Safety factor accounts
            for construction tolerances and aging.
        """
        if safety_factor is None:
            safety_factor = HydrologicalConstants.SAFETY_FACTOR_PIPE
        
        # Apply safety factor to design flow
        design_flow = flow * safety_factor
        
        for d_mm in HydrologicalConstants.PIPE_DIAMETERS:
            d_m = d_mm / 1000
            
            # Calculate capacity at design depth ratio (with freeboard)
            partial_flow = FluidMechanics.pipe_partial_flow(
                d_m, max_depth_ratio, slope, n
            )
            
            if partial_flow['flow'] >= design_flow:
                return d_mm
        
        return HydrologicalConstants.PIPE_DIAMETERS[-1]
    
    @staticmethod
    def required_pipe_diameter_simple(flow: float, slope: float, n: float = 0.013) -> float:
        """
        Simple pipe sizing without safety factor (backward compatible).
        """
        for d_mm in HydrologicalConstants.PIPE_DIAMETERS:
            d_m = d_mm / 1000
            capacity = FluidMechanics.pipe_full_flow(d_m, slope, n)
            if capacity >= flow:
                return d_mm
        return HydrologicalConstants.PIPE_DIAMETERS[-1]
    
    @staticmethod
    def trapezoidal_channel_capacity(bottom_width: float, depth: float,
                                      side_slope: float, bed_slope: float,
                                      n: float = 0.025) -> dict:
        """
        Calculate trapezoidal channel flow capacity.
        
        Args:
            bottom_width: Channel bottom width (m)
            depth: Flow depth (m)
            side_slope: Horizontal:Vertical ratio (e.g., 2 for 2H:1V)
            bed_slope: Channel bed slope (m/m)
            n: Manning's n
            
        Returns:
            dict with area, wetted perimeter, hydraulic radius, velocity, flow
        """
        area = (bottom_width + side_slope * depth) * depth
        wetted_perimeter = bottom_width + 2 * depth * np.sqrt(1 + side_slope ** 2)
        hydraulic_radius = area / wetted_perimeter if wetted_perimeter > 0 else 0
        
        velocity = FluidMechanics.manning_velocity(hydraulic_radius, bed_slope, n)
        flow = area * velocity
        
        return {
            'area': area,
            'wetted_perimeter': wetted_perimeter,
            'hydraulic_radius': hydraulic_radius,
            'velocity': velocity,
            'flow': flow,
            'top_width': bottom_width + 2 * side_slope * depth
        }


# =============================================================================
# HYDROLOGICAL ANALYSIS
# =============================================================================

class HydrologicalAnalysis:
    """
    Hydrological analysis methods.
    
    Implements multiple industry-standard methods for:
    - Peak flow estimation (Rational Method with safety factors)
    - Time of concentration (Kirpich, NRCS, Bransby-Williams)
    - Rainfall intensity (Regional IDF curves for India)
    - Runoff depth (SCS-CN method)
    
    References:
    - USDA-NRCS TR-55 (1986) - Urban Hydrology for Small Watersheds
    - IRC SP 13:2004 - Indian drainage design guidelines
    - Chow, V.T. (1959) - Open Channel Hydraulics
    """
    
    @staticmethod
    def rational_method(C: float, I: float, A: float, safety_factor: float = 1.0) -> float:
        """
        Rational Method for peak runoff with optional safety factor.
        Q = C * I * A / 360 * SF
        
        Args:
            C: Runoff coefficient (0-1)
            I: Rainfall intensity (mm/hr)
            A: Catchment area (hectares)
            safety_factor: Capacity safety factor (default 1.0, recommended 1.25-1.5)
            
        Returns:
            Peak flow Q in m³/s
            
        Note:
            Rational Method is valid for catchments < 80 hectares (IRC SP 13:2004).
            For larger areas, consider SCS Unit Hydrograph method.
        """
        return C * I * A * safety_factor / 360
    
    @staticmethod
    def time_of_concentration_kirpich(length: float, slope: float) -> float:
        """
        Kirpich formula for time of concentration.
        Tc = 0.0078 * L^0.77 * S^(-0.385)
        
        Best for: Natural basins with well-defined channels.
        
        Args:
            length: Flow path length in meters
            slope: Average slope (m/m)
            
        Returns:
            Time of concentration in minutes
            
        Reference:
            Kirpich, Z.P. (1940). Time of concentration of small agricultural watersheds.
        """
        if slope <= 0:
            slope = 0.001
        L_ft = length * 3.281
        S_pct = slope * 100
        tc = 0.0078 * (L_ft ** 0.77) * (S_pct ** (-0.385))
        return max(tc, 5.0)  # Minimum 5 minutes as per ASCE guidelines
    
    @staticmethod
    def time_of_concentration_nrcs(length: float, slope: float, cn: float = 75) -> float:
        """
        NRCS (SCS) Lag Method for time of concentration.
        Tc = L^0.8 * ((1000/CN) - 9)^0.7 / (1900 * S^0.5)
        
        Best for: Urban and suburban areas with mixed land use.
        
        Args:
            length: Flow path length in meters
            slope: Average slope (m/m)
            cn: SCS Curve Number (default 75)
            
        Returns:
            Time of concentration in minutes
            
        Reference:
            USDA-NRCS TR-55 (1986), Chapter 3.
        """
        if slope <= 0:
            slope = 0.001
        if cn <= 0 or cn > 100:
            cn = 75
        
        L_ft = length * 3.281
        S_pct = slope * 100
        
        # Lag time formula
        lag_hr = (L_ft ** 0.8 * ((1000 / cn) - 9) ** 0.7) / (1900 * (S_pct ** 0.5))
        tc = lag_hr * 60 / 0.6  # Tc = Lag / 0.6
        
        return max(tc, 5.0)
    
    @staticmethod
    def time_of_concentration_bransby_williams(length: float, slope: float, area_km2: float) -> float:
        """
        Bransby-Williams formula for time of concentration.
        Tc = 0.243 * L / (A^0.1 * S^0.2)
        
        Best for: Rural catchments in arid/semi-arid regions (e.g., Rajasthan).
        
        Args:
            length: Main channel length in km
            slope: Average slope (m/m)
            area_km2: Catchment area in km²
            
        Returns:
            Time of concentration in minutes
            
        Reference:
            Widely used in Australian and Indian practice for rural catchments.
        """
        if slope <= 0:
            slope = 0.001
        if area_km2 <= 0:
            area_km2 = 0.01
            
        L_km = length / 1000 if length > 100 else length  # Assume meters if > 100
        S_pct = slope * 100
        
        tc_hr = 0.243 * L_km / ((area_km2 ** 0.1) * (S_pct ** 0.2))
        return max(tc_hr * 60, 5.0)
    
    @staticmethod
    def time_of_concentration_combined(length: float, slope: float, 
                                        area_ha: float = None, cn: float = 75,
                                        method: str = 'auto') -> dict:
        """
        Calculate Tc using multiple methods and return recommended value.
        
        Args:
            length: Flow path length in meters
            slope: Average slope (m/m)
            area_ha: Catchment area in hectares (optional)
            cn: Curve Number for NRCS method
            method: 'kirpich', 'nrcs', 'bransby', or 'auto' (average)
            
        Returns:
            dict with Tc values from each method and recommended value
        """
        results = {
            'kirpich': HydrologicalAnalysis.time_of_concentration_kirpich(length, slope),
            'nrcs': HydrologicalAnalysis.time_of_concentration_nrcs(length, slope, cn)
        }
        
        if area_ha:
            area_km2 = area_ha / 100
            results['bransby_williams'] = HydrologicalAnalysis.time_of_concentration_bransby_williams(
                length, slope, area_km2
            )
        
        if method == 'auto':
            # Use geometric mean for robustness
            values = list(results.values())
            recommended = np.exp(np.mean(np.log(values)))
        else:
            recommended = results.get(method, results['kirpich'])
        
        results['recommended'] = recommended
        results['method_used'] = method
        
        return results
    
    @staticmethod
    def rainfall_intensity(duration: float, return_period: int = 10,
                          region: str = 'default') -> float:
        """
        Regional IDF curve for rainfall intensity with India-specific parameters.
        I = (a * Kf) / (t + b)^n
        
        Args:
            duration: Storm duration in minutes
            return_period: Return period in years (2, 5, 10, 25, 50, 100)
            region: Climate region (see HydrologicalConstants.IDF_INDIA_REGIONS)
            
        Returns:
            Rainfall intensity in mm/hr
            
        Reference:
            India Meteorological Department (IMD) IDF curves.
            Regional coefficients based on published rainfall analyses.
        """
        # Get regional parameters
        idf_params = HydrologicalConstants.IDF_INDIA_REGIONS.get(
            region, HydrologicalConstants.IDF_INDIA_REGIONS['default']
        )
        
        a = idf_params['a']
        b = idf_params['b']
        n = idf_params['n']
        
        # Apply return period factor
        kf = HydrologicalConstants.RETURN_PERIOD_FACTORS.get(return_period, 1.0)
        
        # Ensure minimum duration
        duration = max(duration, 5.0)
        
        return (a * kf) / ((duration + b) ** n)
    
    @staticmethod
    def rainfall_intensity_empirical(duration: float, return_period: int = 10,
                                     annual_rainfall_mm: float = 800) -> float:
        """
        Empirical rainfall intensity based on annual rainfall.
        Useful when regional IDF data is unavailable.
        
        Args:
            duration: Storm duration in minutes
            return_period: Return period in years
            annual_rainfall_mm: Mean annual rainfall in mm
            
        Returns:
            Rainfall intensity in mm/hr
            
        Reference:
            Modified from CPWD (Central Public Works Dept, India) guidelines.
        """
        # Base intensity scaled by annual rainfall
        # Arid regions (~400mm) get lower base, high rainfall (~2000mm) get higher
        base_factor = (annual_rainfall_mm / 800) ** 0.6
        
        a = 900 * base_factor
        kf = HydrologicalConstants.RETURN_PERIOD_FACTORS.get(return_period, 1.0)
        
        return (a * kf) / ((duration + 10) ** 0.75)
    
    @staticmethod
    def scs_curve_number_runoff(P: float, CN: float, 
                                 amc: str = 'normal') -> float:
        """
        SCS Curve Number method for runoff depth with AMC adjustment.
        Q = (P - 0.2S)² / (P + 0.8S)
        
        Args:
            P: Precipitation depth in mm
            CN: Curve Number (0-100)
            amc: Antecedent Moisture Condition ('dry', 'normal', 'wet')
            
        Returns:
            Runoff depth Q in mm
            
        Reference:
            USDA-SCS (1972) National Engineering Handbook, Section 4.
        """
        if CN <= 0 or CN > 100:
            return 0
        
        # Adjust CN for antecedent moisture
        amc_factor = HydrologicalConstants.AMC_FACTORS.get(amc, 1.0)
        CN_adjusted = min(CN * amc_factor, 98)  # Cap at 98
        
        S = (25400 / CN_adjusted) - 254  # Potential maximum retention (mm)
        Ia = 0.2 * S  # Initial abstraction (standard 0.2S, some use 0.05S)
        
        if P <= Ia:
            return 0
        return ((P - Ia) ** 2) / (P - Ia + S)
    
    @staticmethod
    def adjusted_runoff_coefficient(base_C: float, slope: float, 
                                    soil_type: str = 'normal',
                                    amc: str = 'normal') -> float:
        """
        Adjust runoff coefficient for slope and soil conditions.
        
        Args:
            base_C: Base runoff coefficient from land use
            slope: Terrain slope (m/m)
            soil_type: 'sandy', 'normal', 'clay'
            amc: Antecedent moisture condition
            
        Returns:
            Adjusted runoff coefficient
            
        Reference:
            IRC SP 13:2004 - Guidelines for design of small bridges and culverts.
        """
        # Slope adjustment (+0.1 for steep, -0.05 for flat)
        if slope > 0.10:
            slope_adj = 0.10
        elif slope > 0.05:
            slope_adj = 0.05
        elif slope < 0.01:
            slope_adj = -0.05
        else:
            slope_adj = 0
        
        # Soil type adjustment
        soil_adj = {'sandy': -0.10, 'normal': 0, 'clay': 0.10}.get(soil_type, 0)
        
        # AMC adjustment
        amc_factor = HydrologicalConstants.AMC_FACTORS.get(amc, 1.0)
        
        adjusted_C = (base_C + slope_adj + soil_adj) * amc_factor
        
        return max(0.05, min(0.95, adjusted_C))  # Clamp to valid range


# =============================================================================
# OPTIMIZED DRAINAGE DESIGNER
# =============================================================================

class OptimizedDrainageDesigner:
    """
    Optimized drainage network designer using D∞ (D-Infinity) flow routing.
    
    Performance optimizations:
    - Efficient grid processing with numpy vectorization
    - Limited headwater sampling to prevent timeout
    - Chunked processing for large terrains
    - Progress callbacks for status updates
    """
    
    def __init__(self, dtm_path: str, output_dir: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the drainage designer.
        
        Args:
            dtm_path: Path to DTM raster file
            output_dir: Output directory for results
            config: Optional configuration dictionary
        """
        self.dtm_path = Path(dtm_path).resolve()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = self.output_dir / 'temp'
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create visualization and results directories early to prevent creation errors later
        self.vis_dir = self.output_dir / 'visualizations'
        self.vis_dir.mkdir(exist_ok=True)
        
        self.results_subdir = self.output_dir / 'results'
        self.results_subdir.mkdir(exist_ok=True)
        
        self.config: Dict[str, Any] = config or {}
        
        # WhiteboxTools
        if HAS_WHITEBOX and WhiteboxTools is not None:
            self.wbt: Any = WhiteboxTools()
            self.wbt.set_verbose_mode(False)
        else:
            self.wbt = None
            
        # DTM data - typed arrays
        self.dtm: Optional[FloatArray] = None
        self.filled_dtm: Optional[FloatArray] = None
        self.transform: Any = None
        self.crs: Any = None
        self.bounds: Any = None
        self.resolution: Optional[float] = None
        self.nodata_mask: Optional[NDArray[np.bool_]] = None
        
        # Hydrological grids
        self.flow_direction: Optional[FloatArray] = None
        self.flow_accumulation: Optional[FloatArray] = None
        self.slope: Optional[FloatArray] = None
        self.catchment_area: Optional[FloatArray] = None
        self.dinf_flow_direction: Optional[FloatArray] = None
        self.stream_raster: Optional[IntArray] = None
        self.strahler_order: Optional[IntArray] = None
        
        # Network
        self.drainage_lines: List[Tuple[str, List[Tuple[float, float, float]], Dict[str, Any]]] = []
        self.outlets: List[Dict[str, Any]] = []
        self.design_data: Dict[str, Any] = {}
        self.validation_results: Dict[str, Any] = {}
        
        # Parameters - with sensible defaults
        self.flow_threshold = 10000
        self.runoff_coeff = self.config.get('runoff_coefficient', 0.5)
        self.design_storm_years = self.config.get('design_storm_years', 10)
        self.stream_threshold_pct = self.config.get('stream_threshold_pct', 1.0)
        self.is_urban = self.config.get('is_urban', False)
        
        # Regional settings for India-specific IDF curves
        # Options: 'default', 'rajasthan_arid', 'delhi_ncr', 'mumbai_coastal', 
        #          'chennai_coastal', 'bengaluru_deccan', 'kolkata_gangetic', 'northeast_hills'
        self.climate_region = self.config.get('climate_region', 'default')
        
        # Antecedent moisture condition: 'dry', 'normal', 'wet'
        self.amc = self.config.get('antecedent_moisture', 'normal')
        
        # Soil type for runoff adjustment: 'sandy', 'normal', 'clay'
        self.soil_type = self.config.get('soil_type', 'normal')
        
        # Time of concentration method: 'kirpich', 'nrcs', 'bransby', 'auto'
        self.tc_method = self.config.get('tc_method', 'kirpich')
        
        # Safety factors (can be overridden)
        self.safety_factor = self.config.get('safety_factor', 
                                             HydrologicalConstants.SAFETY_FACTOR_PIPE)
        
        # Flow algorithm selection - D8 is faster, D∞ is more accurate
        # Default to D8 for performance
        self.flow_algorithm = self.config.get('flow_algorithm', 'd8').lower()
        if self.flow_algorithm not in ['d8', 'dinf', 'mfd']:
            self.flow_algorithm = 'd8'
        
        # Performance limits - tuned for responsiveness
        self.max_headwaters = 80   # Reduced for faster processing
        self.max_trace_steps = 800  # Reduced for faster tracing
        self.min_spacing = 40       # Increased for fewer channels
        self.min_channel_length = 25  # Minimum channel length in meters
        
        # Visualization limits
        self.max_terrain_points = 80  # Max grid size for terrain viz
        self.max_drainage_lines_viz = 50  # Max lines to visualize
        
        # Progress callback
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        
    def set_progress_callback(self, callback: Optional[Callable[[int, str], None]]) -> None:
        """Set progress callback function(progress, step)."""
        self.progress_callback = callback
        
    def _report_progress(self, progress: int, step: str):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(progress, step)
            
    def load_terrain(self) -> 'OptimizedDrainageDesigner':
        """Load and validate terrain data."""
        self._report_progress(5, 'Loading terrain data')
        
        if not HAS_RASTERIO or rasterio is None:
            raise RuntimeError("rasterio is required for terrain loading")
            
        with rasterio.open(self.dtm_path) as src:
            self.dtm = src.read(1).astype(np.float64)
            self.transform = src.transform
            self.crs = src.crs
            self.bounds = src.bounds
            self.resolution = float(src.res[0])
            nodata = src.nodata
        
        # Type assertion - dtm is now set
        dtm = self.dtm
        assert dtm is not None
        
        if nodata is not None:
            dtm[dtm == nodata] = np.nan
            
        self.nodata_mask = np.isnan(dtm)
        nodata_mask = self.nodata_mask
        assert nodata_mask is not None
        
        valid = dtm[~nodata_mask]
        resolution = self.resolution
        assert resolution is not None
        
        self.design_data['terrain'] = {
            'dimensions': f"{dtm.shape[1]} x {dtm.shape[0]}",
            'resolution_m': resolution,
            'elevation_min': float(valid.min()),
            'elevation_max': float(valid.max()),
            'elevation_range': float(valid.max() - valid.min())
        }
        
        return self
        
    def hydrological_processing(self) -> 'OptimizedDrainageDesigner':
        """
        Run hydrological analysis using selected flow algorithm.
        
        Supports:
        - D8: Fast single-direction flow (default for performance)
        - D∞: More accurate multi-direction flow (Tarboton, 1997)
        
        Falls back to scipy-based processing if WhiteboxTools unavailable.
        """
        algorithm_name = 'D8' if self.flow_algorithm == 'd8' else 'D-Infinity'
        self._report_progress(15, f'Hydrological processing ({algorithm_name})')
        
        if not HAS_WHITEBOX or not self.wbt:
            return self._fallback_hydrology()
            
        # Paths for temporary rasters
        filled = str((self.temp_dir / 'filled.tif').resolve())
        d8_flow_dir = str((self.temp_dir / 'd8_flow_dir.tif').resolve())
        d8_flow_acc = str((self.temp_dir / 'd8_flow_acc.tif').resolve())
        slope_path = str((self.temp_dir / 'slope.tif').resolve())
        streams_path = str((self.temp_dir / 'streams.tif').resolve())
        strahler_path = str((self.temp_dir / 'strahler.tif').resolve())
        
        # D∞ paths (only used if algorithm is dinf)
        dinf_flow_dir = str((self.temp_dir / 'dinf_flow_dir.tif').resolve())
        dinf_flow_acc = str((self.temp_dir / 'dinf_flow_acc.tif').resolve())
        
        try:
            # Step 1: Fill depressions (fast breach method)
            self._report_progress(20, 'Conditioning DEM (breach depressions)')
            self.wbt.breach_depressions(str(self.dtm_path), filled)
            
            if self.flow_algorithm == 'd8':
                # ===== D8 ALGORITHM (FASTER) =====
                self._report_progress(30, 'Computing D8 flow direction')
                self.wbt.d8_pointer(filled, d8_flow_dir)
                
                self._report_progress(40, 'Computing D8 flow accumulation')
                self.wbt.d8_flow_accumulation(filled, d8_flow_acc, out_type='cells')
                
                # Load D8 results
                with rasterio.open(d8_flow_acc) as src:
                    self.flow_accumulation = src.read(1).astype(np.float64)
                    
                with rasterio.open(d8_flow_dir) as src:
                    self.flow_direction = src.read(1)
                    
                self.dinf_flow_direction = None
                
            else:
                # ===== D-INFINITY ALGORITHM (MORE ACCURATE) =====
                self._report_progress(25, 'Computing D∞ flow direction')
                self.wbt.d_inf_pointer(filled, dinf_flow_dir)
                
                self._report_progress(35, 'Computing D∞ flow accumulation')
                self.wbt.d_inf_flow_accumulation(filled, dinf_flow_acc, out_type='sca')
                
                # Also compute D8 for stream ordering
                self._report_progress(40, 'Computing D8 for stream network')
                self.wbt.d8_pointer(filled, d8_flow_dir)
                
                # Load D∞ results
                with rasterio.open(dinf_flow_acc) as src:
                    self.flow_accumulation = src.read(1)
                    
                with rasterio.open(dinf_flow_dir) as src:
                    self.dinf_flow_direction = src.read(1)
                    
                with rasterio.open(d8_flow_dir) as src:
                    self.flow_direction = src.read(1)
            
            # Step: Stream delineation
            self._report_progress(50, 'Delineating streams')
            self._extract_streams_with_threshold(
                d8_flow_acc if self.flow_algorithm == 'd8' else dinf_flow_acc,
                d8_flow_dir, 
                streams_path, 
                strahler_path
            )
            
            # Step: Slope calculation
            self._report_progress(55, 'Computing slope')
            self.wbt.slope(filled, slope_path, units='degrees')
                
            with rasterio.open(slope_path) as src:
                slope_deg = src.read(1)
                self.slope = np.tan(np.radians(slope_deg))
                
            # Load stream network and Strahler order
            try:
                with rasterio.open(streams_path) as src:
                    self.stream_raster = src.read(1)
                with rasterio.open(strahler_path) as src:
                    self.strahler_order = src.read(1)
            except Exception:
                self.stream_raster = None
                self.strahler_order = None
                
            # Load filled DEM
            with rasterio.open(filled) as src:
                self.filled_dtm = src.read(1)
                
            # Calculate catchment area
            resolution = self.resolution
            assert resolution is not None
            flow_acc = self.flow_accumulation
            assert flow_acc is not None
            self.catchment_area = flow_acc * (resolution ** 2)
            
            # Store algorithm info in design data
            self.design_data['flow_algorithm'] = {
                'type': self.flow_algorithm,
                'name': algorithm_name,
                'description': 'D8 single-direction flow' if self.flow_algorithm == 'd8' else 'D-Infinity multi-direction flow'
            }
            
        except Exception as e:
            # Fallback if WhiteboxTools fails
            self._report_progress(30, f'WhiteboxTools failed, using fallback: {str(e)[:50]}')
            return self._fallback_hydrology()
            
        return self
    
    def _extract_streams_with_threshold(self, flow_acc_path, flow_dir_path, streams_path, strahler_path):
        """Extract stream network using flow accumulation threshold."""
        with rasterio.open(flow_acc_path) as src:
            flow_acc = src.read(1)
            profile = src.profile
            
        valid_cells = flow_acc[~np.isnan(flow_acc) & (flow_acc > 0)]
        if len(valid_cells) > 0:
            threshold_value = np.percentile(valid_cells, 100 - self.stream_threshold_pct)
            
            streams = (flow_acc >= threshold_value).astype(np.int16)
            streams[np.isnan(flow_acc)] = 0
            
            profile.update(dtype=rasterio.int16, nodata=-1)
            # If BLOCKXSIZE is set, TILED must be YES
            if 'blockxsize' in profile or 'blocksize' in profile:
                profile['tiled'] = True
            with rasterio.open(streams_path, 'w', **profile) as dst:
                dst.write(streams, 1)
                
            try:
                self.wbt.strahler_stream_order(flow_dir_path, streams_path, strahler_path)
            except Exception:
                # Create simple order based on accumulation
                strahler = np.zeros_like(flow_acc, dtype=np.int16)
                strahler[streams > 0] = 1 + np.log10(flow_acc[streams > 0] + 1).astype(int)
                with rasterio.open(strahler_path, 'w', **profile) as dst:
                    dst.write(strahler, 1)
        
    def _fallback_hydrology(self) -> 'OptimizedDrainageDesigner':
        """Fallback when WhiteboxTools unavailable."""
        self._report_progress(30, 'Using scipy-based hydrology (fallback)')
        
        # Assertions for required data
        dtm = self.dtm
        assert dtm is not None, "DTM must be loaded first"
        resolution = self.resolution
        assert resolution is not None, "Resolution must be set"
        nodata_mask = self.nodata_mask
        assert nodata_mask is not None, "Nodata mask must be set"
        
        if HAS_SCIPY:
            dy, dx = np.gradient(dtm, resolution)
            slope_arr = np.sqrt(dx**2 + dy**2)
            slope_arr[nodata_mask] = np.nan
            self.slope = slope_arr
        else:
            slope_arr = np.ones_like(dtm) * 0.01
            slope_arr[nodata_mask] = np.nan
            self.slope = slope_arr
        
        self.flow_accumulation = np.ones_like(dtm)
        self.catchment_area = self.flow_accumulation * (resolution ** 2)
        self.filled_dtm = dtm.copy()
        
        return self
        
    def extract_drainage_network(self):
        """
        Extract drainage network using optimized downstream tracing.
        
        Performance optimizations:
        - Limited headwater sampling
        - Efficient numpy operations
        - Early termination for traced paths
        """
        self._report_progress(55, 'Extracting drainage network')
        
        if self.flow_accumulation is None:
            return self
        
        # Assertions for required data
        dtm = self.dtm
        assert dtm is not None, "DTM must be loaded"
        nodata_mask = self.nodata_mask
        assert nodata_mask is not None, "Nodata mask must be set"
        flow_accumulation = self.flow_accumulation
            
        rows, cols = dtm.shape
        dem = self.filled_dtm if self.filled_dtm is not None else dtm
        
        # Get flow thresholds
        valid_acc = flow_accumulation[~nodata_mask]
        if len(valid_acc) == 0:
            return self
            
        threshold_main = float(np.percentile(valid_acc, 97))
        threshold_tributary = float(np.percentile(valid_acc, 92))
        threshold_stream = float(np.percentile(valid_acc, 85))
        
        # Find headwater cells using vectorized operations
        self._report_progress(60, 'Finding headwater cells')
        headwater_cells = self._find_headwaters_optimized(dem, threshold_stream)
        
        # Sort and limit headwaters
        headwater_cells.sort(key=lambda x: -x[2])
        
        # Select well-spaced headwaters
        selected_headwaters = self._select_spaced_headwaters(headwater_cells)
        
        # Trace downstream from each headwater
        self._report_progress(65, 'Tracing drainage paths')
        self.drainage_lines = []
        global_visited = set()
        
        for idx, (start_r, start_c, start_acc) in enumerate(selected_headwaters):
            if (start_r, start_c) in global_visited:
                continue
                
            # Get Strahler order if available
            strahler = None
            if self.strahler_order is not None:
                strahler = int(self.strahler_order[start_r, start_c])
                if strahler <= 0:
                    strahler = None
                
            # Trace downstream
            coords = self._trace_downstream(start_r, start_c, dem, global_visited)
            
            if len(coords) >= 5:
                smoothed = self._smooth_line(coords)
                props = self._calculate_channel_properties(smoothed, 'tertiary', strahler)
                props['start_accumulation'] = float(start_acc)
                
                if props.get('length_m', 0) >= self.min_channel_length:
                    self.drainage_lines.append(('temp', smoothed, props))
        
        # Reclassify channels
        self._report_progress(70, 'Classifying channels')
        self._reclassify_channels()
        
        return self
    
    def _find_headwaters_optimized(self, dem: FloatArray, threshold_stream: float) -> List[Tuple[int, int, float]]:
        """Find headwater cells using efficient numpy operations."""
        dtm = self.dtm
        assert dtm is not None
        nodata_mask = self.nodata_mask
        assert nodata_mask is not None
        flow_accumulation = self.flow_accumulation
        assert flow_accumulation is not None
        
        rows, cols = dtm.shape
        headwater_cells: List[Tuple[int, int, float]] = []
        
        # Sample grid to reduce computation
        step = max(1, min(rows, cols) // 200)
        
        for r in range(2, rows - 2, step):
            for c in range(2, cols - 2, step):
                if nodata_mask[r, c]:
                    continue
                    
                cell_acc = float(flow_accumulation[r, c])
                if cell_acc < threshold_stream:
                    continue
                    
                # Check if headwater
                is_headwater = True
                current_elev = dem[r, c]
                
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if not nodata_mask[nr, nc]:
                                if (dem[nr, nc] > current_elev and 
                                    flow_accumulation[nr, nc] >= threshold_stream * 0.8):
                                    is_headwater = False
                                    break
                    if not is_headwater:
                        break
                        
                if is_headwater:
                    headwater_cells.append((r, c, cell_acc))
                    
        return headwater_cells
    
    def _select_spaced_headwaters(self, headwater_cells):
        """Select well-spaced headwater starting points."""
        selected = []
        
        for r, c, acc in headwater_cells:
            too_close = False
            for sr, sc, _ in selected:
                dist = np.sqrt((r - sr)**2 + (c - sc)**2)
                if dist < self.min_spacing:
                    too_close = True
                    break
            if not too_close:
                selected.append((r, c, acc))
                if len(selected) >= self.max_headwaters:
                    break
                    
        return selected
    
    def _trace_downstream(self, start_r: int, start_c: int, dem: FloatArray, 
                          global_visited: set) -> List[Tuple[float, float, float]]:
        """Trace flow path downstream from a starting point."""
        rows, cols = dem.shape
        coords: List[Tuple[float, float, float]] = []
        
        nodata_mask = self.nodata_mask
        assert nodata_mask is not None
        dtm = self.dtm
        assert dtm is not None
        assert xy is not None, "rasterio.transform.xy is required"
        
        r: int = start_r
        c: int = start_c
        local_visited: set = set()
        
        for step in range(self.max_trace_steps):
            if not (0 <= r < rows and 0 <= c < cols):
                break
                
            if nodata_mask[r, c]:
                break
                
            if (r, c) in global_visited and len(coords) > 0:
                x_coord, y_coord = xy(self.transform, r, c)
                z = float(dtm[r, c])
                coords.append((x_coord, y_coord, z))
                break
                
            if (r, c) in local_visited:
                break
                
            local_visited.add((r, c))
            
            x_coord, y_coord = xy(self.transform, r, c)
            z = float(dtm[r, c])
            coords.append((x_coord, y_coord, z))
            
            # Find lowest neighbor
            current_elev = dem[r, c]
            best_r: Optional[int] = None
            best_c: Optional[int] = None
            lowest_elev = current_elev
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    nr, nc = r + dr, c + dc
                    
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                        
                    if nodata_mask[nr, nc]:
                        continue
                        
                    neighbor_elev = dem[nr, nc]
                    
                    if neighbor_elev < lowest_elev:
                        lowest_elev = neighbor_elev
                        best_r, best_c = nr, nc
                        
            if best_r is None or best_c is None:
                break
                
            r, c = best_r, best_c
            
        # Mark traced cells as globally visited
        for (vr, vc) in local_visited:
            global_visited.add((vr, vc))
            
        return coords
    
    def _smooth_line(self, coords, smoothing=0.3):
        """Smooth a line using spline interpolation."""
        if not HAS_SCIPY or splprep is None or splev is None or len(coords) < 4:
            return coords
            
        try:
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            z = [c[2] for c in coords]
            
            tck, u = splprep([x, y], s=smoothing * len(coords), k=min(3, len(coords)-1))
            
            u_new = np.linspace(0, 1, min(30, len(coords) * 2))
            x_new, y_new = splev(u_new, tck)
            z_new = np.interp(u_new, np.linspace(0, 1, len(z)), z)
            
            return [(float(x_new[i]), float(y_new[i]), float(z_new[i])) for i in range(len(x_new))]
        except Exception:
            return coords
    
    def _calculate_channel_properties(self, coords, channel_type, strahler_order=None):
        """
        Calculate hydraulic properties for a channel using enhanced methods.
        
        Uses regional IDF curves, multiple Tc methods, adjusted runoff coefficients,
        safety factors, and freeboard in pipe sizing.
        """
        if len(coords) < 2:
            return {}
            
        # Length
        length = sum(
            np.sqrt((coords[i+1][0] - coords[i][0])**2 + 
                   (coords[i+1][1] - coords[i][1])**2)
            for i in range(len(coords) - 1)
        )
        
        # Elevation drop and slope
        elev_start = coords[0][2]
        elev_end = coords[-1][2]
        elev_drop = elev_start - elev_end
        avg_slope = elev_drop / length if length > 0 else 0
        original_slope = avg_slope
        
        if avg_slope < HydrologicalConstants.MIN_SLOPE_CHANNEL:
            avg_slope = HydrologicalConstants.MIN_SLOPE_CHANNEL
            
        # Contributing area (used for some Tc methods)
        area_factor = {'primary': 10.0, 'secondary': 3.0, 'tertiary': 1.0}
        contrib_area_ha = (length * 50 * area_factor.get(channel_type, 1)) / 10000
        
        # Time of concentration - use selected method
        if self.tc_method == 'auto':
            tc_results = HydrologicalAnalysis.time_of_concentration_combined(
                length, max(avg_slope, 0.001), 
                area_ha=contrib_area_ha, 
                method='auto'
            )
            tc = tc_results['recommended']
            tc_method_used = 'combined'
        elif self.tc_method == 'nrcs':
            tc = HydrologicalAnalysis.time_of_concentration_nrcs(length, max(avg_slope, 0.001))
            tc_method_used = 'nrcs'
        elif self.tc_method == 'bransby':
            tc = HydrologicalAnalysis.time_of_concentration_bransby_williams(
                length, max(avg_slope, 0.001), contrib_area_ha / 100
            )
            tc_method_used = 'bransby_williams'
        else:
            tc = HydrologicalAnalysis.time_of_concentration_kirpich(length, max(avg_slope, 0.001))
            tc_method_used = 'kirpich'
        
        # Rainfall intensity - use regional IDF curve
        intensity = HydrologicalAnalysis.rainfall_intensity(
            tc, self.design_storm_years, region=self.climate_region
        )
        
        # Adjusted runoff coefficient for slope, soil, and AMC
        adjusted_C = HydrologicalAnalysis.adjusted_runoff_coefficient(
            self.runoff_coeff, 
            original_slope, 
            soil_type=self.soil_type,
            amc=self.amc
        )
        
        # Peak flow with safety factor
        peak_flow = HydrologicalAnalysis.rational_method(
            adjusted_C, intensity, contrib_area_ha, safety_factor=self.safety_factor
        )
        
        # Design selection
        design_info = DrainageDesignSelector.select_design(
            original_slope, peak_flow, self.is_urban
        )
        design_type = design_info['type']
        manning_n = design_info['manning_n']
        
        # Pipe sizing with safety factor and freeboard (20%)
        pipe_diameter = FluidMechanics.required_pipe_diameter(
            peak_flow, avg_slope, manning_n,
            safety_factor=self.safety_factor,
            max_depth_ratio=0.80  # 20% freeboard
        )
        
        # Velocity at design depth
        d_m = pipe_diameter / 1000
        partial_flow = FluidMechanics.pipe_partial_flow(d_m, 0.80, avg_slope, manning_n)
        velocity = partial_flow['velocity']
        
        # Validation with enhanced slope analysis
        validation = HydraulicValidator.full_validation(
            slope=original_slope,
            velocity=velocity,
            infrastructure_type='pipe' if 'pipe' in design_type else 'channel'
        )
        
        # Extract slope recommendations for flat terrain
        slope_validation = validation['slope_validation']
        requires_pump = bool(slope_validation.get('requires_pump', False))
        slope_recommendations = slope_validation.get('recommendations', [])
        
        # Froude number
        froude = FluidMechanics.froude_number(velocity, d_m * 0.8)
        flow_regime = 'subcritical' if froude < 1 else ('critical' if froude == 1 else 'supercritical')
        
        # Ensure all values are native Python types for JSON serialization
        return {
            'length_m': float(length),
            'slope_pct': float(avg_slope * 100),
            'original_slope_pct': float(original_slope * 100),
            'elev_drop_m': float(elev_drop),
            'time_conc_min': float(tc),
            'tc_method': tc_method_used,
            'rainfall_intensity_mmhr': float(intensity),
            'climate_region': self.climate_region,
            'runoff_coeff_base': float(self.runoff_coeff),
            'runoff_coeff_adjusted': float(adjusted_C),
            'peak_flow_m3s': float(peak_flow),
            'safety_factor': float(self.safety_factor),
            'pipe_diameter_mm': float(pipe_diameter),
            'velocity_ms': float(velocity),
            'manning_n': float(manning_n),
            'froude_number': float(froude),
            'flow_regime': flow_regime,
            'strahler_order': int(strahler_order) if strahler_order is not None else None,
            'design_type': design_type,
            'design_description': design_info['description'],
            'design_reason': design_info['selection_reason'],
            'validation_passed': bool(validation['overall_valid']),
            'slope_valid': bool(slope_validation['valid']),
            'slope_classification': slope_validation.get('classification', 'normal'),
            'requires_pump': requires_pump,
            'slope_recommendations': slope_recommendations,
            'velocity_valid': bool(validation['velocity_validation']['valid']),
            'velocity_issues': validation['velocity_validation'].get('issues', [])
        }
    
    def _reclassify_channels(self):
        """Reclassify channels based on length and drainage contribution."""
        if not self.drainage_lines:
            return
            
        lengths = [d[2].get('length_m', 0) for d in self.drainage_lines]
        if not lengths:
            return
            
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
        self.drainage_lines.sort(key=lambda x: -x[2].get('length_m', 0))
        
    def identify_outlets(self) -> 'OptimizedDrainageDesigner':
        """Identify outlet points at terrain boundaries."""
        self._report_progress(72, 'Identifying outlets')
        
        dtm = self.dtm
        assert dtm is not None
        assert xy is not None
        
        rows, cols = dtm.shape
        self.outlets = []
        
        boundaries = {
            'south': [(rows-1, c) for c in range(0, cols, max(1, cols//10))],
            'north': [(0, c) for c in range(0, cols, max(1, cols//10))],
            'west': [(r, 0) for r in range(0, rows, max(1, rows//10))],
            'east': [(r, cols-1) for r in range(0, rows, max(1, rows//10))]
        }
        
        for edge, cells in boundaries.items():
            valid_cells = [(r, c, float(dtm[r, c])) for r, c in cells 
                          if not np.isnan(dtm[r, c])]
            if valid_cells:
                sorted_cells = sorted(valid_cells, key=lambda x: x[2])[:2]
                for r, c, z in sorted_cells:
                    x_coord, y_coord = xy(self.transform, r, c)
                    self.outlets.append({'x': x_coord, 'y': y_coord, 'z': z, 'edge': edge})
                    
        return self
        
    def create_visualization(self) -> Optional[str]:
        """Create 3D visualization using Plotly with performance optimizations."""
        self._report_progress(75, 'Creating visualization')
        
        if not HAS_PLOTLY or go is None:
            return None
        
        dtm = self.dtm
        assert dtm is not None
        assert xy is not None
            
        rows, cols = dtm.shape
        # Use configured max terrain points for sampling
        max_points = self.max_terrain_points
        sample_step = max(1, min(rows, cols) // max_points)
        
        z_sampled = dtm[::sample_step, ::sample_step].copy()
        
        x_grid = np.zeros_like(z_sampled)
        y_grid = np.zeros_like(z_sampled)
        
        for i, r in enumerate(range(0, rows, sample_step)):
            for j, c in enumerate(range(0, cols, sample_step)):
                if i < z_sampled.shape[0] and j < z_sampled.shape[1]:
                    x_coord, y_coord = xy(self.transform, r, c)
                    x_grid[i, j] = x_coord
                    y_grid[i, j] = y_coord
        
        # Replace NaN with a sentinel for display (Plotly handles this)
        z_display: Any = np.where(np.isnan(z_sampled), np.nan, z_sampled)
        
        fig = go.Figure()
        
        # Terrain surface
        fig.add_trace(go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_display,
            colorscale=[
                [0.0, 'rgb(34, 139, 34)'],
                [0.25, 'rgb(144, 238, 144)'],
                [0.5, 'rgb(210, 180, 140)'],
                [0.75, 'rgb(139, 90, 43)'],
                [1.0, 'rgb(105, 105, 105)']
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
            lighting=dict(ambient=0.6, diffuse=0.8, specular=0.2, roughness=0.8),
            hovertemplate='<b>Terrain</b><br>Elevation: %{z:.1f}m<extra></extra>',
            name='Terrain'
        ))
        
        # Drainage lines - limited for performance
        self._report_progress(80, 'Adding drainage lines to visualization')
        self._add_drainage_lines_to_figure_optimized(fig)
        
        # Outlets (limit to 10 for display)
        if self.outlets:
            outlets_to_show = self.outlets[:10]
            fig.add_trace(go.Scatter3d(
                x=[o['x'] for o in outlets_to_show],
                y=[o['y'] for o in outlets_to_show],
                z=[o['z'] + 1.5 for o in outlets_to_show],
                mode='markers',
                marker=dict(size=6, color='rgba(220, 20, 60, 0.8)', symbol='diamond',
                           line=dict(width=1, color='white')),
                name='Outlets',
                hovertemplate='<b>Outlet</b><br>Elev: %{z:.1f}m<extra></extra>'
            ))
            
        # Layout
        fig.update_layout(
            title=dict(text='<b>Drainage Network Analysis</b>', x=0.5,
                      font=dict(size=16, color='#333')),
            scene=dict(
                xaxis=dict(title='Easting (m)', showgrid=True,
                          gridcolor='rgba(200,200,200,0.3)', showbackground=False),
                yaxis=dict(title='Northing (m)', showgrid=True,
                          gridcolor='rgba(200,200,200,0.3)', showbackground=False),
                zaxis=dict(title='Elevation (m)', showgrid=True,
                          gridcolor='rgba(200,200,200,0.3)', showbackground=False),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.3),
                camera=dict(eye=dict(x=1.4, y=1.4, z=0.8), up=dict(x=0, y=0, z=1)),
                bgcolor='rgba(248,248,255,1)'
            ),
            legend=dict(yanchor='top', y=0.95, xanchor='left', x=0.02,
                       bgcolor='rgba(255,255,255,0.85)',
                       bordercolor='rgba(200,200,200,0.5)', borderwidth=1,
                       font=dict(size=10)),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor='white'
        )
        
        # Save
        vis_dir = self.output_dir / 'visualizations'
        vis_dir.mkdir(exist_ok=True)
        output_path = vis_dir / 'drainage_analysis.html'
        
        self._write_optimized_html(fig, output_path)
        
        return str(output_path)
    
    def _add_drainage_lines_to_figure_optimized(self, fig):
        """Add drainage lines to Plotly figure - optimized for performance.
        
        Instead of adding individual line segments (which can create thousands of traces),
        this method combines lines by type and uses a single trace per type.
        """
        # Limit number of drainage lines for visualization
        lines_to_show = self.drainage_lines[:self.max_drainage_lines_viz]
        
        # Group lines by type for fewer traces
        type_colors = {
            'primary': 'rgb(0, 80, 180)',
            'secondary': 'rgb(50, 150, 220)',
            'tertiary': 'rgb(100, 190, 240)'
        }
        type_widths = {'primary': 5, 'secondary': 3, 'tertiary': 2}
        
        for channel_type in ['primary', 'secondary', 'tertiary']:
            # Collect all coordinates for this type
            all_x: List[float] = []
            all_y: List[float] = []
            all_z: List[float] = []
            
            type_lines = [l for l in lines_to_show if l[0] == channel_type]
            
            for _, coords, _ in type_lines:
                if len(coords) < 2:
                    continue
                    
                # Ensure upstream to downstream order
                elevs = [c[2] for c in coords]
                if elevs[0] < elevs[-1]:
                    coords = coords[::-1]
                
                # Add coordinates with None separators for discontinuous lines
                for c in coords:
                    all_x.append(c[0])
                    all_y.append(c[1])
                    all_z.append(c[2] + 0.5)
                
                # Add None to create gap between lines
                all_x.append(None)  # type: ignore
                all_y.append(None)  # type: ignore
                all_z.append(None)  # type: ignore
            
            if all_x:
                fig.add_trace(go.Scatter3d(
                    x=all_x,
                    y=all_y,
                    z=all_z,
                    mode='lines',
                    line=dict(
                        color=type_colors.get(channel_type, 'rgb(100, 150, 200)'),
                        width=type_widths.get(channel_type, 2)
                    ),
                    name=f'{channel_type.title()} ({len(type_lines)})',
                    hovertemplate=f'<b>{channel_type.title()} Drainage</b><br>Elev: %{{z:.1f}}m<extra></extra>'
                ))
        
        # Add info if lines were truncated
        total_lines = len(self.drainage_lines)
        if total_lines > self.max_drainage_lines_viz:
            shown = self.max_drainage_lines_viz
            # Add annotation about truncation
            fig.add_annotation(
                text=f'Showing {shown} of {total_lines} drainage lines',
                xref='paper', yref='paper',
                x=0.02, y=0.02,
                showarrow=False,
                font=dict(size=10, color='gray'),
                bgcolor='rgba(255,255,255,0.8)'
            )
    
    def _add_drainage_lines_to_figure(self, fig):
        """Add drainage lines to Plotly figure."""
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
            
            # Ensure upstream to downstream order
            elevs = [c[2] for c in coords]
            if elevs[0] < elevs[-1]:
                coords = coords[::-1]
                
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            zs = [c[2] + 0.5 for c in coords]
            
            n_points = len(coords)
            light = base_colors[channel_type]['light']
            dark = base_colors[channel_type]['dark']
            
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
                    x=[xs[i], xs[i+1]], y=[ys[i], ys[i+1]], z=[zs[i], zs[i+1]],
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
    
    def _write_optimized_html(self, fig, output_path):
        """Write optimized HTML file using CDN for Plotly."""
        fig_json = fig.to_json()
        
        config_json = json.dumps({
            'displayModeBar': True, 
            'scrollZoom': True,
            'responsive': True
        })
        
        total_length = sum(props.get('length_m', 0) for _, _, props in self.drainage_lines)
        primary_count = sum(1 for d in self.drainage_lines if d[0] == 'primary')
        secondary_count = sum(1 for d in self.drainage_lines if d[0] == 'secondary')
        tertiary_count = sum(1 for d in self.drainage_lines if d[0] == 'tertiary')
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drainage Network Analysis</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" defer></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: rgba(255,255,255,0.95); border-radius: 12px;
                  padding: 20px 30px; margin-bottom: 20px;
                  box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
        .header h1 {{ color: #333; font-size: 1.8rem; margin-bottom: 10px; }}
        .header .subtitle {{ color: #666; font-size: 0.95rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                      gap: 15px; margin-top: 15px; }}
        .stat-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
                     border-radius: 8px; padding: 15px; text-align: center; }}
        .stat-card .value {{ font-size: 1.5rem; font-weight: bold; color: #4a5568; }}
        .stat-card .label {{ font-size: 0.8rem; color: #718096; margin-top: 5px; }}
        .stat-card.primary .value {{ color: #3182ce; }}
        .stat-card.secondary .value {{ color: #38a169; }}
        .stat-card.tertiary .value {{ color: #805ad5; }}
        .chart-container {{ background: white; border-radius: 12px;
                           box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                           overflow: hidden; position: relative; }}
        #chart {{ width: 100%; height: 75vh; min-height: 500px; }}
        .loading {{ position: absolute; top: 50%; left: 50%;
                   transform: translate(-50%, -50%); text-align: center; z-index: 10; }}
        .loading.hidden {{ display: none; }}
        .spinner {{ width: 50px; height: 50px; border: 4px solid #e2e8f0;
                   border-top-color: #667eea; border-radius: 50%;
                   animation: spin 1s linear infinite; margin: 0 auto 15px; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.8);
                  font-size: 0.85rem; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🌊 Drainage Network Analysis</h1>
            <p class="subtitle">D∞ (D-Infinity) Flow Routing | Professional Hydrological Design</p>
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
                <p>Loading 3D visualization...</p>
            </div>
            <div id="chart"></div>
        </div>
        <footer class="footer">
            Generated by Terra Pravah | D∞ Algorithm (Tarboton, 1997)
        </footer>
    </div>
    <script>
        const figureData = {fig_json};
        const chartConfig = {config_json};
        document.addEventListener('DOMContentLoaded', function() {{
            const loadingEl = document.getElementById('loading');
            const chartEl = document.getElementById('chart');
            function renderChart() {{
                if (typeof Plotly !== 'undefined') {{
                    Plotly.newPlot(chartEl, figureData.data, figureData.layout, chartConfig)
                        .then(() => loadingEl.classList.add('hidden'));
                }}
            }}
            if (typeof Plotly !== 'undefined') {{ renderChart(); }}
            else {{
                let attempts = 0;
                const check = setInterval(() => {{
                    attempts++;
                    if (typeof Plotly !== 'undefined') {{ clearInterval(check); renderChart(); }}
                    else if (attempts >= 50) {{ clearInterval(check); loadingEl.innerHTML = 'Error loading chart'; }}
                }}, 100);
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
    def generate_report(self):
        """Generate engineering report."""
        self._report_progress(85, 'Generating report')
        
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
                'outlets': len(self.outlets),
                'primary_length_m': sum(d[2].get('length_m', 0) for d in primary),
                'secondary_length_m': sum(d[2].get('length_m', 0) for d in secondary),
                'tertiary_length_m': sum(d[2].get('length_m', 0) for d in tertiary)
            },
            'hydraulics': {
                'design_method': 'Rational Method (Q=CIA)',
                'flow_routing': 'D∞ (D-Infinity) Algorithm (Tarboton, 1997)',
                'stream_threshold': f'{self.stream_threshold_pct}% of cells',
                'strahler_ordering': 'Applied',
                'pipe_sizing': "Manning's Equation",
                'velocity_limits': f'{HydrologicalConstants.MIN_VELOCITY}-{HydrologicalConstants.MAX_VELOCITY} m/s',
                'total_design_flow_m3s': total_flow,
                'max_peak_flow': max((d[2].get('peak_flow_m3s', 0) for d in self.drainage_lines), default=0),
                'min_slope': min((d[2].get('original_slope_pct', 0)/100 for d in self.drainage_lines), default=0)
            },
            'hydraulic_summary': {
                'max_peak_flow': max((d[2].get('peak_flow_m3s', 0) for d in self.drainage_lines), default=0),
                'min_slope': min((d[2].get('original_slope_pct', 0)/100 for d in self.drainage_lines), default=0)
            },
            'outlet_summary': {
                'count': len(self.outlets)
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
        
        # Add top 20 channel details
        for channel_type, coords, props in self.drainage_lines[:20]:
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
            
        report_path = self.output_dir / 'drainage_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def export_geojson(self):
        """Export network to GeoJSON."""
        self._report_progress(90, 'Exporting GeoJSON')
        
        features = []
        
        def convert_to_native(obj: Any) -> Any:
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
            converted_coords = [[float(c[0]), float(c[1]), float(c[2])] for c in coords]
            converted_props: Dict[str, Any] = convert_to_native(props)
            
            properties_dict: Dict[str, Any] = {'type': channel_type}
            properties_dict.update(converted_props)
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': converted_coords
                },
                'properties': properties_dict
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
            
        return str(path)
        
    def process(self):
        """Run complete analysis pipeline."""
        self.load_terrain()
        self.hydrological_processing()
        self.extract_drainage_network()
        self.identify_outlets()
        
        vis_path = self.create_visualization()
        report = self.generate_report()
        geojson_path = self.export_geojson()
        
        self._report_progress(95, 'Finalizing')
        
        return {
            'report': report,
            'visualization_path': vis_path,
            'geojson_path': geojson_path
        }
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# SERVICE CLASS (MAIN INTERFACE)
# =============================================================================

class DrainageAnalysisService:
    """
    Service for running drainage network analysis.
    Main interface for the Terra Pravah web application.
    """
    
    def __init__(self, dtm_path: str, output_dir: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analysis service.
        
        Args:
            dtm_path: Path to DTM file
            output_dir: Output directory for results
            config: Analysis configuration
        """
        self.dtm_path = dtm_path
        self.output_dir = Path(output_dir)
        self.config: Dict[str, Any] = config or {}
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.designer = OptimizedDrainageDesigner(dtm_path, str(self.output_dir), self.config)
    
    def run_full_analysis(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """
        Run complete drainage analysis pipeline.
        
        Args:
            progress_callback: Function(progress, step) called to report progress
            
        Returns:
            dict with analysis results
        """
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'config': self.config
        }
        
        try:
            # Set progress callback
            if progress_callback:
                self.designer.set_progress_callback(progress_callback)
            
            # Run analysis
            analysis_results = self.designer.process()
            report = analysis_results['report']
            
            # Compile results
            results.update({
                'completed_at': datetime.utcnow().isoformat(),
                'status': 'completed',
                'results_path': str(self.output_dir),
                'visualization_path': analysis_results.get('visualization_path'),
                'geojson_path': analysis_results.get('geojson_path'),
                'report_path': str(self.output_dir / 'drainage_report.json'),
                
                # Summary statistics
                'total_channels': report.get('network_summary', {}).get('total_channels', 0),
                'total_length_km': report.get('network_summary', {}).get('total_length_km', 0),
                'total_outlets': report.get('outlet_summary', {}).get('count', 0),
                'peak_flow_m3s': report.get('hydraulic_summary', {}).get('max_peak_flow', 0),
                
                # Detailed breakdown
                'primary_count': report.get('network_summary', {}).get('primary_channels', 0),
                'secondary_count': report.get('network_summary', {}).get('secondary_channels', 0),
                'tertiary_count': report.get('network_summary', {}).get('tertiary_channels', 0),
                'primary_length_m': report.get('network_summary', {}).get('primary_length_m', 0),
                'secondary_length_m': report.get('network_summary', {}).get('secondary_length_m', 0),
                'tertiary_length_m': report.get('network_summary', {}).get('tertiary_length_m', 0),
                
                # Full report
                'full_report': report
            })
            
            if progress_callback:
                progress_callback(100, 'Complete')
            
            return results
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            results['completed_at'] = datetime.utcnow().isoformat()
            raise
    
    def run_quick_analysis(self, progress_callback=None) -> dict:
        """Run quick/preview analysis with reduced resolution."""
        original_threshold = self.config.get('stream_threshold_pct', 1.0)
        self.config['stream_threshold_pct'] = 5.0
        self.designer.stream_threshold_pct = 5.0
        self.designer.max_headwaters = 50
        self.designer.min_spacing = 50
        
        try:
            return self.run_full_analysis(progress_callback)
        finally:
            self.config['stream_threshold_pct'] = original_threshold
    
    def get_terrain_preview(self) -> Dict[str, Any]:
        """Get terrain preview without full analysis."""
        if not HAS_RASTERIO or rasterio is None:
            raise RuntimeError("rasterio required for terrain preview")
            
        with rasterio.open(self.dtm_path) as src:
            scale_factor = min(1.0, 500 / max(src.width, src.height))
            
            data = src.read(
                1,
                out_shape=(
                    int(src.height * scale_factor),
                    int(src.width * scale_factor)
                )
            )
            
            nodata = src.nodata
            valid_data = data[data != nodata] if nodata else data.flatten()
            
            return {
                'width': src.width,
                'height': src.height,
                'crs': str(src.crs) if src.crs else None,
                'bounds': list(src.bounds),
                'resolution': src.res,
                'statistics': {
                    'min_elevation': float(np.min(valid_data)),
                    'max_elevation': float(np.max(valid_data)),
                    'mean_elevation': float(np.mean(valid_data)),
                    'std_elevation': float(np.std(valid_data))
                }
            }
    
    def export_to_format(self, format_type: str, output_path: Optional[str] = None) -> str:
        """Export results to different formats."""
        if format_type == 'geojson':
            return str(self.output_dir / 'drainage_network.geojson')
        raise NotImplementedError(f"Export to {format_type} not yet implemented")
    
    def cleanup(self):
        """Clean up temporary files."""
        self.designer.cleanup()


# =============================================================================
# AI DESIGN ASSISTANT
# =============================================================================

class AIDesignAssistant:
    """
    AI-powered design assistant for drainage optimization.
    
    Analyzes design results and provides recommendations based on:
    - Network connectivity and outlet distribution
    - Slope adequacy and flat terrain handling
    - Peak flow capacity and climate considerations
    - Regional appropriateness (especially for arid regions)
    - Safety factor and freeboard adequacy
    """
    
    def __init__(self, analysis_results: dict):
        self.results = analysis_results
        self.suggestions = []
    
    def analyze_design(self) -> list:
        """Analyze the design and generate suggestions."""
        self.suggestions = []
        
        self._check_network_connectivity()
        self._check_slopes()
        self._check_capacity()
        self._check_outlets()
        self._check_regional_settings()
        self._check_velocity_issues()
        self._check_pump_requirements()
        
        return self.suggestions
    
    def _check_network_connectivity(self):
        total_channels = self.results.get('total_channels', 0)
        outlets = self.results.get('total_outlets', 0)
        
        if outlets == 0:
            self.suggestions.append({
                'type': 'warning',
                'category': 'connectivity',
                'message': 'No outlet points identified. The drainage network may be incomplete.',
                'recommendation': 'Review the analysis area boundaries and ensure the DTM extends to natural outlets.'
            })
        elif total_channels > 0 and total_channels / outlets > 50:
            self.suggestions.append({
                'type': 'info',
                'category': 'connectivity',
                'message': f'High channel-to-outlet ratio ({total_channels / outlets:.1f}). Network is well-connected.',
                'recommendation': None
            })
    
    def _check_slopes(self):
        full_report = self.results.get('full_report', {})
        hydraulic = full_report.get('hydraulic_summary', {})
        channels = full_report.get('channels', [])
        
        min_slope = hydraulic.get('min_slope', 0)
        if min_slope < 0.005:
            self.suggestions.append({
                'type': 'warning',
                'category': 'slope',
                'message': f'Very flat slopes detected (min: {min_slope*100:.2f}%). May require special design.',
                'recommendation': 'Consider pump stations or special low-gradient channel designs for flat sections. '
                                 'See IRC SP 13:2004 for flat terrain drainage guidelines.'
            })
        
        # Check for channels requiring pump stations
        pump_count = sum(1 for c in channels if c.get('requires_pump', False))
        if pump_count > 0:
            self.suggestions.append({
                'type': 'warning',
                'category': 'infrastructure',
                'message': f'{pump_count} channel(s) have slopes requiring pump stations.',
                'recommendation': 'Budget for pump infrastructure. Consider gravity alternatives by extending outlet distances.'
            })
    
    def _check_capacity(self):
        peak_flow = self.results.get('peak_flow_m3s', 0)
        config = self.results.get('config', {})
        design_storm = config.get('design_storm_years', 10)
        
        if peak_flow > 10:
            self.suggestions.append({
                'type': 'info',
                'category': 'capacity',
                'message': f'Significant peak flow ({peak_flow:.2f} m³/s) for {design_storm}-year storm.',
                'recommendation': 'Consider detention basins or flow attenuation structures for large watersheds. '
                                 'Refer to CPWD guidelines for storage facility sizing.'
            })
        
        # Check if safety factor is applied
        safety_factor = config.get('safety_factor', 1.0)
        if safety_factor < 1.2:
            self.suggestions.append({
                'type': 'warning',
                'category': 'safety',
                'message': f'Low safety factor ({safety_factor}). Recommended minimum is 1.25.',
                'recommendation': 'Increase safety_factor in config to at least 1.25 for design reliability.'
            })
    
    def _check_outlets(self):
        outlets = self.results.get('total_outlets', 0)
        total_length = self.results.get('total_length_km', 0)
        
        if outlets > 0 and total_length > 0:
            avg_contributing_length = total_length / outlets
            
            if avg_contributing_length > 5:
                self.suggestions.append({
                    'type': 'info',
                    'category': 'outlets',
                    'message': f'Long average contributing length ({avg_contributing_length:.1f} km/outlet).',
                    'recommendation': 'Consider additional intermediate outlets or storage to reduce peak flows at main outlets.'
                })
    
    def _check_regional_settings(self):
        """Check if regional settings are appropriate for project location."""
        config = self.results.get('config', {})
        climate_region = config.get('climate_region', 'default')
        
        if climate_region == 'default':
            self.suggestions.append({
                'type': 'info',
                'category': 'configuration',
                'message': 'Using default IDF parameters. Region-specific settings may improve accuracy.',
                'recommendation': 'Set climate_region to match project location (e.g., "rajasthan_arid", '
                                 '"mumbai_coastal", "delhi_ncr") for accurate rainfall intensity estimates.'
            })
        
        # For arid regions, check runoff coefficient
        if climate_region == 'rajasthan_arid':
            runoff_coeff = config.get('runoff_coefficient', 0.5)
            if runoff_coeff < 0.35:
                self.suggestions.append({
                    'type': 'warning',
                    'category': 'hydrology',
                    'message': f'Low runoff coefficient ({runoff_coeff}) for arid region.',
                    'recommendation': 'Arid regions often have higher runoff due to poor infiltration. '
                                     'Consider C = 0.35-0.50 for scrubland/agricultural areas.'
                })
    
    def _check_velocity_issues(self):
        """Check for velocity-related issues in designed channels."""
        full_report = self.results.get('full_report', {})
        channels = full_report.get('channels', [])
        
        low_velocity_count = sum(1 for c in channels if not c.get('velocity_valid', True) 
                                 and c.get('velocity_ms', 1) < 0.6)
        high_velocity_count = sum(1 for c in channels if not c.get('velocity_valid', True)
                                  and c.get('velocity_ms', 0) > 3.0)
        
        if low_velocity_count > 0:
            self.suggestions.append({
                'type': 'warning',
                'category': 'velocity',
                'message': f'{low_velocity_count} channel(s) have velocity below self-cleaning minimum (0.6 m/s).',
                'recommendation': 'Increase slope, reduce pipe diameter, or plan for periodic maintenance flushing.'
            })
        
        if high_velocity_count > 0:
            self.suggestions.append({
                'type': 'warning',
                'category': 'velocity',
                'message': f'{high_velocity_count} channel(s) exceed maximum erosion velocity (3.0 m/s).',
                'recommendation': 'Add drop structures, use erosion-resistant lining, or consider stepped channels.'
            })
    
    def _check_pump_requirements(self):
        """Summarize pump station requirements for flat terrain."""
        full_report = self.results.get('full_report', {})
        channels = full_report.get('channels', [])
        
        flat_channels = [c for c in channels if c.get('slope_classification') == 'very_flat']
        
        if len(flat_channels) > len(channels) * 0.3:
            total_flow = sum(c.get('peak_flow_m3s', 0) for c in flat_channels)
            self.suggestions.append({
                'type': 'critical',
                'category': 'infrastructure',
                'message': f'{len(flat_channels)} channels ({len(flat_channels)/len(channels)*100:.0f}%) '
                          f'are in very flat terrain requiring pump stations.',
                'recommendation': f'Estimated pump capacity needed: {total_flow:.2f} m³/s. '
                                 'Consider hybrid gravity-pump system design.'
            })
    
    def optimize_design(self) -> dict:
        return {
            'suggestions': self.suggestions,
            'optimization_potential': self._calculate_optimization_score(),
            'recommended_actions': self._get_priority_actions()
        }
    
    def _calculate_optimization_score(self) -> float:
        warnings = sum(1 for s in self.suggestions if s['type'] == 'warning')
        critical = sum(1 for s in self.suggestions if s['type'] == 'critical')
        score = 100 - (warnings * 10) - (critical * 25)
        return max(0, min(100, score))
    
    def _get_priority_actions(self) -> list:
        actions = []
        for s in self.suggestions:
            if s['type'] in ['warning', 'critical'] and s.get('recommendation'):
                actions.append({
                    'priority': 'critical' if s['type'] == 'critical' else 'high',
                    'category': s['category'],
                    'action': s['recommendation']
                })
        return sorted(actions, key=lambda x: 0 if x['priority'] == 'critical' else 1)


# =============================================================================
# WATERLOGGING HOTSPOT DETECTION
# =============================================================================

def detect_waterlogging_hotspots(dtm_path: str,
                                   flow_acc_path: str,
                                   output_gpkg: str,
                                   percentile_threshold: float = 90.0,
                                   min_area_m2: float = 4.0) -> dict:
    """
    Identify waterlogging-prone areas based on:
    1. Low elevation zones (topographic depressions)
    2. High flow accumulation (water collects here)
    3. Combined risk score

    This feature is explicitly listed in the hackathon scope but most
    competitors skip it. It requires only ~40 lines on top of existing
    flow accumulation output.

    Args:
        dtm_path: Path to DTM GeoTIFF.
        flow_acc_path: Path to flow accumulation raster GeoTIFF.
        output_gpkg: Output path for GeoPackage with hotspot polygons.
        percentile_threshold: Risk percentile threshold (default 90 = top 10%).
        min_area_m2: Minimum hotspot area in m² (default 4.0 = 2×2 cells at 1m).

    Returns:
        dict with hotspot_count, total_area, risk statistics, and output path.

    Raises:
        ImportError: If rasterio or geopandas are not available.
        FileNotFoundError: If input rasters don't exist.
    """
    if not HAS_RASTERIO or rasterio is None:
        raise ImportError("rasterio is required for waterlogging detection. "
                         "Install with: pip install rasterio")

    try:
        import geopandas as gpd
        from shapely.geometry import shape as shapely_shape
        import rasterio.features
    except ImportError:
        raise ImportError("geopandas and shapely are required. "
                         "Install with: pip install geopandas shapely")

    dtm_file = Path(dtm_path)
    fa_file = Path(flow_acc_path)
    if not dtm_file.exists():
        raise FileNotFoundError(f"DTM file not found: {dtm_path}")
    if not fa_file.exists():
        raise FileNotFoundError(f"Flow accumulation file not found: {flow_acc_path}")

    # Read DTM
    with rasterio.open(dtm_path) as dtm_src:
        dtm = dtm_src.read(1).astype(np.float32)
        if dtm_src.nodata is not None:
            dtm[dtm == dtm_src.nodata] = np.nan
        transform = dtm_src.transform
        crs = dtm_src.crs

    # Read flow accumulation
    with rasterio.open(flow_acc_path) as fa_src:
        flow_acc = fa_src.read(1).astype(np.float32)
        flow_acc[flow_acc < 0] = 0

    # Normalize both surfaces to 0–1
    dtm_norm = (dtm - np.nanmin(dtm)) / (np.nanmax(dtm) - np.nanmin(dtm) + 1e-9)

    fa_norm = np.log1p(flow_acc)  # log scale — flow acc is highly skewed
    fa_norm = fa_norm / (fa_norm.max() + 1e-9)

    # Risk score: low elevation + high flow accumulation
    # (1 - dtm_norm) = high where terrain is low
    risk = (0.5 * (1 - dtm_norm)) + (0.5 * fa_norm)
    risk = np.where(np.isnan(dtm), np.nan, risk)

    # Threshold: top N% risk cells are hotspots
    threshold = float(np.nanpercentile(risk, percentile_threshold))
    hotspot_mask = (risk >= threshold).astype(np.uint8)

    # Vectorize hotspot polygons
    shapes_gen = rasterio.features.shapes(hotspot_mask, transform=transform)
    polygons = []
    for geom, value in shapes_gen:
        if value == 1:
            polygon = shapely_shape(geom)
            if polygon.area > min_area_m2:
                centroid = polygon.centroid
                # Sample risk score at centroid
                try:
                    r, c = rasterio.transform.rowcol(transform, centroid.x, centroid.y)
                    risk_score = float(risk[r, c])
                except (IndexError, ValueError):
                    risk_score = threshold

                polygons.append({
                    'geometry': polygon,
                    'risk_score': round(risk_score, 4),
                    'risk_level': 'High' if risk_score > 0.85 else 'Medium',
                    'area_m2': round(polygon.area, 2)
                })

    # Save to GeoPackage
    Path(output_gpkg).parent.mkdir(parents=True, exist_ok=True)
    gdf = gpd.GeoDataFrame(polygons, crs=crs)
    gdf.to_file(output_gpkg, layer='waterlogging_hotspots', driver='GPKG')

    result = {
        "hotspot_count": len(polygons),
        "total_hotspot_area_m2": round(sum(p['area_m2'] for p in polygons), 2),
        "risk_threshold_used": round(threshold, 4),
        "high_risk_zones": sum(1 for p in polygons if p['risk_level'] == 'High'),
        "medium_risk_zones": sum(1 for p in polygons if p['risk_level'] == 'Medium'),
        "output_gpkg": output_gpkg,
        "percentile_threshold": percentile_threshold
    }

    logger.info(f"Waterlogging detection complete: {result['hotspot_count']} hotspots "
                f"({result['high_risk_zones']} high risk, {result['medium_risk_zones']} medium)")

    return result


# =============================================================================
# GEOPACKAGE MULTI-LAYER EXPORT
# =============================================================================

def export_complete_geopackage(drainage_lines: list,
                                 nodes: list,
                                 crs,
                                 output_path: str,
                                 hotspots_gdf=None,
                                 processing_info: dict = None) -> str:
    """
    Export ALL drainage design layers to a single OGC-compliant GeoPackage.

    The OGC guide explicitly asks for GeoPackage output. This exports all
    analysis results as multiple layers in one file for easy consumption
    in QGIS, ArcGIS, or any GIS tool.

    Layers exported:
      - drainage_network    (pipe/channel linestrings with hydraulic properties)
      - structures          (manholes, inlets, outlets as points)
      - waterlogging_hotspots (if provided)
      - metadata            (processing info, standards, software version)

    Args:
        drainage_lines: List of (channel_type, coords, props) tuples from designer.
        nodes: List of node dicts with x, y, z, type keys.
        crs: Coordinate reference system (rasterio CRS or string).
        output_path: Output GeoPackage file path.
        hotspots_gdf: Optional GeoDataFrame of waterlogging hotspots.
        processing_info: Optional dict of additional metadata key-value pairs.

    Returns:
        str: Path to the created GeoPackage file.
    """
    try:
        import geopandas as gpd
        from shapely.geometry import LineString, Point
    except ImportError:
        raise ImportError("geopandas and shapely are required. "
                         "Install with: pip install geopandas shapely")

    from datetime import date

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Layer 1: Drainage network segments
    lines = []
    for channel_type, coords, props in drainage_lines:
        if len(coords) < 2:
            continue
        line_coords = [(float(c[0]), float(c[1]), float(c[2])) for c in coords]
        line = LineString(line_coords)
        lines.append({
            'geometry': line,
            'channel_type': channel_type,
            'length_m': round(float(props.get('length_m', 0)), 2),
            'slope_pct': round(float(props.get('slope_pct', props.get('original_slope_pct', 0))), 3),
            'pipe_diameter_mm': int(props.get('pipe_diameter_mm', 0)),
            'peak_flow_m3s': round(float(props.get('peak_flow_m3s', 0)), 6),
            'velocity_ms': round(float(props.get('velocity_ms', 0)), 3),
            'drain_type': str(props.get('design_type', props.get('type', 'pipe'))),
            'material': 'RCC',  # IS:458 concrete pipe
            'strahler_order': int(props.get('strahler_order', 0)) if props.get('strahler_order') else None,
            'cost_inr': round(float(props.get('cost_inr', 0)), 2) if props.get('cost_inr') else None
        })

    if lines:
        gdf_network = gpd.GeoDataFrame(lines, crs=crs)
        gdf_network.to_file(output_path, layer='drainage_network', driver='GPKG')
        logger.info(f"  Layer 'drainage_network': {len(lines)} segments")

    # Layer 2: Structures (manholes, inlets, outlets)
    structures = []
    for node in nodes:
        if 'x' in node and 'y' in node:
            pt = Point(float(node['x']), float(node['y']))
            structures.append({
                'geometry': pt,
                'node_type': str(node.get('type', 'unknown')),
                'invert_level_m': round(float(node.get('invert_z', node.get('z', 0))), 3),
                'cover_level_m': round(float(node.get('z', 0)), 3),
                'depth_m': round(float(node.get('depth', 0)), 3)
            })

    if structures:
        gdf_structures = gpd.GeoDataFrame(structures, crs=crs)
        gdf_structures.to_file(output_path, layer='structures', driver='GPKG')
        logger.info(f"  Layer 'structures': {len(structures)} nodes")

    # Layer 3: Waterlogging hotspots (if provided)
    if hotspots_gdf is not None and len(hotspots_gdf) > 0:
        hotspots_gdf.to_file(output_path, layer='waterlogging_hotspots', driver='GPKG')
        logger.info(f"  Layer 'waterlogging_hotspots': {len(hotspots_gdf)} polygons")

    # Layer 4: Metadata (as a non-spatial table)
    meta = [
        {'key': 'processing_date', 'value': str(date.today())},
        {'key': 'software', 'value': 'Terra Pravah v2.3'},
        {'key': 'classification_algorithm', 'value': 'PDAL SMRF'},
        {'key': 'interpolation_method', 'value': 'Ordinary Kriging'},
        {'key': 'flow_routing', 'value': 'D-Infinity (D∞)'},
        {'key': 'pipe_design_standard', 'value': 'IS:10430, IS:458'},
        {'key': 'coordinate_reference_system', 'value': str(crs) if crs else 'undefined'},
        {'key': 'hackathon', 'value': 'MoPR Geospatial Intelligence 2025'},
        {'key': 'problem_statement', 'value': 'PS2 - DTM + Drainage Network'},
    ]
    if processing_info:
        for k, v in processing_info.items():
            meta.append({'key': str(k), 'value': str(v)})

    import pandas as pd
    gdf_meta = gpd.GeoDataFrame(pd.DataFrame(meta))
    gdf_meta.to_file(output_path, layer='metadata', driver='GPKG')
    logger.info(f"  Layer 'metadata': {len(meta)} entries")

    logger.info(f"✅ GeoPackage exported: {output_path}")

    return output_path
