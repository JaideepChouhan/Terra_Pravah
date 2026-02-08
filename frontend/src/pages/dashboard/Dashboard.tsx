import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  FolderIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  PlusIcon,
  PlayIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '../../store/authStore'
import { projectsApi, analysisApi } from '../../services/api'

interface DashboardStats {
  totalProjects: number
  activeAnalyses: number
  reportsGenerated: number
  storageUsed: string
  projectsChange: number
  analysesChange: number
}

interface RecentProject {
  id: string
  name: string
  status: string
  updatedAt: string
  thumbnail?: string
}

interface RecentActivity {
  id: string
  type: 'analysis' | 'report' | 'project' | 'share'
  message: string
  timestamp: string
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats>({
    totalProjects: 0,
    activeAnalyses: 0,
    reportsGenerated: 0,
    storageUsed: '0 MB',
    projectsChange: 0,
    analysesChange: 0,
  })
  const [recentProjects, setRecentProjects] = useState<RecentProject[]>([])
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Load projects
      const projectsResponse = await projectsApi.list({ per_page: 5 })
      setRecentProjects(
        projectsResponse.data.projects.map((p: any) => ({
          id: p.id,
          name: p.name,
          status: p.status,
          updatedAt: p.updated_at,
          thumbnail: p.thumbnail_url,
        }))
      )

      // Set mock stats for now
      setStats({
        totalProjects: projectsResponse.data.total || 0,
        activeAnalyses: 2,
        reportsGenerated: 15,
        storageUsed: '2.4 GB',
        projectsChange: 12,
        analysesChange: -5,
      })

      // Mock recent activity
      setRecentActivity([
        {
          id: '1',
          type: 'analysis',
          message: 'Drainage analysis completed for Site A',
          timestamp: '2 hours ago',
        },
        {
          id: '2',
          type: 'report',
          message: 'Engineering report generated',
          timestamp: '5 hours ago',
        },
        {
          id: '3',
          type: 'project',
          message: 'New project "Downtown Expansion" created',
          timestamp: '1 day ago',
        },
        {
          id: '4',
          type: 'share',
          message: 'Project shared with team member',
          timestamp: '2 days ago',
        },
      ])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const statCards = [
    {
      name: 'Total Projects',
      value: stats.totalProjects,
      change: stats.projectsChange,
      icon: FolderIcon,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      name: 'Active Analyses',
      value: stats.activeAnalyses,
      change: stats.analysesChange,
      icon: ChartBarIcon,
      color: 'from-purple-500 to-pink-500',
    },
    {
      name: 'Reports Generated',
      value: stats.reportsGenerated,
      change: 8,
      icon: DocumentTextIcon,
      color: 'from-green-500 to-emerald-500',
    },
    {
      name: 'Storage Used',
      value: stats.storageUsed,
      change: null,
      icon: ClockIcon,
      color: 'from-orange-500 to-red-500',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'badge-success'
      case 'completed':
        return 'badge-primary'
      case 'draft':
        return 'badge-secondary'
      case 'archived':
        return 'badge-warning'
      default:
        return 'badge-secondary'
    }
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome back, {user?.firstName || 'Engineer'}! 👋
          </h1>
          <p className="text-dark-400 mt-1">
            Here's what's happening with your drainage projects.
          </p>
        </div>
        <Link to="/dashboard/projects/new" className="btn-primary">
          <PlusIcon className="w-5 h-5 mr-2" />
          New Project
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-start justify-between">
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-r ${stat.color} p-0.5`}
              >
                <div className="w-full h-full bg-dark-800 rounded-lg flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              {stat.change !== null && (
                <span
                  className={`flex items-center text-sm font-medium ${
                    stat.change >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {stat.change >= 0 ? (
                    <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
                  ) : (
                    <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
                  )}
                  {Math.abs(stat.change)}%
                </span>
              )}
            </div>
            <div className="mt-4">
              <h3 className="text-2xl font-bold">{stat.value}</h3>
              <p className="text-dark-400 text-sm">{stat.name}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Projects */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Recent Projects</h2>
            <Link to="/dashboard/projects" className="text-sm text-primary-400 hover:text-primary-300">
              View all →
            </Link>
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-4 p-4 rounded-lg bg-dark-700/50">
                  <div className="w-12 h-12 skeleton rounded-lg" />
                  <div className="flex-1">
                    <div className="h-4 w-32 skeleton rounded mb-2" />
                    <div className="h-3 w-24 skeleton rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : recentProjects.length > 0 ? (
            <div className="space-y-3">
              {recentProjects.map((project) => (
                <Link
                  key={project.id}
                  to={`/dashboard/projects/${project.id}`}
                  className="flex items-center gap-4 p-4 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
                >
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-white font-bold">
                    {project.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium truncate">{project.name}</h3>
                    <p className="text-sm text-dark-400">Updated {project.updatedAt}</p>
                  </div>
                  <span className={getStatusColor(project.status)}>{project.status}</span>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FolderIcon className="w-12 h-12 text-dark-600 mx-auto mb-4" />
              <p className="text-dark-400 mb-4">No projects yet</p>
              <Link to="/dashboard/projects/new" className="btn-primary">
                Create Your First Project
              </Link>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex gap-3">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    activity.type === 'analysis'
                      ? 'bg-purple-500/20 text-purple-400'
                      : activity.type === 'report'
                      ? 'bg-green-500/20 text-green-400'
                      : activity.type === 'project'
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'bg-orange-500/20 text-orange-400'
                  }`}
                >
                  {activity.type === 'analysis' ? (
                    <ChartBarIcon className="w-4 h-4" />
                  ) : activity.type === 'report' ? (
                    <DocumentTextIcon className="w-4 h-4" />
                  ) : activity.type === 'project' ? (
                    <FolderIcon className="w-4 h-4" />
                  ) : (
                    <PlayIcon className="w-4 h-4" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-dark-200 truncate">{activity.message}</p>
                  <p className="text-xs text-dark-500">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-6">Quick Actions</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/dashboard/projects/new"
            className="flex items-center gap-3 p-4 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
              <PlusIcon className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h3 className="font-medium">New Project</h3>
              <p className="text-sm text-dark-400">Start fresh</p>
            </div>
          </Link>
          <Link
            to="/dashboard/analysis"
            className="flex items-center gap-3 p-4 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <ChartBarIcon className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="font-medium">Run Analysis</h3>
              <p className="text-sm text-dark-400">Process data</p>
            </div>
          </Link>
          <Link
            to="/dashboard/reports"
            className="flex items-center gap-3 p-4 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
              <DocumentTextIcon className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h3 className="font-medium">Generate Report</h3>
              <p className="text-sm text-dark-400">Export results</p>
            </div>
          </Link>
          <Link
            to="/dashboard/teams"
            className="flex items-center gap-3 p-4 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <FolderIcon className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="font-medium">Invite Team</h3>
              <p className="text-sm text-dark-400">Collaborate</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
