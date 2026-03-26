import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  Download, 
  FileJson, 
  FileText, 
  Settings, 
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Layers,
  MapPin,
  Activity,
  Droplets,
  TrendingDown,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Gauge,
  Ruler
} from 'lucide-react'
import DrainageViewer, { VisualizationControls } from '../../components/DrainageViewer'
import { projectsApi, analysisApi } from '../../services/api'

interface Project {
  id: string
  name: string
  description?: string
  status: string
  dtm_file_path?: string
  visualization_path?: string
  total_channels?: number
  total_length_km?: number
  total_outlets?: number
  peak_flow_m3s?: number
  primary_count?: number
  secondary_count?: number
  tertiary_count?: number
  design_storm_years?: number
  runoff_coefficient?: number
  flow_algorithm?: string
}

interface AnalysisJob {
  id: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_step?: string
  error_message?: string
  created_at: string
  completed_at?: string
  result?: any
}

interface ChannelDetail {
  type: string
  length_m: number
  slope_pct: number
  peak_flow_m3s: number
  pipe_diameter_mm: number
  velocity_ms: number
  design_type?: string
  design_reason?: string
  validation_passed?: boolean
}

interface DrainageReport {
  project?: {
    terrain_file: string
    design_storm_return_years: number
    runoff_coefficient: number
  }
  terrain?: {
    dimensions: string
    resolution_m: number
    elevation_min: number
    elevation_max: number
    elevation_range: number
  }
  network_summary?: {
    total_channels: number
    primary_channels: number
    secondary_channels: number
    tertiary_channels: number
    total_length_m: number
    total_length_km: number
    outlets: number
  }
  hydraulics?: {
    design_method: string
    flow_routing: string
    pipe_sizing: string
    total_design_flow_m3s: number
  }
  channels?: ChannelDetail[]
}

