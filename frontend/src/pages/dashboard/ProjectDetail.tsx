import { useState, useEffect, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  MapPin, 
  Calendar, 
  Clock, 
  Play, 
  Loader2, 
  Download,
  Share2,
  Settings,
  Trash2,
  CheckCircle,
  AlertCircle,
  Activity,
  Layers,
  Droplets,
  TrendingDown,
  FileText,
  BarChart3,
  ChevronRight,
  Gauge,
  Ruler,
  Mountain
} from 'lucide-react'
import DrainageViewer from '../../components/DrainageViewer'
import { projectsApi, analysisApi } from '../../services/api'

interface Project {
  id: string
  name: string
  description?: string
  status: string
  location_name?: string
  created_at: string
  updated_at: string
  dtm_file_path?: string
  visualization_path?: string
  total_channels?: number
  total_length_km?: number
  total_outlets?: number
  peak_flow_m3s?: number
  primary_count?: number
  secondary_count?: number
  tertiary_count?: number
  primary_length_m?: number
  secondary_length_m?: number
  tertiary_length_m?: number
  design_storm_years?: number
  runoff_coefficient?: number
  flow_algorithm?: string
}

interface DrainageReport {
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
    total_design_flow_m3s: number
  }
}

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [report, setReport] = useState<DrainageReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'drainage' | 'dtm'>('dtm')
  const [isRunningAnalysis, setIsRunningAnalysis] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [pollingActive, setPollingActive] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const fetchProject = useCallback(async () => {
    if (!projectId) return
    try {
      const response = await projectsApi.get(projectId)
      setProject(response.data.project)
      
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

  const fetchReport = async () => {
    if (!projectId) return
    try {
      const response = await analysisApi.getReport(projectId)
      setReport(response.data.report)
    } catch (err) {
      console.error('Failed to fetch report:', err)
    }
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      const proj = await fetchProject()
      setLoading(false)
      
      if (proj?.status === 'processing') {
        setPollingActive(true)
      }
    }
    init()
  }, [fetchProject])

  useEffect(() => {
    if (!pollingActive || !projectId) return

    const interval = setInterval(async () => {
      try {
        const response = await analysisApi.getProjectStatus(projectId)
        const status = response.data
        
        if (status.latest_job) {
          setAnalysisProgress(status.latest_job.progress || 0)
        }
        
        if (status.status === 'completed') {
          setPollingActive(false)
          setIsRunningAnalysis(false)
          await fetchProject()
        } else if (status.status === 'failed') {
          setPollingActive(false)
          setIsRunningAnalysis(false)
          setError('Analysis failed. Please try again.')
          await fetchProject()
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [pollingActive, projectId, fetchProject])

  const startAnalysis = async () => {
    if (!projectId) return
    
    try {
      setIsRunningAnalysis(true)
      setError(null)
      setAnalysisProgress(0)
      
      await analysisApi.start(projectId, { analysis_type: 'full_analysis' })
      setPollingActive(true)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to start analysis')
      setIsRunningAnalysis(false)
    }
  }

  const handleDelete = async () => {
    if (!projectId) return
    
    try {
      await projectsApi.delete(projectId)
      navigate('/dashboard/projects')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete project')
    }
    setShowDeleteModal(false)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="badge-success flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5" />
            Completed
          </span>
        )
      case 'processing':
        return (
          <span className="badge-primary flex items-center gap-1.5">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            Processing
          </span>
        )
      case 'failed':
        return (
          <span className="badge-error flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5" />
            Failed
          </span>
        )
      case 'draft':
        return (
          <span className="badge-secondary flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            Draft
          </span>
        )
      case 'dtm_ready':
        return (
          <span className="badge-primary flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5" />
            Ready for Analysis
          </span>
        )
      default:
        return (
          <span className="badge-secondary flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {status}
          </span>
        )
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-20">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-white mb-2">Project Not Found</h3>
        <p className="text-slate-400 mb-6">{error || 'The project you are looking for does not exist.'}</p>
        <Link to="/dashboard/projects" className="btn-primary">
          Back to Projects
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <Link 
            to="/dashboard/projects" 
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors mt-1"
          >
            <ArrowLeft className="w-5 h-5 text-slate-400" />
          </Link>
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-white">{project.name}</h1>
              {getStatusBadge(project.status)}
            </div>
            {project.description && (
              <p className="text-slate-400 max-w-2xl">{project.description}</p>
            )}
            <div className="flex items-center gap-4 mt-3 text-sm text-slate-500">
              {project.location_name && (
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  {project.location_name}
                </span>
              )}
              <span className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                Created {formatDate(project.created_at)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {(project.status === 'draft' || project.status === 'dtm_ready') && project.dtm_file_path && (
            <button
              onClick={startAnalysis}
              disabled={isRunningAnalysis}
              className="btn-primary"
            >
              {isRunningAnalysis ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Analysis
                </>
              )}
            </button>
          )}
          {project.status === 'completed' && (
            <Link
              to={`/dashboard/analysis/${project.id}`}
              className="btn-primary"
            >
              <BarChart3 className="w-4 h-4" />
              View Results
            </Link>
          )}
          <button className="btn-ghost">
            <Share2 className="w-4 h-4" />
          </button>
          <button className="btn-ghost">
            <Settings className="w-4 h-4" />
          </button>
          <button 
            onClick={() => setShowDeleteModal(true)}
            className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/10"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Analysis Progress */}
      {(isRunningAnalysis || project.status === 'processing') && (
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center">
              <Activity className="w-5 h-5 text-primary-400 animate-pulse" />
            </div>
            <div>
              <h3 className="font-medium text-white">Analysis in Progress</h3>
              <p className="text-sm text-slate-400">Processing drainage network...</p>
            </div>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-primary-500 to-violet-500 transition-all duration-300"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
          <p className="text-sm text-slate-500 mt-2">{analysisProgress}% complete</p>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visualization */}
        <div className="lg:col-span-2">
          <div className="card p-0 overflow-hidden">
            {/* View Mode Tabs */}
            <div className="flex items-center gap-2 p-4 border-b border-slate-800/50">
              <button
                onClick={() => setViewMode('dtm')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  viewMode === 'dtm' 
                    ? 'bg-slate-800 text-white' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Mountain className="w-4 h-4 inline mr-2" />
                Terrain
              </button>
              <button
                onClick={() => setViewMode('drainage')}
                disabled={project.status !== 'completed'}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  viewMode === 'drainage' 
                    ? 'bg-slate-800 text-white' 
                    : 'text-slate-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                <Droplets className="w-4 h-4 inline mr-2" />
                Drainage Network
              </button>
            </div>

            {/* Viewer */}
            {project.dtm_file_path ? (
              <DrainageViewer 
                projectId={project.id} 
                mode={viewMode}
                className="h-[500px]"
              />
            ) : (
              <div className="h-[500px] flex items-center justify-center bg-slate-900/50">
                <div className="text-center">
                  <Layers className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-slate-400">No DTM file uploaded</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Project Config */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-slate-400" />
              Configuration
            </h3>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-400">Flow Algorithm</dt>
                <dd className="text-white font-medium">
                  {project.flow_algorithm === 'dinf' ? 'D-Infinity' : 'D8'}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-400">Design Storm</dt>
                <dd className="text-white font-medium">{project.design_storm_years || 10} years</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-400">Runoff Coefficient</dt>
                <dd className="text-white font-medium">{project.runoff_coefficient || 0.5}</dd>
              </div>
            </dl>
          </div>

          {/* Terrain Info */}
          {report?.terrain && (
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Mountain className="w-5 h-5 text-slate-400" />
                Terrain Info
              </h3>
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-400">Dimensions</dt>
                  <dd className="text-white font-medium">{report.terrain.dimensions}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-400">Resolution</dt>
                  <dd className="text-white font-medium">{report.terrain.resolution_m?.toFixed(2)} m</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-400">Elevation Range</dt>
                  <dd className="text-white font-medium">
                    {report.terrain.elevation_min?.toFixed(1)} - {report.terrain.elevation_max?.toFixed(1)} m
                  </dd>
                </div>
              </dl>
            </div>
          )}

          {/* Network Summary */}
          {project.status === 'completed' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Droplets className="w-5 h-5 text-cyan-400" />
                Network Summary
              </h3>
              
              {/* Drainage Type Breakdown */}
              <div className="space-y-4">
                {/* Primary */}
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-sky-600" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">Primary</span>
                      <span className="text-white font-medium">
                        {project.primary_count || 0} channels
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {((project.primary_length_m || 0) / 1000).toFixed(2)} km
                    </p>
                  </div>
                </div>

                {/* Secondary */}
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-teal-500" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">Secondary</span>
                      <span className="text-white font-medium">
                        {project.secondary_count || 0} channels
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {((project.secondary_length_m || 0) / 1000).toFixed(2)} km
                    </p>
                  </div>
                </div>

                {/* Tertiary */}
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">Tertiary</span>
                      <span className="text-white font-medium">
                        {project.tertiary_count || 0} channels
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {((project.tertiary_length_m || 0) / 1000).toFixed(2)} km
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Total Length</span>
                    <span className="text-white font-semibold">
                      {project.total_length_km?.toFixed(2) || 0} km
                    </span>
                  </div>
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-slate-400">Total Outlets</span>
                    <span className="text-white font-semibold">
                      {project.total_outlets || 0}
                    </span>
                  </div>
                </div>
              </div>

              <Link 
                to={`/dashboard/analysis/${project.id}`}
                className="btn-outline w-full mt-4"
              >
                View Detailed Analysis
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          )}

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {project.status === 'completed' && (
                <>
                  <button className="btn-ghost w-full justify-start">
                    <Download className="w-4 h-4" />
                    Download Report (JSON)
                  </button>
                  <button className="btn-ghost w-full justify-start">
                    <FileText className="w-4 h-4" />
                    Export GeoJSON
                  </button>
                </>
              )}
              <button className="btn-ghost w-full justify-start">
                <Share2 className="w-4 h-4" />
                Share Project
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Delete Project</h3>
                <p className="text-sm text-slate-400">This action cannot be undone</p>
              </div>
            </div>
            <p className="text-slate-300 mb-6">
              Are you sure you want to delete <strong>{project.name}</strong>? 
              All associated data and analysis results will be permanently removed.
            </p>
            <div className="flex gap-3">
              <button 
                onClick={() => setShowDeleteModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button 
                onClick={handleDelete}
                className="btn flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                Delete Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
