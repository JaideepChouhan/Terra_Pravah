# 🌊 Terra Pravah - AI-Powered Drainage Network Design System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WhiteboxTools](https://img.shields.io/badge/WhiteboxTools-2.1+-green.svg)](https://www.whiteboxgeo.com/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

A comprehensive automated drainage network design system that leverages **Digital Terrain Models (DTM)**, advanced hydrological analysis, and fluid mechanics principles to create optimized drainage networks. Built with WhiteboxTools and professional geospatial libraries for accurate, engineering-grade results.

> 📖 **New to Terra Pravah?** Check out the [User Guide](USER_GUIDE.md) for step-by-step instructions.

**Latest Release (v2.3 - Production Ready):**
- **Complete Web Application** - Full-stack React + Flask application
- **Docker Deployment** - One-command production deployment
- **Team Collaboration** - Create teams, invite members, share projects
- **Professional Reports** - Multiple report templates with PDF/HTML export
- **Billing Integration** - Subscription plans with INR pricing

**v2.2 - Regional Hydrology & Safety Enhancements:** 
- **Regional IDF Curves for India** - Climate-specific rainfall intensity (Rajasthan, Mumbai, Delhi, etc.)
- **Multiple Time of Concentration Methods** - Kirpich, NRCS, Bransby-Williams, or auto-combined
- **Adjusted Runoff Coefficients** - Slope, soil type, and antecedent moisture corrections
- **Safety Factors & Freeboard** - 25% capacity safety factor and 20% freeboard in pipe sizing
- **Enhanced Flat Terrain Handling** - Automatic pump station recommendations for < 0.5% slopes
- **AI Design Assistant Improvements** - Regional recommendations and velocity validation

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [User Guide](#-user-guide)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Hydrological Methods](#-hydrological-methods)
- [Outputs](#-outputs)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Testing](#-running-tests)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [References](#-references)
- [License](#-license)

---

## 🎯 Overview

This system automates the complete drainage network design workflow, from terrain analysis to final engineering outputs. It combines:

- **Hydrological Analysis**: D8/D-infinity (D∞) flow routing, watershed delineation
- **Fluid Mechanics**: Manning's equation, Hazen-Williams formula, Froude number analysis
- **Peak Flow Estimation**: Rational Method (Q=CIA), SCS Curve Number method
- **Pipe Sizing**: Automated selection from standard pipe diameters
- **3D Visualization**: Interactive Plotly-based terrain and network visualization
- **AI Design Assistant**: Automated design recommendations and optimization suggestions
- **Web Application**: Modern React frontend with real-time analysis updates
- **Team Collaboration**: Share projects and collaborate with team members

### Use Cases

- 🏘️ Village/rural drainage planning
- 🌾 Agricultural land drainage
- 🏗️ Urban stormwater management
- 🛣️ Road drainage design
- 🌍 Watershed analysis and management

---

## ✨ Key Features

### Hydrological Processing
- **Automated DEM conditioning** - Breach/fill depressions for proper flow routing
- **D8 Flow Direction (Default)** - Fast, industry-standard single-direction flow routing
- **D-Infinity Flow Direction** - Optional multi-direction flow for higher accuracy
- **Flow Accumulation** - Specific contributing area calculations
- **Stream Network Extraction** - Threshold-based channel identification

### Engineering Design
- **Universal, Slope-Adaptive Design** - Automatically selects drain types based on terrain slope
- **Manning's Equation** - Open channel flow velocity and capacity calculations
- **Rational Method** - Peak runoff estimation (Q = C × I × A)
- **Time of Concentration** - Kirpich formula for travel time
- **Automatic Pipe Sizing** - Selection from standard diameters (150mm - 1200mm)

### Visualization & Output
- **Interactive 3D Visualization** - Plotly-based terrain with drainage overlay
- **Performance Optimized** - Configurable terrain sampling (80 points) and drainage line limits (50 lines)
- **Flow Direction Indicators** - Gradient coloring showing upstream to downstream flow
- **Multiple Export Formats** - GeoJSON, GeoPackage, Shapefiles, JSON reports
- **Engineering Reports** - Complete design documentation with multiple templates

### Advanced Features
- **Configurable Parameters** - JSON-based configuration with sensible defaults
- **Comprehensive Validation** - Hydraulic continuity, capacity checks, slope validation
- **Fallback Processing** - scipy-based hydrology when WhiteboxTools unavailable
- **Performance Optimized** - Embedded algorithms with configurable limits to prevent timeouts
- **Strahler Stream Ordering** - Hierarchical stream classification

---

## 🏗️ Architecture

### Backend Services Architecture

```
backend/services/
├── drainage_service.py           # Main drainage analysis (D∞ embedded)
├── visualization_service.py      # 3D visualization generation
└── email_service.py              # Notification service

drainage_service.py Classes:
├── HydrologicalConstants         # Standard coefficients and thresholds
├── DrainageDesignSelector        # Slope-based design selection
├── HydraulicValidator            # Velocity, slope, continuity checks
├── FluidMechanics                # Manning's equation, pipe sizing
├── HydrologicalAnalysis          # Rational method, Kirpich formula
├── OptimizedDrainageDesigner     # Main processing engine (D∞)
├── DrainageAnalysisService       # Web API interface
└── AIDesignAssistant             # Design optimization suggestions
```

### Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Digital Terrain Model                  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  HYDROLOGICAL PROCESSING                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   DEM       │  │    Flow     │  │    Flow     │              │
│  │ Conditioning│──│  Direction  │──│Accumulation │              │
│  │  (Breach)   │  │    (D8)     │  │    (SCA)    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   NETWORK EXTRACTION                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Headwater  │  │  Downstream │  │   Channel   │              │
│  │Identification│──│   Tracing   │──│Classification│             │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   HYDRAULIC DESIGN                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Rational   │  │  Manning's  │  │    Pipe     │              │
│  │   Method    │──│  Equation   │──│   Sizing    │              │
│  │   (Q=CIA)   │  │  (Velocity) │  │ (Standard)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUTS                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ GeoJSON  │  │   JSON   │  │   3D     │  │  Design  │        │
│  │ Network  │  │  Report  │  │  Visual  │  │  Tables  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- **Python 3.8 or higher**
- **GDAL/OGR libraries** (for geospatial processing)

### System Dependencies (Linux/Ubuntu)

```bash
# Install GDAL
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev python3-gdal
```

### System Dependencies (macOS)

```bash
brew install gdal
```

### Install Python Dependencies

```bash
# Clone or navigate to the project
cd AIR_Terra_Pravah

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Install WhiteboxTools

```bash
pip install whitebox
```

> **Note**: The WhiteboxTools binary will be downloaded automatically on first use (~120MB).

### Verify Installation

```bash
python -c "from whitebox import WhiteboxTools; wbt = WhiteboxTools(); print(f'WhiteboxTools v{wbt.version()}')"
```

---

## 🚀 Quick Start

### Web Application (Recommended)

The easiest way to use Terra Pravah is through the web interface:

```bash
# 1. Navigate to project directory
cd /home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Start the server
python run.py
```

**Open browser:** http://localhost:5000

**Default Admin Credentials:**
| Field | Value |
|-------|-------|
| Email | `admin@terrapravah.com` |
| Password | `admin123` |

### Server Commands

| Command | Description |
|---------|-------------|
| `python run.py` | Start server on port 5000 |
| `python run.py --init-db` | Initialize database |
| `python run.py --port 8000` | Custom port |
| `python run.py --production` | Production mode |

### Command Line Usage (Advanced)

```bash
# Professional drainage designer with custom parameters
python professional_drainage.py /path/to/dtm.tif /path/to/output_dir --runoff-coeff 0.6 --storm-years 25
```

### Python API Usage

```python
from backend.services.drainage_service import DrainageAnalysisService

# Create service instance
service = DrainageAnalysisService(
    dtm_path='path/to/dtm.tif',
    output_dir='path/to/output',
    config={
        'runoff_coefficient': 0.5,
        'design_storm_years': 10,
        'stream_threshold_pct': 1.0,
        'is_urban': False
    }
)

# Run full analysis with progress callback
def progress_handler(progress, step):
    print(f"[{progress}%] {step}")

results = service.run_full_analysis(progress_callback=progress_handler)

# Check results
print(f"Total channels: {results['total_channels']}")
print(f"Total length: {results['total_length_km']:.2f} km")
print(f"Peak flow: {results['peak_flow_m3s']:.3f} m³/s")

# Use AI Design Assistant
from backend.services.drainage_service import AIDesignAssistant
assistant = AIDesignAssistant(results)
suggestions = assistant.analyze_design()
for s in suggestions:
    print(f"[{s['type']}] {s['message']}")
```

---

## 📖 Usage Guide

### DrainageAnalysisService (Recommended)

The `DrainageAnalysisService` class in `backend/services/drainage_service.py` provides the main interface:

```python
from backend.services.drainage_service import DrainageAnalysisService

# Initialize service
service = DrainageAnalysisService(
    dtm_path='terrain/dtm.tif',
    output_dir='output/results',
    config={
        'runoff_coefficient': 0.5,      # Suburban area
        'design_storm_years': 10,        # 10-year return period
        'stream_threshold_pct': 1.0,     # 1% of cells for stream initiation
        'is_urban': False                # Rural/suburban setting
    }
)

# Run complete analysis
results = service.run_full_analysis()

# Quick preview analysis (lower resolution)
preview = service.run_quick_analysis()

# Get terrain preview without full analysis
terrain_info = service.get_terrain_preview()
```

### Professional Drainage Designer

The `professional_drainage.py` module provides advanced hydrological analysis:

```python
from professional_drainage import ProfessionalDrainageDesigner

# Initialize designer
designer = ProfessionalDrainageDesigner(
    dtm_path='terrain/dtm.tif',
    output_dir='output/results'
)

# Configure design parameters
designer.runoff_coeff = 0.5      # Suburban area
designer.design_storm_years = 10  # 10-year return period

# Run complete analysis
report = designer.process()

# Access results
print(f"Total network length: {report['network_summary']['total_length_km']:.2f} km")
print(f"Primary channels: {report['network_summary']['primary_channels']}")
```

---

## ⚙️ Configuration

### Default Configuration (config/default_config.json)

```json
{
  "dtm_resolution": 1.0,
  "flow_accumulation_threshold": 500,
  "flow_direction_algorithm": "D8",
  "min_stream_length": 100.0,
  
  "slope_flat": 0.2,
  "slope_shallow": 2.0,
  "slope_moderate": 5.0,
  "slope_steep": 10.0,
  
  "safety_factor": 1.5,
  "design_storm_return_period": 10,
  "vegetation_buffer_width": 2.0,
  "service_corridor_width": 1.0
}
```

### Configuration Parameters Reference

| Parameter | Description | Default | Valid Range |
|-----------|-------------|---------|-------------|
| `flow_accumulation_threshold` | Cells needed to initiate stream | 500 | 100 - 10000 |
| `min_stream_length` | Minimum drain length (m) | 100 | 10 - 1000 |
| `slope_flat` | Threshold for pumped drainage (%) | 0.2 | 0.1 - 0.5 |
| `slope_shallow` | Threshold for shallow drains (%) | 2.0 | 1.0 - 3.0 |
| `slope_moderate` | Threshold for V-ditches (%) | 5.0 | 3.0 - 8.0 |
| `slope_steep` | Threshold for trapezoidal channels (%) | 10.0 | 8.0 - 15.0 |
| `safety_factor` | Capacity safety factor | 1.25 | 1.2 - 2.5 |
| `design_storm_return_period` | Design storm (years) | 10 | 2 - 100 |

### Regional Settings (New in v2.2)

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `climate_region` | Regional IDF curve | `default` | `rajasthan_arid`, `delhi_ncr`, `mumbai_coastal`, `chennai_coastal`, `bengaluru_deccan`, `kolkata_gangetic`, `northeast_hills` |
| `antecedent_moisture` | Pre-storm soil moisture | `normal` | `dry`, `normal`, `wet` |
| `soil_type` | Soil infiltration class | `normal` | `sandy`, `normal`, `clay` |
| `tc_method` | Time of concentration method | `kirpich` | `kirpich`, `nrcs`, `bransby`, `auto` |

### Runoff Coefficients (C)

| Land Use | Coefficient |
|----------|-------------|
| Impervious surfaces | 0.95 |
| Urban (high density) | 0.70 |
| Urban (medium density) | 0.50 |
| Suburban | 0.35 |
| Rural | 0.20 |
| Forest | 0.15 |

**Indian-Specific Land Use Types (New):**

| Land Use | Coefficient | Notes |
|----------|-------------|-------|
| Paved roads | 0.85 | Concrete/asphalt |
| Gravel roads | 0.35 | Unpaved rural |
| Sandy soil (flat) | 0.10 | High infiltration |
| Sandy soil (steep) | 0.20 | Reduced infiltration |
| Clay soil (flat) | 0.30 | Low infiltration |
| Clay soil (steep) | 0.50 | Very low infiltration |
| Agricultural row crops | 0.35 | Typical farming |
| Paddy fields | 0.25 | Flooded rice |
| Scrubland (arid) | 0.45 | Rajasthan, Gujarat |

---

## 🌊 Hydrological Methods

### Flow Direction: D∞ (D-Infinity) Algorithm

The D∞ algorithm (Tarboton, 1997) distributes flow between multiple downslope cells based on aspect:

- More realistic flow representation than D8
- Handles divergent and convergent flow
- Used for specific contributing area calculations

### Flow Direction: D8 Algorithm

The D8 algorithm assigns flow direction to one of eight neighboring cells based on steepest descent:

```
┌───┬───┬───┐
│ 32│ 64│128│
├───┼───┼───┤
│ 16│ X │ 1 │
├───┼───┼───┤
│ 8 │ 4 │ 2 │
└───┴───┴───┘
```

### Strahler Stream Ordering

Hierarchical stream classification:
- Order 1: Headwater streams (no tributaries)
- Order 2: Formed by junction of two Order 1 streams
- Order n: Formed by junction of two Order (n-1) streams

### Manning's Equation

Open channel flow velocity:

$$V = \frac{1}{n} R^{2/3} S^{1/2}$$

Where:
- $V$ = Flow velocity (m/s)
- $n$ = Manning's roughness coefficient
- $R$ = Hydraulic radius (m) = Area / Wetted Perimeter
- $S$ = Channel slope (m/m)

**Manning's Roughness Coefficients:**

| Material | n value |
|----------|---------|
| Concrete pipe | 0.013 |
| PVC pipe | 0.010 |
| Corrugated metal | 0.024 |
| Earth channel | 0.025 |
| Grass-lined channel | 0.035 |
| Natural stream | 0.040 |

### Rational Method

Peak runoff estimation with safety factor:

$$Q = C \cdot I \cdot A \cdot SF / 360$$

Where:
- $Q$ = Peak discharge (m³/s)
- $C$ = Runoff coefficient (adjusted for slope, soil, AMC)
- $I$ = Rainfall intensity (mm/hr)
- $A$ = Catchment area (hectares)
- $SF$ = Safety factor (default 1.25)

> **Note**: Rational Method valid for catchments < 80 hectares (IRC SP 13:2004).

### Time of Concentration Methods

The system supports multiple Tc methods (configurable via `tc_method`):

#### Kirpich Formula (Default)
$$T_c = 0.0078 \cdot L^{0.77} \cdot S^{-0.385}$$

Best for: Natural basins with well-defined channels.

#### NRCS (SCS) Lag Method
$$T_c = \frac{L^{0.8} \cdot \left(\frac{1000}{CN} - 9\right)^{0.7}}{1900 \cdot S^{0.5} \cdot 0.6}$$

Best for: Urban and suburban areas with mixed land use.

#### Bransby-Williams Formula
$$T_c = \frac{0.243 \cdot L}{A^{0.1} \cdot S^{0.2}}$$

Best for: Rural catchments in arid/semi-arid regions (e.g., Rajasthan).

> **Recommendation**: Use `tc_method: "auto"` for geometric mean of all methods.

### Regional IDF Curves (India-Specific)

Rainfall intensity calculated using region-specific IDF parameters:

$$I = \frac{a \cdot K_f}{(t + b)^n}$$

| Region | a | b | n | Typical Annual Rainfall |
|--------|---|---|---|-------------------------|
| Default | 1000 | 10 | 0.80 | 800 mm |
| Rajasthan (Arid) | 850 | 8 | 0.75 | 400 mm |
| Delhi NCR | 1100 | 12 | 0.82 | 650 mm |
| Mumbai (Coastal) | 1500 | 15 | 0.85 | 2200 mm |
| Chennai (Coastal) | 1400 | 14 | 0.83 | 1400 mm |
| Bengaluru (Deccan) | 1000 | 11 | 0.78 | 950 mm |
| Kolkata (Gangetic) | 1200 | 13 | 0.80 | 1600 mm |
| Northeast Hills | 1800 | 18 | 0.88 | 2500+ mm |

> **Reference**: IMD (India Meteorological Department) methodology.

### SCS Curve Number Method

Runoff depth calculation with Antecedent Moisture Condition (AMC):

$$Q = \frac{(P - 0.2S)^2}{P + 0.8S}$$

Where:
- $Q$ = Runoff depth (mm)
- $P$ = Precipitation depth (mm)
- $S$ = Potential maximum retention = (25400/CN) - 254

**AMC Adjustment Factors:**

| Condition | Factor | When to Use |
|-----------|--------|-------------|
| Dry (AMC I) | 0.85 | Pre-monsoon, long dry period |
| Normal (AMC II) | 1.00 | Typical conditions |
| Wet (AMC III) | 1.15 | During monsoon, saturated soil |

### Froude Number

Flow characterization:

$$Fr = \frac{V}{\sqrt{gD}}$$

| Froude Number | Flow Type |
|---------------|-----------|
| Fr < 1 | Subcritical (tranquil) |
| Fr = 1 | Critical |
| Fr > 1 | Supercritical (rapid) |

---

## 🎨 Drain Type Selection

The system automatically selects drain types based on terrain slope using `DrainageDesignSelector`:

| Slope Range | Design Type | Manning's n | Typical Application |
|-------------|------------|-------------|---------------------|
| < 0.5% | Pump Station | 0.013 | Very flat areas, below water table |
| 0.5 - 1% | Circular Pipe / Trapezoidal | 0.013-0.022 | Low slope areas |
| 1 - 5% | Box Culvert / V-Ditch | 0.015-0.030 | Moderate slopes |
| 5 - 10% | Trapezoidal Channel | 0.022 | Moderate-high slopes |
| 10 - 15% | Cascade Channel | 0.050 | Steep terrain |
| > 15% | Stepped Channel | 0.045 | Very steep terrain |

### Standard Pipe Diameters

The system selects from standard pipe sizes (mm):
`150, 200, 250, 300, 375, 450, 525, 600, 750, 900, 1050, 1200`

---

## 📤 Outputs

### Directory Structure

```
output_dir/
├── temp/                        # Temporary processing files
├── visualizations/
│   └── drainage_analysis.html   # Interactive 3D visualization
├── drainage_network.geojson     # Network in GeoJSON format
└── drainage_report.json         # Engineering report
```

### GIS Outputs (GeoPackage/GeoJSON)

1. **Drainage Network Lines** (`drainage_network.geojson`)
   - `type`: Channel classification (primary/secondary/tertiary)
   - `length_m`: Channel length in meters
   - `slope_pct`: Average slope percentage
   - `peak_flow_m3s`: Design peak flow (m³/s)
   - `pipe_diameter_mm`: Recommended pipe size
   - `velocity_ms`: Design flow velocity

2. **Structures** (`drainage_network.gpkg:structures`)
   - Junction nodes
   - Outlet structures
   - Drop structures

### Reports (JSON)

**drainage_report.json** includes:
- Project metadata
- Terrain statistics
- Network summary (channel counts, total length)
- Hydraulic design parameters
- Individual channel details

### Visualizations

1. **3D Interactive View** (`drainage_analysis.html`)
   - Terrain surface with natural coloring
   - Drainage network with gradient coloring (upstream → downstream)
   - Flow direction indicators
   - Outlet markers
   - Hover information with hydraulic data

2. **Static Maps** (optional)
   - 2D drainage map on hillshade
   - Longitudinal profiles
   - Cross-sections

---

## 📁 Project Structure

```
AIR_Terra_Pravah/
├── 📄 README.md                      # Technical documentation
├── 📄 USER_GUIDE.md                  # 📖 User guide for end users
├── 📄 requirements.txt               # Python dependencies
├── 📄 run.py                         # Application entry point
├── 📄 init_db.py                     # Database initialization
├── 📄 Makefile                       # Build and deployment commands
│
├── 🐳 Docker Files
│   ├── Dockerfile                    # Backend container
│   ├── docker-compose.yml            # Development stack
│   ├── docker-compose.prod.yml       # Production overrides
│   ├── .dockerignore                 # Docker build exclusions
│   └── .env.example                  # Environment template
│
├── 🐍 professional_drainage.py       # Professional designer with fluid mechanics
│
├── 📁 backend/
│   ├── 📄 __init__.py
│   ├── 📄 app.py                     # Flask application factory
│   ├── 📄 config.py                  # Application configuration
│   │
│   ├── 📁 api/                       # REST API endpoints
│   │   ├── admin.py                  # Admin operations
│   │   ├── analysis.py               # Analysis endpoints
│   │   ├── auth.py                   # Authentication (JWT)
│   │   ├── billing.py                # Subscription management
│   │   ├── projects.py               # Project CRUD
│   │   ├── reports.py                # Report generation
│   │   ├── teams.py                  # Team collaboration
│   │   ├── uploads.py                # File uploads
│   │   └── users.py                  # User management
│   │
│   ├── 📁 models/
│   │   └── models.py                 # SQLAlchemy models
│   │
│   ├── 📁 services/
│   │   ├── drainage_service.py       # Core drainage analysis engine
│   │   ├── visualization_service.py  # 3D Plotly visualization
│   │   └── email_service.py          # Email notifications
│   │
│   └── 📁 utils/
│       └── __init__.py
│
├── 📁 frontend/                      # React + TypeScript + Vite
│   ├── 📄 Dockerfile                 # Frontend container
│   ├── 📄 index.html
│   ├── 📄 package.json
│   ├── 📄 vite.config.ts
│   ├── 📄 tailwind.config.js
│   └── 📁 src/
│       ├── App.tsx                   # Main application
│       ├── 📁 components/            # Reusable UI components
│       ├── 📁 pages/                 # Page components
│       │   ├── Landing.tsx
│       │   ├── 📁 auth/              # Login, Register, etc.
│       │   └── 📁 dashboard/         # Dashboard pages
│       │       ├── Dashboard.tsx
│       │       ├── Projects.tsx
│       │       ├── Analysis.tsx
│       │       ├── Reports.tsx
│       │       ├── Teams.tsx
│       │       ├── Profile.tsx
│       │       ├── Settings.tsx
│       │       └── Billing.tsx
│       ├── 📁 services/              # API client
│       ├── 📁 store/                 # Zustand state management
│       └── 📁 context/               # React context
│
├── 📁 nginx/                         # Production reverse proxy
│   └── nginx.conf
│
├── 📁 config/
│   └── default_config.json           # Default configuration
│
├── 📁 database/                      # SQLite database
├── 📁 uploads/                       # Uploaded terrain files
├── 📁 results/                       # Analysis results
└── 📁 migrations/                    # Database migrations
```

---

## 📖 User Guide

For detailed usage instructions, see the **[User Guide](USER_GUIDE.md)** which covers:

- 🚀 Getting started and account creation
- 📁 Creating and managing projects
- 📤 Uploading DTM files
- 📊 Running drainage analysis
- 🗺️ Understanding 3D visualization
- 📄 Generating professional reports
- 👥 Team collaboration
- ⚙️ Settings and preferences
- 💳 Billing and subscriptions

---

## 📚 API Reference

### DrainageAnalysisService (Main Interface)

```python
class DrainageAnalysisService:
    """Service for running drainage network analysis."""
    
    def __init__(self, dtm_path: str, output_dir: str, config: dict = None): ...
    def run_full_analysis(self, progress_callback=None) -> dict: ...
    def run_quick_analysis(self, progress_callback=None) -> dict: ...
    def get_terrain_preview(self) -> dict: ...
    def export_to_format(self, format_type: str, output_path: str = None) -> str: ...
    def cleanup(self): ...
```

### OptimizedDrainageDesigner

```python
class OptimizedDrainageDesigner:
    """Optimized drainage designer using D∞ flow routing."""
    
    def __init__(self, dtm_path: str, output_dir: str, config: dict = None): ...
    def set_progress_callback(self, callback): ...
    def load_terrain(self) -> self: ...
    def hydrological_processing(self) -> self: ...
    def extract_drainage_network(self) -> self: ...
    def identify_outlets(self) -> self: ...
    def create_visualization(self) -> str: ...
    def generate_report(self) -> dict: ...
    def export_geojson(self) -> str: ...
    def process(self) -> dict: ...
    def cleanup(self): ...
```

### AIDesignAssistant

```python
class AIDesignAssistant:
    """AI-powered design assistant for drainage optimization."""
    
    def __init__(self, analysis_results: dict): ...
    def analyze_design(self) -> list: ...
    def optimize_design(self) -> dict: ...
```

### HydrologicalConstants

```python
class HydrologicalConstants:
    """Standard hydrological and hydraulic constants."""
    
    MANNING_N: dict          # Manning's roughness coefficients
    RUNOFF_COEFF: dict       # Runoff coefficients by land use
    RETURN_PERIODS: list     # Standard return periods [2, 5, 10, 25, 50, 100]
    MIN_SLOPE_PIPE: float    # Minimum pipe slope (0.005)
    MIN_SLOPE_CHANNEL: float # Minimum channel slope (0.002)
    PIPE_DIAMETERS: list     # Standard pipe sizes (mm)
```

### FluidMechanics

```python
class FluidMechanics:
    """Fluid mechanics calculations for drainage design."""
    
    @staticmethod
    def manning_velocity(hydraulic_radius, slope, n=0.013) -> float:
        """Calculate flow velocity using Manning's equation."""
    
    @staticmethod
    def manning_flow(area, hydraulic_radius, slope, n=0.013) -> float:
        """Calculate flow rate using Manning's equation."""
    
    @staticmethod
    def pipe_full_flow(diameter, slope, n=0.013) -> float:
        """Calculate full pipe flow capacity."""
    
    @staticmethod
    def froude_number(velocity, depth) -> float:
        """Calculate Froude number for flow characterization."""
    
    @staticmethod
    def required_pipe_diameter(flow, slope, n=0.013) -> float:
        """Calculate required pipe diameter for given flow."""
```

### HydrologicalAnalysis

```python
class HydrologicalAnalysis:
    """Hydrological analysis methods."""
    
    @staticmethod
    def rational_method(C, I, A) -> float:
        """Peak runoff using Rational Method (Q = CIA)."""
    
    @staticmethod
    def time_of_concentration_kirpich(length, slope) -> float:
        """Time of concentration using Kirpich formula."""
    
    @staticmethod
    def rainfall_intensity(duration, return_period=10) -> float:
        """Rainfall intensity from IDF curve approximation."""
    
    @staticmethod
    def scs_curve_number_runoff(P, CN) -> float:
        """Runoff depth using SCS Curve Number method."""
```

### ProfessionalDrainageDesigner

```python
class ProfessionalDrainageDesigner:
    """Professional drainage network designer (standalone module)."""
    
    def __init__(self, dtm_path: str, output_dir: str): ...
    def load_terrain(self) -> self: ...
    def hydrological_processing(self) -> self: ...
    def extract_drainage_network(self) -> self: ...
    def identify_outlets(self) -> self: ...
    def create_visualization(self) -> str: ...
    def generate_report(self) -> dict: ...
    def export_geojson(self) -> None: ...
    def process(self) -> dict: ...
```

### DrainageDesignSelector

```python
class DrainageDesignSelector:
    """Automated design selection based on slope and hydraulic requirements."""
    
    @staticmethod
    def select_design(slope: float, peak_flow: float = 0, is_urban: bool = False) -> dict:
        """Select appropriate drainage design based on conditions."""
```

### HydraulicValidator

```python
class HydraulicValidator:
    """Validates hydraulic design parameters."""
    
    @staticmethod
    def validate_continuity(upstream_flows, downstream_flow, tolerance=0.01) -> dict: ...
    @staticmethod
    def validate_slope(slope, infrastructure_type='pipe') -> dict: ...
    @staticmethod
    def validate_velocity(velocity) -> dict: ...
    @staticmethod
    def full_validation(slope, velocity, upstream_flows=None, 
                        downstream_flow=None, infrastructure_type='pipe') -> dict: ...
```

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test class
python -m pytest tests/test_drainage_network.py::TestManningEquation -v

# Run integration tests (requires RUN_INTEGRATION_TESTS=1)
RUN_INTEGRATION_TESTS=1 python -m pytest tests/ -v

# Quick validation of drainage service
python -c "from backend.services.drainage_service import DrainageAnalysisService; print('OK')"

# Test FluidMechanics calculations
python -c "from backend.services.drainage_service import FluidMechanics; print(FluidMechanics.manning_velocity(0.25, 0.01))"
```

---

## 🚀 Deployment

### Docker Deployment (Recommended)

The project includes complete Docker configuration for easy deployment.

#### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/AIR_Terra_Pravah.git
cd AIR_Terra_Pravah

# Copy environment template
cp .env.example .env

# Edit .env with your settings (especially SECRET_KEY, JWT_SECRET_KEY)
nano .env

# Build and start containers
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

#### Production Deployment

```bash
# Generate SSL certificates (or use your own)
make ssl-dev

# Start full production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# With PostgreSQL and Celery workers
docker-compose --profile production --profile workers up -d
```

#### Available Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React/Vite UI |
| Backend | 5000 | Flask API |
| Redis | 6379 | Cache & Queue |
| PostgreSQL | 5432 | Database (production) |
| Nginx | 80/443 | Reverse proxy (production) |

### Manual Deployment

#### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 run:app
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx or any static file server
```

### Environment Variables

Key environment variables for production:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | development |
| `SECRET_KEY` | Flask secret key | **Required** |
| `JWT_SECRET_KEY` | JWT signing key | **Required** |
| `DATABASE_URL` | Database connection | sqlite:///database/terrapravah.db |
| `REDIS_URL` | Redis connection | redis://localhost:6379/0 |
| `WBT_PATH` | WhiteboxTools path | /opt/WBT |
| `CORS_ORIGINS` | Allowed origins | http://localhost:3000 |

### Makefile Commands

```bash
make help           # Show all commands
make install        # Install all dependencies
make dev            # Start development servers
make build          # Build for production
make docker-build   # Build Docker images
make docker-up      # Start containers
make docker-prod    # Start production stack
make test           # Run tests
make lint           # Run linters
```

---

## ❗ Troubleshooting

### Common Issues

#### Runtime Timeout or Window Crashes

The optimized `drainage_service.py` includes performance limits to prevent timeouts:
- `max_headwaters=100`: Limits starting points for tracing
- `max_trace_steps=1000`: Limits downstream tracing iterations
- `min_spacing=30`: Ensures headwaters are well-spaced

If still experiencing issues, try:
```python
# Use quick analysis for faster results
service = DrainageAnalysisService(dtm_path, output_dir)
results = service.run_quick_analysis()
```

#### WhiteboxTools not found

```bash
pip uninstall whitebox
pip install whitebox

# Verify installation
python -c "from whitebox import WhiteboxTools; print('OK')"
```

#### Memory errors with large DTMs

1. Reduce DTM resolution before processing
2. Increase `processing_chunk_size` in configuration
3. Use tiled processing for very large areas

```bash
# Resample DTM to lower resolution
gdalwarp -tr 5 5 input.tif output_5m.tif
```

#### No streams extracted

1. Reduce `flow_accumulation_threshold` in configuration
2. Check if DTM has proper elevation values (not all NaN/NoData)
3. Ensure terrain has sufficient relief

#### GDAL/Rasterio errors

```bash
# Linux
sudo apt-get install gdal-bin libgdal-dev

# Reinstall rasterio with system GDAL
pip install --no-binary rasterio rasterio
```

#### Visualization not loading

1. Ensure Plotly is properly installed
2. Check output HTML file exists
3. Open in modern browser (Chrome, Firefox)

---

## ⚠️ Limitations

- **Maximum recommended area**: 10 km² (larger areas may require chunking)
- **DTM requirements**: Continuous coverage (handles small data gaps)
- **Flat terrain** (< 0.2% slope): Flagged for pumped drainage consideration
- **Urban areas**: Best results with building footprint masking (optional)
- **Resolution**: Minimum 1m recommended for detailed design

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Run tests**: `python -m pytest tests/`
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions with docstrings
- Add tests for new features

---

## 📖 References

### Algorithms & Methods
- **O'Callaghan, J.F. and Mark, D.M. (1984)** - "The extraction of drainage networks from digital elevation data" - D8 Flow Direction Algorithm
- **Tarboton, D.G. (1997)** - "A new method for the determination of flow directions and upslope areas in grid digital elevation models" - D-Infinity Algorithm
- **Strahler, A.N. (1957)** - "Quantitative analysis of watershed geomorphology" - Stream Order Classification

### Hydraulics
- **Manning, R. (1891)** - "On the flow of water in open channels and pipes" - Manning's Equation
- **Chow, V.T. (1959)** - "Open-channel hydraulics" - Comprehensive hydraulics reference

### Hydrology
- **SCS (1972)** - "National Engineering Handbook, Section 4: Hydrology" - Curve Number Method
- **Kirpich, Z.P. (1940)** - "Time of concentration of small agricultural watersheds" - Kirpich Formula

### Software
- **WhiteboxTools** - https://www.whiteboxgeo.com/
- **GDAL/OGR** - https://gdal.org/
- **Rasterio** - https://rasterio.readthedocs.io/

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 📧 Contact

For questions, issues, or suggestions, please:
- Open an issue on GitHub
- Contact the development team

---

<p align="center">
  <b>Built with ❤️ for better drainage infrastructure</b>
</p>