export default function Analysis() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [job, setJob] = useState<AnalysisJob | null>(null)
  const [report, setReport] = useState<DrainageReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'drainage' | 'dtm'>('dtm')
  const [isRunningAnalysis, setIsRunningAnalysis] = useState(false)
  const [showChannelDetails, setShowChannelDetails] = useState(false)
  const [pollingActive, setPollingActive] = useState(false)

  // Fetch project data
  const fetchProject = useCallback(async () => {
    if (!projectId) return

    try {
      const response = await projectsApi.get(projectId)
      setProject(response.data.project)
      
      // If analysis is complete, fetch the detailed report
      if (response.data.project.status === 'completed') {
        fetchReport()
        setViewMode('drainage')
      }
      
      return response.data.project
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load project')
      return null
    }
  }, [projectId])

  // Fetch detailed report
  const fetchReport = async () => {
    if (!projectId) return
    
    try {
      const response = await analysisApi.getReport(projectId)
      setReport(response.data.report)
    } catch (err) {
      console.error('Failed to fetch report:', err)
    }
  }

  // Initial load
  useEffect(() => {
    const init = async () => {
      setLoading(true)
      const proj = await fetchProject()
      setLoading(false)
      
      // Start polling if processing
      if (proj?.status === 'processing') {
        setPollingActive(true)
      }
    }
    init()
  }, [fetchProject])

  // Polling effect
  useEffect(() => {
    if (!pollingActive || !projectId) return

    const interval = setInterval(async () => {
      try {
        const response = await analysisApi.getProjectStatus(projectId)
        const status = response.data
        
        if (status.latest_job) {
          setJob(status.latest_job)
        }
        
        if (status.status === 'completed') {
          setPollingActive(false)
          await fetchProject()
        } else if (status.status === 'failed') {
          setPollingActive(false)
          setError('Analysis failed. Please try again.')
          await fetchProject()
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [pollingActive, projectId, fetchProject])

  // Start analysis
  const startAnalysis = async () => {
    if (!projectId) return
    
    try {
      setIsRunningAnalysis(true)
      setError(null)
      
      const response = await analysisApi.start(projectId, {
        analysis_type: 'full_analysis'
      })
      
      setJob(response.data.job)
      setPollingActive(true)
      
      // Update project status locally
      if (project) {
        setProject({ ...project, status: 'processing' })
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to start analysis')
    } finally {
      setIsRunningAnalysis(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-navy/60">Loading project...</p>
        </div>
      </div>
    )
  }

  if (error && !project) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-navy mb-2">Error Loading Project</h2>
          <p className="text-navy/60 mb-6">{error || 'Project not found'}</p>
          <Link to="/dashboard/projects" className="btn-primary">
            Back to Projects
          </Link>
        </div>
      </div>
    )
  }

  if (!project) return null

  const hasResults = project.status === 'completed'
  const isProcessing = project.status === 'processing'
  const hasDTM = !!project.dtm_file_path
  const hasDTMVisualization = !!project.visualization_path || hasDTM

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link 
            to="/dashboard/projects" 
            className="p-2 hover:bg-white rounded-none transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-navy/60" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-navy">{project.name}</h1>
            <p className="text-navy/60">
              {project.description || 'Drainage Network Analysis'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {hasDTM && !isProcessing && (
            <button
              onClick={startAnalysis}
              disabled={isRunningAnalysis}
              className="btn-primary flex items-center gap-2"
            >
              {isRunningAnalysis ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  {hasResults ? 'Re-run Analysis' : 'Run Analysis'}
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-none p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" />
          <div>
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Processing status */}
      {isProcessing && (
        <div className="bg-white rounded-none p-6 border border-primary-500/20">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 bg-primary-500/20 rounded-full flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-navy">Analysis in Progress</h3>
              <p className="text-navy/60">{job?.current_step || 'Processing...'}</p>
            </div>
            <RefreshCw className="w-5 h-5 text-navy/60 animate-spin" />
          </div>
          
          <div className="w-full bg-neutral-100 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-primary-500 to-violet-500 transition-all duration-500"
              style={{ width: `${job?.progress || 0}%` }}
            />
          </div>
          <p className="text-sm text-navy/60 mt-2 ">{job?.progress || 0}% complete</p>
        </div>
      )}

      {/* No DTM warning */}
      {!hasDTM && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-none p-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center shrink-0">
              <MapPin className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-navy mb-1">No DTM File Uploaded</h3>
              <p className="text-navy/60 mb-4">
                Upload a Digital Terrain Model (DTM) file to begin drainage analysis.
              </p>
              <Link 
                to="/dashboard/projects/new"
                className="btn-primary inline-flex items-center gap-2"
              >
                Create New Project with DTM
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Results Statistics */}
      {hasResults && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard 
            icon={<Layers className="w-4 h-4 text-blue-400" />}
            label="Total Channels"
            value={report?.network_summary?.total_channels || project.total_channels || 0}
            bgColor="bg-blue-500/20"
          />
          <StatCard 
            icon={<Ruler className="w-4 h-4 text-primary-400" />}
            label="Total Length"
            value={`${(report?.network_summary?.total_length_km || project.total_length_km || 0).toFixed(1)} km`}
            bgColor="bg-primary-500/20"
          />
          <StatCard 
            icon={<MapPin className="w-4 h-4 text-green-400" />}
            label="Outlets"
            value={report?.network_summary?.outlets || project.total_outlets || 0}
            bgColor="bg-green-500/20"
          />
          <StatCard 
            icon={<Droplets className="w-4 h-4 text-violet-400" />}
            label="Peak Flow"
            value={`${(report?.hydraulics?.total_design_flow_m3s || project.peak_flow_m3s || 0).toFixed(2)} m³/s`}
            bgColor="bg-violet-500/20"
          />
          <StatCard 
            icon={<Activity className="w-4 h-4 text-cyan-400" />}
            label="Primary"
            value={report?.network_summary?.primary_channels || project.primary_count || 0}
            bgColor="bg-cyan-500/20"
          />
          <StatCard 
            icon={<Activity className="w-4 h-4 text-amber-400" />}
            label="Secondary"
            value={report?.network_summary?.secondary_channels || project.secondary_count || 0}
            bgColor="bg-amber-500/20"
          />
        </div>
      )}

      {/* Terrain Info */}
      {report?.terrain && (
        <div className="bg-white rounded-none p-6 border border-navy/10">
          <h3 className="text-lg font-semibold text-navy mb-4">Terrain Information</h3>
          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <span className="text-sm text-navy/60">Dimensions</span>
              <p className="text-navy font-medium">{report.terrain.dimensions}</p>
            </div>
            <div>
              <span className="text-sm text-navy/60">Resolution</span>
              <p className="text-navy font-medium">{report.terrain.resolution_m} m</p>
            </div>
            <div>
              <span className="text-sm text-navy/60">Elevation Range</span>
              <p className="text-navy font-medium">
                {report.terrain.elevation_min?.toFixed(1)} - {report.terrain.elevation_max?.toFixed(1)} m
              </p>
            </div>
            <div>
              <span className="text-sm text-navy/60">Relief</span>
              <p className="text-navy font-medium">{report.terrain.elevation_range?.toFixed(1)} m</p>
            </div>
          </div>
        </div>
      )}

      {/* Hydraulic Design Info */}
      {report?.hydraulics && (
        <div className="bg-white rounded-none p-6 border border-navy/10">
          <h3 className="text-lg font-semibold text-navy mb-4">Hydraulic Design</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <span className="text-sm text-navy/60">Design Method</span>
              <p className="text-navy font-medium">{report.hydraulics.design_method}</p>
            </div>
            <div>
              <span className="text-sm text-navy/60">Flow Routing</span>
              <p className="text-navy font-medium">{report.hydraulics.flow_routing}</p>
            </div>
            <div>
              <span className="text-sm text-navy/60">Pipe Sizing</span>
              <p className="text-navy font-medium">{report.hydraulics.pipe_sizing}</p>
            </div>
          </div>
        </div>
      )}

      {/* Channel Details */}
      {report?.channels && report.channels.length > 0 && (
        <div className="bg-white rounded-none border border-navy/10 overflow-hidden">
          <button
            onClick={() => setShowChannelDetails(!showChannelDetails)}
            className="w-full p-4 flex items-center justify-between hover:bg-neutral-100/50 transition-colors"
          >
            <h3 className="text-lg font-semibold text-navy">
              Channel Details ({report.channels.length} channels)
            </h3>
            {showChannelDetails ? (
              <ChevronUp className="w-5 h-5 text-navy/60" />
            ) : (
              <ChevronDown className="w-5 h-5 text-navy/60" />
            )}
          </button>
          
          {showChannelDetails && (
            <div className="p-4 pt-0 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-navy/10">
                    <th className="text-left py-2 px-3 text-navy/60 font-medium">Type</th>
                    <th className=" py-2 px-3 text-navy/60 font-medium">Length (m)</th>
                    <th className=" py-2 px-3 text-navy/60 font-medium">Slope (%)</th>
                    <th className=" py-2 px-3 text-navy/60 font-medium">Flow (m³/s)</th>
                    <th className=" py-2 px-3 text-navy/60 font-medium">Pipe (mm)</th>
                    <th className=" py-2 px-3 text-navy/60 font-medium">Velocity (m/s)</th>
                  </tr>
                </thead>
                <tbody>
                  {report.channels.slice(0, 20).map((channel, idx) => (
                    <tr key={idx} className="border-b border-navy/10/50 hover:bg-neutral-100/30">
                      <td className="py-2 px-3">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                          channel.type === 'primary' ? 'bg-blue-500/20 text-blue-400' :
                          channel.type === 'secondary' ? 'bg-cyan-500/20 text-cyan-400' :
                          'bg-neutral-200 text-navy-muted'
                        }`}>
                          {channel.type}
                        </span>
                      </td>
                      <td className="py-2 px-3  text-navy">{channel.length_m?.toFixed(1)}</td>
                      <td className="py-2 px-3  text-navy">{channel.slope_pct?.toFixed(2)}</td>
                      <td className="py-2 px-3  text-navy">{channel.peak_flow_m3s?.toFixed(3)}</td>
                      <td className="py-2 px-3  text-navy">{channel.pipe_diameter_mm}</td>
                      <td className="py-2 px-3  text-navy">{channel.velocity_ms?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {report.channels.length > 20 && (
                <p className="text-sm text-navy/60 mt-3 text-center">
                  Showing 20 of {report.channels.length} channels. Download full report for complete data.
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Visualization Section */}
      {hasDTMVisualization && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-navy">3D Visualization</h2>
            <VisualizationControls 
              mode={viewMode} 
              onModeChange={setViewMode}
            />
          </div>
          
          <DrainageViewer
            projectId={projectId!}
            mode={viewMode}
            className="h-[70vh]"
          />
        </div>
      )}

      {/* Reports & Downloads Section */}
      {hasResults && (
        <div className="bg-white rounded-none p-6 border border-navy/10">
          <h2 className="text-lg font-semibold text-navy mb-4 flex items-center gap-2">
            <Download className="w-5 h-5 text-primary-400" />
            Reports & Downloads
          </h2>
          
          <div className="grid md:grid-cols-3 gap-4">
            {/* JSON Report */}
            <a
              href={`/api/analysis/projects/${projectId}/download/report?token=${localStorage.getItem('token')}`}
              download
              className="flex items-center gap-4 p-4 bg-neutral-100/50 hover:bg-neutral-100 rounded-none border border-navy/20 transition-all hover:border-primary-500/50 group"
            >
              <div className="w-12 h-12 bg-blue-500/20 rounded-none flex items-center justify-center group-hover:scale-110 transition-transform">
                <FileText className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="font-medium text-navy">Analysis Report</h3>
                <p className="text-sm text-navy/60">Complete analysis in JSON format</p>
              </div>
            </a>

            {/* GeoJSON */}
            <a
              href={`/api/analysis/projects/${projectId}/download/geojson?token=${localStorage.getItem('token')}`}
              download
              className="flex items-center gap-4 p-4 bg-neutral-100/50 hover:bg-neutral-100 rounded-none border border-navy/20 transition-all hover:border-green-500/50 group"
            >
              <div className="w-12 h-12 bg-green-500/20 rounded-none flex items-center justify-center group-hover:scale-110 transition-transform">
                <FileJson className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 className="font-medium text-navy">GeoJSON Network</h3>
                <p className="text-sm text-navy/60">Drainage network for GIS</p>
              </div>
            </a>

            {/* CSV Data */}
            <a
              href={`/api/analysis/projects/${projectId}/download/csv?token=${localStorage.getItem('token')}`}
              download
              className="flex items-center gap-4 p-4 bg-neutral-100/50 hover:bg-neutral-100 rounded-none border border-navy/20 transition-all hover:border-violet-500/50 group"
            >
              <div className="w-12 h-12 bg-violet-500/20 rounded-none flex items-center justify-center group-hover:scale-110 transition-transform">
                <Layers className="w-6 h-6 text-violet-400" />
              </div>
              <div>
                <h3 className="font-medium text-navy">Channel Data (CSV)</h3>
                <p className="text-sm text-navy/60">Spreadsheet-compatible export</p>
              </div>
            </a>
          </div>
        </div>
      )}

      {/* Help section */}
      <div className="bg-white/50 rounded-none p-6 border border-navy/10">
        <h3 className="text-lg font-semibold text-navy mb-4">About the Analysis</h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-primary-400 mb-2">D∞ Flow Algorithm</h4>
            <p className="text-sm text-navy/60">
              Uses D-Infinity algorithm (Tarboton, 1997) for accurate flow distribution 
              across multiple downslope cells.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-primary-400 mb-2">Rational Method</h4>
            <p className="text-sm text-navy/60">
              Peak flow calculated using Q=CIA where C is runoff coefficient, 
              I is rainfall intensity, and A is catchment area.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-primary-400 mb-2">Manning's Equation</h4>
            <p className="text-sm text-navy/60">
              Pipe sizing and velocity validation using Manning's equation for 
              open channel and pipe flow calculations.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Stat Card Component
function StatCard({ icon, label, value, bgColor }: { 
  icon: React.ReactNode
  label: string
  value: string | number
  bgColor: string 
}) {
  return (
    <div className="bg-white rounded-none p-4 border border-navy/10">
      <div className="flex items-center gap-3 mb-2">
        <div className={`w-8 h-8 ${bgColor} rounded-none flex items-center justify-center`}>
          {icon}
        </div>
        <span className="text-sm text-navy/60">{label}</span>
      </div>
      <p className="text-2xl font-bold text-navy">{value}</p>
    </div>
  )
}
