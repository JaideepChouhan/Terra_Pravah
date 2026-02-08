# 📖 Terra Pravah - User Guide

**AI-Powered Drainage Network Design & Visualization System**

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard Overview](#2-dashboard-overview)
3. [Creating Your First Project](#3-creating-your-first-project)
4. [Uploading DTM Files](#4-uploading-dtm-files)
5. [Running Drainage Analysis](#5-running-drainage-analysis)
6. [Understanding Results](#6-understanding-results)
7. [3D Visualization](#7-3d-visualization)
8. [Generating Reports](#8-generating-reports)
9. [Team Collaboration](#9-team-collaboration)
10. [Managing Your Profile](#10-managing-your-profile)
11. [Billing & Subscriptions](#11-billing--subscriptions)
12. [Settings & Preferences](#12-settings--preferences)
13. [Keyboard Shortcuts](#13-keyboard-shortcuts)
14. [FAQ & Tips](#14-faq--tips)

---

## 1. Getting Started

### 1.1 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Browser | Chrome 90+, Firefox 88+, Edge 90+ | Latest Chrome/Firefox |
| Internet | 2 Mbps | 10+ Mbps |
| Screen Resolution | 1280×720 | 1920×1080+ |

### 1.2 Creating an Account

1. Navigate to the Terra Pravah website
2. Click **"Get Started"** or **"Sign Up"**
3. Enter your details:
   - Email address
   - Password (minimum 8 characters)
   - First and last name
   - Company (optional)
4. Click **"Create Account"**
5. Verify your email (check inbox/spam folder)

### 1.3 Logging In

1. Go to the login page
2. Enter your email and password
3. Click **"Sign In"**

> 💡 **Tip:** Check "Remember me" for faster access on trusted devices.

### 1.4 Default Admin Account (Development)

For testing purposes:
- **Email:** admin@terrapravah.com
- **Password:** admin123

---

## 2. Dashboard Overview

After logging in, you'll see the main dashboard with:

### 2.1 Navigation Sidebar

| Icon | Section | Description |
|------|---------|-------------|
| 📊 | Dashboard | Overview and quick stats |
| 📁 | Projects | All your drainage projects |
| 📈 | Analysis | Run and view analyses |
| 📄 | Reports | Generate professional reports |
| 👥 | Teams | Collaborate with others |
| ⚙️ | Settings | Preferences and configuration |
| 👤 | Profile | Your account details |
| 💳 | Billing | Subscription management |

### 2.2 Dashboard Widgets

- **Recent Projects** - Quick access to your latest work
- **Analysis Status** - Ongoing and completed analyses
- **Storage Usage** - How much of your quota is used
- **Quick Actions** - Create new project, upload DTM

---

## 3. Creating Your First Project

### 3.1 Step-by-Step Guide

1. Click **"+ New Project"** button
2. Fill in project details:

   | Field | Description | Example |
   |-------|-------------|---------|
   | Project Name | Descriptive name | "Mumbai Suburb Drainage Phase 1" |
   | Description | Optional details | "Stormwater drainage for 50 hectare residential area" |
   | Location | Geographic location | "Thane, Maharashtra" |
   | Design Storm | Return period in years | 10 (typical urban), 25 (critical areas) |
   | Runoff Coefficient | Surface type factor | 0.7 (urban), 0.3 (rural) |
   | Flow Algorithm | Analysis method | D8 (faster) or D∞ (more accurate) |

3. Click **"Create Project"**

### 3.2 Understanding Parameters

#### Design Storm Return Period

| Years | Usage | Description |
|-------|-------|-------------|
| 2-5 | Minor drains | Low-risk areas, residential streets |
| 10 | Standard urban | Most urban drainage systems |
| 25 | Major infrastructure | Main drains, commercial areas |
| 50-100 | Critical | Hospitals, airports, industrial |

#### Runoff Coefficient (C)

| Surface Type | Coefficient | Description |
|--------------|-------------|-------------|
| Asphalt/Concrete | 0.85-0.95 | Roads, parking lots |
| Urban Residential | 0.65-0.75 | Mixed development |
| Suburban | 0.40-0.60 | Low density housing |
| Parks/Lawns | 0.20-0.35 | Green spaces |
| Agricultural | 0.15-0.30 | Farmland |
| Forest | 0.10-0.20 | Natural vegetation |

#### Flow Algorithms

| Algorithm | Speed | Accuracy | Best For |
|-----------|-------|----------|----------|
| **D8** | ⚡ Fast | Good | Steep terrain, quick analysis |
| **D∞** | 🐢 Slower | Excellent | Flat terrain, detailed design |

---

## 4. Uploading DTM Files

### 4.1 Supported File Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| GeoTIFF | .tif, .tiff | Recommended format |
| ESRI ASCII Grid | .asc | ASCII elevation grid |
| LAS/LAZ | .las, .laz | LiDAR point cloud |
| XYZ | .xyz | Point cloud text file |

### 4.2 Upload Process

1. Open your project
2. Click **"Upload DTM"** button
3. Drag & drop your file OR click to browse
4. Wait for upload and processing
5. Preview will appear when ready

### 4.3 File Requirements

| Requirement | Specification |
|-------------|---------------|
| Maximum Size | 500 MB (Free), 2 GB (Pro) |
| Resolution | 1-30 meters recommended |
| Projection | Any (auto-detected) |
| Area | Up to 10 km² recommended |

### 4.4 Tips for Best Results

✅ **Do:**
- Use projected coordinate systems (UTM preferred)
- Ensure complete coverage (no large gaps)
- Pre-process to remove obvious errors
- Use 1-5m resolution for detailed design

❌ **Avoid:**
- Very large files (>10 km² without chunking)
- Corrupted or incomplete data
- Geographic coordinates for small areas
- Extremely low resolution (>30m)

---

## 5. Running Drainage Analysis

### 5.1 Starting Analysis

1. Open your project with uploaded DTM
2. Click **"Run Analysis"** button
3. Confirm parameters (or adjust if needed)
4. Click **"Start"**

### 5.2 Analysis Stages

The analysis progresses through several stages:

| Stage | Progress | Description |
|-------|----------|-------------|
| 1. Loading | 0-10% | Reading terrain data |
| 2. Conditioning | 10-30% | Filling depressions, preparing DEM |
| 3. Flow Direction | 30-50% | Calculating water flow paths |
| 4. Flow Accumulation | 50-65% | Determining drainage areas |
| 5. Network Extraction | 65-80% | Identifying channels |
| 6. Hydraulic Design | 80-95% | Sizing pipes, calculating flows |
| 7. Visualization | 95-100% | Creating 3D view |

### 5.3 During Analysis

- Progress bar shows current stage
- Status text indicates what's happening
- You can navigate away - analysis continues in background
- Email notification when complete (if enabled)

### 5.4 Analysis Time Estimates

| DTM Size | Area | Expected Time |
|----------|------|---------------|
| < 10 MB | < 1 km² | 30 seconds - 2 minutes |
| 10-50 MB | 1-5 km² | 2-5 minutes |
| 50-200 MB | 5-10 km² | 5-15 minutes |
| > 200 MB | > 10 km² | 15-45 minutes |

---

## 6. Understanding Results

### 6.1 Network Summary

After analysis, you'll see key statistics:

| Metric | Description | Typical Range |
|--------|-------------|---------------|
| Total Channels | Number of drainage lines | 10-500+ |
| Total Length | Combined channel length | 1-50+ km |
| Outlets | Discharge points | 1-20 |
| Peak Flow | Maximum design flow | 0.1-10+ m³/s |
| Primary Channels | Main drainage lines | 10-30% of total |
| Secondary Channels | Collector drains | 30-50% of total |
| Tertiary Channels | Minor drains | 20-40% of total |

### 6.2 Channel Classification

Channels are classified by Strahler stream order:

| Type | Order | Function | Typical Size |
|------|-------|----------|--------------|
| **Primary** | 3+ | Main collectors | 600-1200 mm pipe |
| **Secondary** | 2 | Sub-collectors | 300-600 mm pipe |
| **Tertiary** | 1 | Field drains | 150-300 mm pipe |

### 6.3 Channel Details Table

Each channel shows:

| Column | Description |
|--------|-------------|
| Type | Primary/Secondary/Tertiary |
| Length (m) | Channel segment length |
| Slope (%) | Ground gradient |
| Flow (m³/s) | Design peak flow rate |
| Pipe (mm) | Recommended pipe diameter |
| Velocity (m/s) | Flow velocity (should be 0.6-3.0) |

### 6.4 Terrain Information

| Metric | Description |
|--------|-------------|
| Dimensions | Raster size (cols × rows) |
| Resolution | Cell size in meters |
| Elevation Range | Min to max elevation |
| Relief | Total height difference |

### 6.5 Hydraulic Design Info

| Parameter | Description |
|-----------|-------------|
| Design Method | Rational Method (Q=CIA) |
| Flow Routing | D8 or D-Infinity |
| Pipe Sizing | Manning's equation based |

---

## 7. 3D Visualization

### 7.1 Viewing Modes

| Mode | Shows | Use For |
|------|-------|---------|
| **DTM View** | Raw terrain only | Checking elevation data |
| **Drainage View** | Terrain + network | Design review |

### 7.2 Navigation Controls

| Action | Mouse | Trackpad |
|--------|-------|----------|
| Rotate | Left-click + drag | Two-finger drag |
| Zoom | Scroll wheel | Pinch |
| Pan | Right-click + drag | Three-finger drag |
| Reset | Double-click | Double-tap |

### 7.3 Understanding Colors

**Terrain:**
- 🟤 Brown → Low elevation
- 🟢 Green → Mid elevation
- ⚪ White/Gray → High elevation

**Drainage Network:**
- 🔵 Blue → Upstream (flow origin)
- 🟢 Green → Downstream (flow direction)
- Line thickness → Flow magnitude

### 7.4 Visualization Tips

- Use **DTM View** first to verify terrain data
- Switch to **Drainage View** to see the network
- Rotate to see channel connections
- Zoom to specific areas of interest

---

## 8. Generating Reports

### 8.1 Available Report Templates

| Template | Description | Best For |
|----------|-------------|----------|
| **Engineering Design** | Full technical report | Detailed design, approvals |
| **Construction Docs** | Build specifications | Contractors, site teams |
| **Environmental** | Impact assessment | Regulatory compliance |
| **Permit Package** | Regulatory submission | Government approvals |
| **Client Presentation** | Executive summary | Stakeholder meetings |

### 8.2 Generating a Report

1. Go to **Reports** section
2. Select a completed project
3. Choose a report template
4. Select output format (HTML, JSON)
5. Click **"Generate Report"**
6. Download when ready

### 8.3 Report Contents

A typical Engineering Report includes:

- **Executive Summary** - Key findings and recommendations
- **Project Information** - Location, parameters, coordinates
- **Network Summary** - Statistics and classification
- **Design Calculations** - Flow rates, pipe sizes, velocities
- **Recommendations** - Construction and maintenance guidance
- **Appendices** - Detailed channel data

### 8.4 Downloading Data

Additional downloads available:

| Format | File | Use |
|--------|------|-----|
| GeoJSON | drainage_network.geojson | GIS software, mapping |
| JSON | analysis_report.json | Data integration |
| CSV | channel_data.csv | Spreadsheets, databases |

---

## 9. Team Collaboration

### 9.1 Creating a Team

1. Go to **Teams** section
2. Click **"Create Team"**
3. Enter team name and description
4. Click **"Create"**

### 9.2 Inviting Members

1. Select your team
2. Click **"Invite"** button
3. Enter colleague's email
4. Select role:

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, can invite others |
| **Member** | Create/edit projects, run analysis |
| **Viewer** | View-only access |

5. Click **"Send Invite"**

### 9.3 Managing Members

- View all team members in the team panel
- See member roles (crown = owner)
- Remove members by clicking the trash icon
- Only owners can remove admins

### 9.4 Team Projects

- Team projects are visible to all members
- Permissions based on member role
- Activity logged for audit purposes

---

## 10. Managing Your Profile

### 10.1 Profile Information

Edit your profile to update:

| Field | Description |
|-------|-------------|
| First Name | Your given name |
| Last Name | Your surname |
| Company | Organization name |
| Job Title | Your role |
| Phone | Contact number |
| Timezone | For accurate timestamps |

### 10.2 Changing Password

1. Go to **Profile** → **Security** tab
2. Enter current password
3. Enter new password (min 8 characters)
4. Confirm new password
5. Click **"Update Password"**

### 10.3 Notification Settings

Toggle notifications for:

- ✉️ Email when analysis completes
- ✉️ Email when project is shared
- ✉️ Email when mentioned in comments
- 🔔 Push notifications

### 10.4 Display Preferences

- **Units:** Metric or Imperial
- **Theme:** Dark (default)

---

## 11. Billing & Subscriptions

### 11.1 Available Plans

| Feature | Free | Professional | Enterprise |
|---------|------|--------------|------------|
| **Price** | ₹0 | ₹2,999/mo | ₹9,999/mo |
| Projects | 3 | 25 | Unlimited |
| Storage | 100 MB | 10 GB | 100 GB |
| Team Members | 1 | 5 | Unlimited |
| D∞ Algorithm | ❌ | ✅ | ✅ |
| API Access | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ✅ | ✅ |
| CAD Export | ❌ | ✅ | ✅ |
| Custom Branding | ❌ | ❌ | ✅ |

### 11.2 Upgrading Your Plan

1. Go to **Billing** section
2. Select desired plan
3. Click **"Upgrade"**
4. Complete payment (Razorpay/Stripe)
5. Access new features immediately

### 11.3 Viewing Invoices

- All invoices listed in billing history
- Download PDF for records
- Status shows paid/pending/failed

### 11.4 Cancelling Subscription

1. Go to **Billing**
2. Click **"Cancel Subscription"**
3. Confirm cancellation
4. Access continues until period end

---

## 12. Settings & Preferences

### 12.1 Default Analysis Settings

Configure defaults for new projects:

| Setting | Options | Recommended |
|---------|---------|-------------|
| Algorithm | D8, D∞ | D8 for most cases |
| Storm Years | 2-100 | 10 years |
| Runoff Coeff | 0.1-0.95 | 0.5-0.7 |
| Units | Metric, Imperial | Metric |

### 12.2 Notification Preferences

Control when you receive emails:

- Analysis completion
- Project sharing
- Team invitations
- System updates

### 12.3 API Keys (Professional+)

For programmatic access:

1. Go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name your key
4. Copy and store securely
5. Use in API requests

---

## 13. Keyboard Shortcuts

### 13.1 Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New project |
| `Ctrl/Cmd + S` | Save changes |
| `Ctrl/Cmd + /` | Show shortcuts |
| `Esc` | Close modal/dialog |

### 13.2 Visualization Shortcuts

| Shortcut | Action |
|----------|--------|
| `R` | Reset view |
| `D` | Toggle DTM/Drainage view |
| `+` / `-` | Zoom in/out |
| `Arrow keys` | Pan view |

---

## 14. FAQ & Tips

### 14.1 Frequently Asked Questions

**Q: How long does analysis take?**
> A: Typically 1-5 minutes for areas under 5 km². Larger areas may take longer.

**Q: What file format should I use?**
> A: GeoTIFF (.tif) is recommended for best compatibility and performance.

**Q: Why are no streams showing?**
> A: Try reducing the flow accumulation threshold in settings, or check if your DTM has sufficient elevation variation.

**Q: Can I edit the drainage network?**
> A: Currently, manual editing is not supported. Re-run analysis with different parameters for adjustments.

**Q: How accurate is the analysis?**
> A: Results depend on DTM quality. With 1-5m resolution data, expect ±10-20% accuracy for design flows.

**Q: Can I use this for flat terrain?**
> A: Yes! Use D∞ algorithm for flat areas. The system will flag areas needing pump stations.

### 14.2 Pro Tips

🎯 **Better Results:**
- Use highest resolution DTM available
- Pre-fill any obvious errors in source data
- Start with D8 for quick preview, then D∞ for final design
- Use appropriate return period for your infrastructure class

⚡ **Faster Workflow:**
- Set default parameters in Settings
- Use keyboard shortcuts
- Enable email notifications for long analyses
- Download GeoJSON for GIS integration

💾 **Data Management:**
- Organize projects with descriptive names
- Use location names consistently
- Archive completed projects
- Download reports for offline access

### 14.3 Getting Help

- **In-App:** Click the help icon (?) for contextual guidance
- **Documentation:** Full technical docs at [docs.terrapravah.com]
- **Email:** support@terrapravah.com
- **Response Time:** 24 hours (Free), 4 hours (Professional), 1 hour (Enterprise)

---

## Quick Reference Card

### Essential Formulas Used

| Formula | Equation | Usage |
|---------|----------|-------|
| Rational Method | Q = C × I × A | Peak flow calculation |
| Manning's Equation | V = (1/n) × R^(2/3) × S^(1/2) | Flow velocity |
| Kirpich Formula | Tc = 0.0195 × L^0.77 × S^(-0.385) | Time of concentration |

### Standard Pipe Sizes (mm)

150, 200, 250, 300, 375, 450, 525, 600, 750, 900, 1050, 1200

### Velocity Limits

| Condition | Min (m/s) | Max (m/s) |
|-----------|-----------|-----------|
| Self-cleaning | 0.6 | - |
| Erosion prevention | - | 3.0 |
| Optimal range | 0.8 | 2.5 |

---

<p align="center">
  <b>Terra Pravah - Professional Drainage Design Made Simple</b>
  <br>
  <i>Built with ❤️ for better infrastructure</i>
</p>
