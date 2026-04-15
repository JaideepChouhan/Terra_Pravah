import { useState, useRef, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  Upload, 
  FileUp, 
  Map, 
  Settings2, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  X,
  FileText,
  Layers
} from 'lucide-react'
import { projectsApi, uploadsApi } from '../../services/api'

interface FileInfo {
  name: string
  size: number
  type: string
  extension: string
}

type Step = 'details' | 'upload' | 'configure' | 'complete'

export default function NewProject() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Step tracking
  const [currentStep, setCurrentStep] = useState<Step>('details')
  
  // Form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [locationName, setLocationName] = useState('')
  
  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileInfo, setFileInfo] = useState<FileInfo | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  
  // Configuration state
  const [designStormYears, setDesignStormYears] = useState(10)
  const [runoffCoefficient, setRunoffCoefficient] = useState(0.5)
  const [flowAlgorithm, setFlowAlgorithm] = useState('d8')  // D8 is faster default
  const [dtmResolution, setDtmResolution] = useState(1.0)
  const [epsgCode, setEpsgCode] = useState('')
  
  // Status
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [createdProjectId, setCreatedProjectId] = useState<string | null>(null)

  // File validation - simplified to rely more on backend validation
  const validateFile = (file: File): string | null => {
    const maxSize = 5000 * 1024 * 1024 // 5000MB = 5GB
    
    // Basic size check
    if (file.size > maxSize) {
      return 'File too large. Maximum size is 5GB'
    }
    
    // Basic extension check (backend will do comprehensive validation)
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    const commonExtensions = ['.tif', '.tiff', '.las', '.laz', '.geotiff', '.img', '.asc', '.grd', '.dem']
    
    if (!commonExtensions.includes(ext)) {
      return 'Unsupported file format. Please upload a raster file (GeoTIFF, COG, TIFF, etc.) or LiDAR file (LAS, LAZ)'
    }
    
    return null
  }

  const getFileExtension = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    return ext ? `.${ext}` : ''
  }

  const isLidarFile = (file: File | null) => {
    if (!file) return false
    const ext = getFileExtension(file.name)
    return ext === '.las' || ext === '.laz'
  }

  // Handle file selection
  const handleFileSelect = (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }
    
    setSelectedFile(file)
    setFileInfo({
      name: file.name,
      size: file.size,
      type: file.type || 'application/octet-stream',
      extension: getFileExtension(file.name)
    })
    setError(null)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileSelect(file)
  }

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }, [])

  // Step navigation
  const goToStep = (step: Step) => {
    setError(null)
    setCurrentStep(step)
  }

  // Create project and upload file
  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('Project name is required')
      return
    }
    
    if (!selectedFile) {
      setError('Please upload a terrain file')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      // Step 1: Create project
      const projectResponse = await projectsApi.create({
        name: name.trim(),
        description: description.trim(),
        location_name: locationName.trim() || undefined,
        design_storm_years: designStormYears,
        runoff_coefficient: runoffCoefficient,
        flow_algorithm: flowAlgorithm
      })
      
      const projectId = projectResponse.data.project.id
      setCreatedProjectId(projectId)
      
      // Step 2: Upload terrain file / generate DTM
      setIsUploading(true)

      if (isLidarFile(selectedFile)) {
        const uploadResponse = await uploadsApi.uploadLAS(projectId, selectedFile, (progress) => {
          setUploadProgress(progress)
        })

        setUploadProgress(100)

        const uploadedFilename = uploadResponse.data?.file?.name
        if (!uploadedFilename) {
          throw new Error('LAS upload completed but filename was not returned by server')
        }

        await uploadsApi.buildDTMFromLAS({
          project_id: projectId,
          filename: uploadedFilename,
          resolution: dtmResolution,
          epsg: epsgCode.trim() || undefined,
        })
      } else {
        await uploadsApi.uploadDTM(projectId, selectedFile, (progress) => {
          setUploadProgress(progress)
        })
      }
      
      setIsUploading(false)
      setCurrentStep('complete')
      
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create project')
      setIsSubmitting(false)
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  // Step indicator
  const steps = [
    { id: 'details', label: 'Project Details', icon: FileText },
    { id: 'upload', label: 'Upload DTM', icon: Upload },
    { id: 'configure', label: 'Configure', icon: Settings2 },
    { id: 'complete', label: 'Complete', icon: CheckCircle }
  ]

  const stepOrder = ['details', 'upload', 'configure', 'complete']
  const currentIndex = stepOrder.indexOf(currentStep)

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link 
          to="/dashboard/projects" 
          className="p-2 hover:bg-white rounded-none transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-navy/60" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-navy">Create New Project</h1>
          <p className="text-navy/60">Upload your LiDAR data and configure analysis settings</p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center justify-between mb-10 px-4">
        {steps.map((step, index) => {
          const isActive = step.id === currentStep
          const isCompleted = stepOrder.indexOf(step.id) < currentIndex
          const Icon = step.icon
          
          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                  isActive 
                    ? 'bg-primary-600 text-navy  shadow-primary-500/30' 
                    : isCompleted
                      ? 'bg-green-500 text-navy'
                      : 'bg-white text-navy/60'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span className={`mt-2 text-sm ${isActive ? 'text-navy font-medium' : 'text-navy/60'}`}>
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-20 h-0.5 mx-2 ${
                  stepOrder.indexOf(step.id) < currentIndex 
                    ? 'bg-green-500' 
                    : 'bg-neutral-100'
                }`} />
              )}
            </div>
          )
        })}
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-none flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-red-400">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="ml-auto">
            <X className="w-4 h-4 text-red-400" />
          </button>
        </div>
      )}

      {/* Step Content */}
      <div className="bg-white rounded-none border border-navy/10 p-8">
        
        {/* Step 1: Project Details */}
        {currentStep === 'details' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-navy mb-2">Project Details</h2>
              <p className="text-navy/60">Enter basic information about your drainage project</p>
            </div>
            
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Project Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Downtown Drainage Analysis"
                  className="input w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of the project area and objectives..."
                  rows={3}
                  className="input w-full resize-none"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Location Name
                </label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  placeholder="e.g., Mumbai, Maharashtra"
                  className="input w-full"
                />
              </div>
            </div>
            
            <div className="flex justify-end pt-4">
              <button
                onClick={() => {
                  if (!name.trim()) {
                    setError('Project name is required')
                    return
                  }
                  goToStep('upload')
                }}
                className="btn-primary"
              >
                Continue to Upload
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Upload DTM */}
        {currentStep === 'upload' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-navy mb-2">Upload Terrain File</h2>
              <p className="text-navy/60">Upload GeoTIFF directly, or upload LAS/LAZ to generate DTM automatically</p>
            </div>
            
            {/* File drop zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`
                relative border-2 border-dashed rounded-none p-12 text-center cursor-pointer transition-all
                ${isDragging 
                  ? 'border-primary-500 bg-primary-500/10' 
                  : selectedFile
                    ? 'border-green-500 bg-green-500/5'
                    : 'border-navy/20 hover:border-dark-500 hover:bg-neutral-100/50'
                }
              `}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".tif,.tiff,.las,.laz"
                onChange={handleFileInputChange}
                className="hidden"
              />
              
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                    <Layers className="w-8 h-8 text-green-400" />
                  </div>
                  <div>
                    <p className="text-navy font-medium">{fileInfo?.name}</p>
                    <p className="text-navy/60 text-sm">{formatFileSize(fileInfo?.size || 0)}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedFile(null)
                      setFileInfo(null)
                    }}
                    className="text-sm text-navy/60 hover:text-navy underline"
                  >
                    Choose a different file
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto">
                    <FileUp className="w-8 h-8 text-navy/60" />
                  </div>
                  <div>
                    <p className="text-navy font-medium">
                      {isDragging ? 'Drop your file here' : 'Drag and drop your DTM file here'}
                    </p>
                    <p className="text-navy/60 text-sm mt-1">
                      or click to browse • GeoTIFF (.tif, .tiff) / LAS / LAZ • Max 500MB
                    </p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="bg-neutral-100/50 rounded-none p-4">
              <h4 className="text-sm font-medium text-navy-muted mb-2">Supported Data Formats</h4>
              <ul className="text-sm text-navy/60 space-y-1">
                <li>• GeoTIFF (.tif, .tiff) - Upload ready DTM directly</li>
                <li>• LAS/LAZ (.las, .laz) - Auto-generate DTM in Terra Pravah</li>
                <li>• Coordinate systems: Any projected CRS (UTM recommended)</li>
              </ul>
            </div>
            
            <div className="flex justify-between pt-4">
              <button
                onClick={() => goToStep('details')}
                className="btn-secondary"
              >
                Back
              </button>
              <button
                onClick={() => {
                  if (!selectedFile) {
                    setError('Please upload a terrain file')
                    return
                  }
                  goToStep('configure')
                }}
                className="btn-primary"
                disabled={!selectedFile}
              >
                Continue to Configure
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Configure */}
        {currentStep === 'configure' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-navy mb-2">Analysis Configuration</h2>
              <p className="text-navy/60">Configure parameters for drainage network analysis</p>
            </div>

            {isLidarFile(selectedFile) && (
              <div className="bg-primary-500/10 border border-primary-500/20 rounded-none p-4">
                <h4 className="text-sm font-medium text-primary-300 mb-3">LAS/LAZ to DTM Generation</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-navy-muted mb-2">
                      DTM Resolution (m)
                    </label>
                    <input
                      type="number"
                      min={0.25}
                      step={0.25}
                      value={dtmResolution}
                      onChange={(e) => setDtmResolution(Number(e.target.value || 1.0))}
                      className="input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy-muted mb-2">
                      EPSG (optional)
                    </label>
                    <input
                      type="text"
                      value={epsgCode}
                      onChange={(e) => setEpsgCode(e.target.value)}
                      placeholder="EPSG:32644"
                      className="input w-full"
                    />
                  </div>
                </div>
                <p className="text-xs text-navy/60 mt-3">
                  Terra Pravah will upload your LAS/LAZ file, generate DTM, apply hydrological conditioning, and use that DTM for analysis.
                </p>
              </div>
            )}
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Flow Routing Algorithm
                </label>
                <select
                  value={flowAlgorithm}
                  onChange={(e) => setFlowAlgorithm(e.target.value)}
                  className="input w-full"
                >
                  <option value="d8">D8 - Fast & Recommended</option>
                  <option value="dinf">D-Infinity (D∞) - More accurate, slower</option>
                </select>
                <p className="text-xs text-navy/60 mt-1">
                  D8 is faster for large terrains. D∞ provides more accurate flow distribution.
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Design Storm Return Period (years)
                </label>
                <select
                  value={designStormYears}
                  onChange={(e) => setDesignStormYears(Number(e.target.value))}
                  className="input w-full"
                >
                  <option value={2}>2 years - Minor drainage</option>
                  <option value={5}>5 years - Urban drainage</option>
                  <option value={10}>10 years - Standard design</option>
                  <option value={25}>25 years - Major infrastructure</option>
                  <option value={50}>50 years - Critical facilities</option>
                  <option value={100}>100 years - Extreme events</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Runoff Coefficient (C)
                </label>
                <select
                  value={runoffCoefficient}
                  onChange={(e) => setRunoffCoefficient(Number(e.target.value))}
                  className="input w-full"
                >
                  <option value={0.15}>0.15 - Forest/Woodland</option>
                  <option value={0.20}>0.20 - Rural/Agricultural</option>
                  <option value={0.35}>0.35 - Suburban Residential</option>
                  <option value={0.50}>0.50 - Urban Residential</option>
                  <option value={0.70}>0.70 - Commercial/Industrial</option>
                  <option value={0.95}>0.95 - Impervious Surfaces</option>
                </select>
                <p className="text-xs text-navy/60 mt-1">
                  Fraction of rainfall that becomes runoff
                </p>
              </div>
            </div>
            
            {/* Summary */}
            <div className="bg-neutral-100/50 rounded-none p-4">
              <h4 className="text-sm font-medium text-navy-muted mb-3">Project Summary</h4>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-navy/60">Project:</span>
                  <span className="text-navy ml-2">{name}</span>
                </div>
                <div>
                  <span className="text-navy/60">File:</span>
                  <span className="text-navy ml-2">{fileInfo?.name}</span>
                </div>
                {isLidarFile(selectedFile) && (
                  <>
                    <div>
                      <span className="text-navy/60">DTM Resolution:</span>
                      <span className="text-navy ml-2">{dtmResolution} m</span>
                    </div>
                    <div>
                      <span className="text-navy/60">EPSG:</span>
                      <span className="text-navy ml-2">{epsgCode.trim() || 'Auto-detect'}</span>
                    </div>
                  </>
                )}
                <div>
                  <span className="text-navy/60">Algorithm:</span>
                  <span className="text-navy ml-2">{flowAlgorithm === 'd8' ? 'D8 (Fast)' : 'D-Infinity (Accurate)'}</span>
                </div>
                <div>
                  <span className="text-navy/60">Design Storm:</span>
                  <span className="text-navy ml-2">{designStormYears} years</span>
                </div>
              </div>
            </div>
            
            <div className="flex justify-between pt-4">
              <button
                onClick={() => goToStep('upload')}
                className="btn-secondary"
                disabled={isSubmitting}
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                className="btn-primary flex items-center gap-2"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    {isUploading
                      ? isLidarFile(selectedFile)
                        ? `Uploading LAS/LAZ... ${uploadProgress}%`
                        : `Uploading DTM... ${uploadProgress}%`
                      : 'Creating Project...'}
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Create Project
                  </>
                )}
              </button>
            </div>
            
            {/* Upload progress */}
            {isUploading && (
              <div className="mt-4">
                <div className="w-full bg-neutral-100 rounded-full h-2 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary-500 to-violet-500 transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-navy/60 mt-2 text-center">
                  Uploading {fileInfo?.name}...
                </p>
              </div>
            )}
          </div>
        )}

        {/* Step 4: Complete */}
        {currentStep === 'complete' && (
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
            
            <h2 className="text-2xl font-bold text-navy mb-2">Project Created Successfully!</h2>
            <p className="text-navy/60 mb-8 max-w-md mx-auto">
              {isLidarFile(selectedFile)
                ? 'Your LAS/LAZ file was uploaded and DTM has been generated. You can now run drainage analysis.'
                : 'Your DTM file has been uploaded. You can now run drainage analysis to visualize the network.'}
            </p>
            
            <div className="flex justify-center gap-4">
              <Link
                to="/dashboard/projects"
                className="btn-secondary"
              >
                View All Projects
              </Link>
              <Link
                to={`/dashboard/projects/${createdProjectId}/analysis`}
                className="btn-primary flex items-center gap-2"
              >
                <Map className="w-4 h-4" />
                Run Analysis
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
