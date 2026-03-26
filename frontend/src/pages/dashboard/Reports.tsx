import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  FileText, 
  Download, 
  Loader2, 
  CheckCircle, 
  Clock, 
  FileJson, 
  FileCode,
  ArrowRight,
  Droplets,
  Building2,
  Leaf,
  FileCheck,
  Users,
  Wrench
} from 'lucide-react'
import { projectsApi } from '../../services/api'

interface Project {
  id: string
  name: string
  status: string
  created_at: string
  total_channels?: number
  total_length_km?: number
}

interface ReportTemplate {
  id: string
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  sections: string[]
}

const reportTemplates: ReportTemplate[] = [
  {
    id: 'engineering',
    name: 'Engineering Design Report',
    description: 'Comprehensive technical report with calculations and specifications',
    icon: Building2,
    sections: ['executive_summary', 'design_parameters', 'hydrological_analysis', 'hydraulic_design', 'materials', 'cost_estimate']
  },
  {
    id: 'construction',
    name: 'Construction Documentation',
    description: 'Detailed construction plans and specifications',
    icon: Wrench,
    sections: ['project_overview', 'site_preparation', 'materials_list', 'construction_sequence', 'quality_control']
  },
  {
    id: 'environmental',
    name: 'Environmental Assessment',
    description: 'Environmental impact analysis and mitigation measures',
    icon: Leaf,
    sections: ['existing_conditions', 'impact_analysis', 'mitigation_measures', 'monitoring_plan']
  },
  {
    id: 'permit',
    name: 'Permit Application Package',
    description: 'Documentation for regulatory permit applications',
    icon: FileCheck,
    sections: ['application_form', 'project_description', 'design_drawings', 'calculations']
  },
  {
    id: 'client',
    name: 'Client Presentation',
    description: 'Executive summary for client presentations',
    icon: Users,
    sections: ['overview', 'key_findings', 'recommendations', 'cost_summary']
  }
]

export default function Reports() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generatedReport, setGeneratedReport] = useState<string | null>(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await projectsApi.list()
      // Only show completed projects
      const completedProjects = response.data.projects.filter(
        (p: Project) => p.status === 'completed'
      )
      setProjects(completedProjects)
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async () => {
    if (!selectedProject || !selectedTemplate) return
    
    setGenerating(true)
    try {
      const response = await fetch(`/api/v1/reports/projects/${selectedProject}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          template: selectedTemplate,
          format: 'html'
        })
      })
      
      const data = await response.json()
      if (data.download_url) {
        setGeneratedReport(data.download_url)
      }
    } catch (err) {
      console.error('Failed to generate report:', err)
    } finally {
      setGenerating(false)
    }
  }

  const completedProjects = projects.filter(p => p.status === 'completed')

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-navy flex items-center gap-3">
          <FileText className="w-7 h-7 text-primary-500" />
          Reports
        </h1>
        <p className="text-navy/60 mt-2">
          Generate professional reports from your completed drainage analysis projects
        </p>
      </div>

      {/* Project Selection */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold text-navy mb-4">1. Select Project</h2>
        
        {completedProjects.length === 0 ? (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-dark-500 mx-auto mb-3" />
            <p className="text-navy/60">No completed projects available</p>
            <p className="text-dark-500 text-sm mt-1">
              Complete a drainage analysis to generate reports
            </p>
            <Link to="/dashboard/projects/new" className="btn-primary mt-4 inline-block">
              Create New Project
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedProjects.map((project) => (
              <button
                key={project.id}
                onClick={() => setSelectedProject(project.id)}
                className={`p-4 rounded-none border text-left transition-all ${
                  selectedProject === project.id
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-navy/10 hover:border-navy/20 bg-white/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-navy">{project.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <CheckCircle className="w-3 h-3 text-primary-500" />
                      <span className="text-xs text-navy/60">Completed</span>
                    </div>
                  </div>
                  {selectedProject === project.id && (
                    <CheckCircle className="w-5 h-5 text-primary-500" />
                  )}
                </div>
                {(project.total_channels || project.total_length_km) && (
                  <div className="flex items-center gap-3 mt-3 text-xs text-navy/60">
                    <span className="flex items-center gap-1">
                      <Droplets className="w-3 h-3" />
                      {project.total_channels} channels
                    </span>
                    <span>{project.total_length_km?.toFixed(2)} km</span>
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Template Selection */}
      {selectedProject && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-navy mb-4">2. Select Report Template</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reportTemplates.map((template) => {
              const Icon = template.icon
              return (
                <button
                  key={template.id}
                  onClick={() => setSelectedTemplate(template.id)}
                  className={`p-4 rounded-none border text-left transition-all ${
                    selectedTemplate === template.id
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-navy/10 hover:border-navy/20 bg-white/50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-none ${
                      selectedTemplate === template.id ? 'bg-primary-500/20' : 'bg-neutral-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        selectedTemplate === template.id ? 'text-primary-400' : 'text-navy/60'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-navy">{template.name}</h3>
                      <p className="text-xs text-navy/60 mt-1">{template.description}</p>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Generate Button */}
      {selectedProject && selectedTemplate && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-navy mb-4">3. Generate Report</h2>
          
          <div className="flex items-center gap-4 flex-wrap">
            <button
              onClick={generateReport}
              disabled={generating}
              className="btn-primary flex items-center gap-2"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Generate Report
                </>
              )}
            </button>
            
            <div className="flex items-center gap-2">
              <button className="btn-secondary flex items-center gap-2 text-sm">
                <FileCode className="w-4 h-4" />
                HTML
              </button>
              <button className="btn-secondary flex items-center gap-2 text-sm">
                <FileJson className="w-4 h-4" />
                JSON
              </button>
            </div>
          </div>
          
          {generatedReport && (
            <div className="mt-4 p-4 bg-primary-500/10 border border-primary-500/20 rounded-none">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-primary-500" />
                  <span className="text-navy">Report generated successfully!</span>
                </div>
                <a
                  href={generatedReport}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary text-sm flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download
                </a>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Reports */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-navy">Recent Reports</h2>
          <Link 
            to="/dashboard/projects" 
            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            View All Projects
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        
        <div className="text-center py-8 text-navy/60">
          <FileText className="w-12 h-12 text-dark-600 mx-auto mb-3" />
          <p>Generated reports will appear here</p>
        </div>
      </div>
    </div>
  )
}
