import { useState, useRef, useEffect } from 'react'
import { MapPin, Layers, Maximize2, RefreshCw, Mountain } from 'lucide-react'

interface DrainageViewerProps {
  projectId: string
  mode?: 'drainage' | 'dtm'
  className?: string
  onLoad?: () => void
  onError?: (error: string) => void
}

export default function DrainageViewer({ 
  projectId, 
  mode = 'drainage',
  className = '',
  onLoad,
  onError 
}: DrainageViewerProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Determine the endpoint based on mode
  const getVisualizationUrl = () => {
    const baseUrl = import.meta.env.VITE_API_URL || ''
    const token = localStorage.getItem('token')
    
    switch (mode) {
      case 'dtm':
        return `${baseUrl}/api/analysis/projects/${projectId}/raw-dtm?token=${token}`
      case 'drainage':
      default:
        return `${baseUrl}/api/analysis/projects/${projectId}/visualization?token=${token}`
    }
  }

  useEffect(() => {
    setLoading(true)
    setError(null)
  }, [projectId, mode])

  const handleIframeLoad = () => {
    setLoading(false)
    onLoad?.()
  }

  const handleIframeError = () => {
    const errorMsg = 'Failed to load visualization'
    setError(errorMsg)
    setLoading(false)
    onError?.(errorMsg)
  }

  const toggleFullscreen = () => {
    if (!containerRef.current) return

    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
  }

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  const refresh = () => {
    if (iframeRef.current) {
      setLoading(true)
      iframeRef.current.src = getVisualizationUrl()
    }
  }

  return (
    <div 
      ref={containerRef}
      className={`relative bg-dark-900 rounded-xl overflow-hidden border border-dark-700 ${className}`}
    >
      {/* Toolbar */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
        <button
          onClick={refresh}
          className="p-2 bg-dark-800/90 hover:bg-dark-700 rounded-lg backdrop-blur-sm transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4 text-dark-300" />
        </button>
        <button
          onClick={toggleFullscreen}
          className="p-2 bg-dark-800/90 hover:bg-dark-700 rounded-lg backdrop-blur-sm transition-colors"
          title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
        >
          <Maximize2 className="w-4 h-4 text-dark-300" />
        </button>
      </div>

      {/* Mode indicator */}
      <div className="absolute top-4 left-4 z-20">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-800/90 rounded-lg backdrop-blur-sm">
          {mode === 'dtm' && (
            <>
              <Mountain className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-dark-200">Digital Terrain Model</span>
            </>
          )}
          {mode === 'drainage' && (
            <>
              <Layers className="w-4 h-4 text-green-400" />
              <span className="text-sm text-dark-200">Drainage Network</span>
            </>
          )}
        </div>
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-dark-900/80 backdrop-blur-sm">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-dark-300">Loading visualization...</p>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-dark-900/80 backdrop-blur-sm">
          <div className="text-center max-w-md px-6">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">⚠️</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Visualization Error</h3>
            <p className="text-dark-400 mb-4">{error}</p>
            <button 
              onClick={refresh}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Iframe container */}
      <iframe
        ref={iframeRef}
        src={getVisualizationUrl()}
        className="w-full h-full min-h-[500px] border-0"
        onLoad={handleIframeLoad}
        onError={handleIframeError}
        title="Drainage Visualization"
        allow="fullscreen"
      />
    </div>
  )
}


interface VisualizationControlsProps {
  mode: 'drainage' | 'dtm'
  onModeChange: (mode: 'drainage' | 'dtm') => void
}

export function VisualizationControls({ mode, onModeChange }: VisualizationControlsProps) {
  return (
    <div className="flex items-center gap-2 p-1 bg-dark-800 rounded-lg">
      <button
        onClick={() => onModeChange('drainage')}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
          mode === 'drainage' 
            ? 'bg-primary-600 text-white shadow-lg' 
            : 'text-dark-300 hover:text-white hover:bg-dark-700'
        }`}
      >
        <span className="flex items-center gap-2">
          <Layers className="w-4 h-4" />
          Drainage Network
        </span>
      </button>
      <button
        onClick={() => onModeChange('dtm')}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
          mode === 'dtm' 
            ? 'bg-primary-600 text-white shadow-lg' 
            : 'text-dark-300 hover:text-white hover:bg-dark-700'
        }`}
      >
        <span className="flex items-center gap-2">
          <Mountain className="w-4 h-4" />
          DTM View
        </span>
      </button>
    </div>
  )
}
