import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  Search, 
  FolderOpen, 
  Clock, 
  CheckCircle2, 
  PlayCircle, 
  AlertCircle,
  MoreVertical,
  Trash2,
  Edit2,
  Share2,
  Map,
  Loader2
} from 'lucide-react'
import { projectsApi } from '../../services/api'

interface Project {
  id: string
  name: string
  description: string
  status: string
  created_at: string
  updated_at: string
  dtm_file_path?: string
  location_name?: string
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [openMenu, setOpenMenu] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await projectsApi.list()
      setProjects(response.data.projects || [])
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch projects')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return
    
    setDeletingId(id)
    try {
      await projectsApi.delete(id)
      setProjects(projects.filter(p => p.id !== id))
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete project')
    } finally {
      setDeletingId(null)
      setOpenMenu(null)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />
      case 'processing':
        return <PlayCircle className="w-4 h-4 text-blue-400" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <Clock className="w-4 h-4 text-navy/60" />
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'processing':
        return 'Processing'
      case 'failed':
        return 'Failed'
      case 'draft':
        return 'Draft'
      case 'dtm_ready':
        return 'Ready'
      default:
        return status
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          project.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">Projects</h1>
          <p className="text-navy/60">Manage your drainage analysis projects</p>
        </div>
        <Link to="/dashboard/projects/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Project
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-navy/60" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full pl-10"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-full sm:w-48"
        >
          <option value="all">All Status</option>
          <option value="draft">Draft</option>
          <option value="dtm_ready">Ready</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-none flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredProjects.length === 0 && (
        <div className="bg-white border border-navy/10 rounded-none p-12 text-center">
          <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FolderOpen className="w-8 h-8 text-navy/60" />
          </div>
          <h3 className="text-lg font-medium text-navy mb-2">
            {searchQuery || statusFilter !== 'all' ? 'No projects found' : 'No projects yet'}
          </h3>
          <p className="text-navy/60 mb-6">
            {searchQuery || statusFilter !== 'all' 
              ? 'Try adjusting your search or filter' 
              : 'Create your first project to get started with drainage analysis'}
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Link to="/dashboard/projects/new" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Create Your First Project
            </Link>
          )}
        </div>
      )}

      {/* Projects Grid */}
      {!loading && filteredProjects.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map(project => (
            <div 
              key={project.id}
              className="bg-white border border-navy/10 rounded-none p-5 hover:border-navy/20 transition-colors group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(project.status)}
                  <span className="text-sm text-navy/60">{getStatusLabel(project.status)}</span>
                </div>
                <div className="relative">
                  <button 
                    onClick={() => setOpenMenu(openMenu === project.id ? null : project.id)}
                    className="p-1.5 hover:bg-neutral-100 rounded-none transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <MoreVertical className="w-4 h-4 text-navy/60" />
                  </button>
                  
                  {openMenu === project.id && (
                    <>
                      <div 
                        className="fixed inset-0 z-10" 
                        onClick={() => setOpenMenu(null)}
                      />
                      <div className="absolute right-0 top-full mt-1 w-40 bg-neutral-100 border border-navy/20 rounded-none shadow-xl z-20 py-1">
                        <Link
                          to={`/dashboard/projects/${project.id}/analysis`}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-navy-muted hover:bg-neutral-200 w-full"
                        >
                          <Map className="w-4 h-4" />
                          View Analysis
                        </Link>
                        <button className="flex items-center gap-2 px-3 py-2 text-sm text-navy-muted hover:bg-neutral-200 w-full">
                          <Edit2 className="w-4 h-4" />
                          Edit
                        </button>
                        <button className="flex items-center gap-2 px-3 py-2 text-sm text-navy-muted hover:bg-neutral-200 w-full">
                          <Share2 className="w-4 h-4" />
                          Share
                        </button>
                        <button 
                          onClick={() => handleDelete(project.id)}
                          className="flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-neutral-200 w-full"
                          disabled={deletingId === project.id}
                        >
                          {deletingId === project.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Content */}
              <Link to={`/dashboard/projects/${project.id}/analysis`}>
                <h3 className="text-lg font-semibold text-navy mb-1 hover:text-primary-400 transition-colors">
                  {project.name}
                </h3>
              </Link>
              <p className="text-sm text-navy/60 line-clamp-2 mb-4">
                {project.description || 'No description'}
              </p>

              {/* Footer */}
              <div className="flex items-center justify-between text-xs text-dark-500">
                <span>{project.location_name || 'No location'}</span>
                <span>Created {formatDate(project.created_at)}</span>
              </div>

              {/* DTM Indicator */}
              {project.dtm_file_path && (
                <div className="mt-3 pt-3 border-t border-navy/10">
                  <span className="inline-flex items-center gap-1.5 text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded">
                    <CheckCircle2 className="w-3 h-3" />
                    DTM Uploaded
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
