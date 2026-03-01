/**
 * Common UI Components
 * ====================
 * Reusable UI components following the Terra Pravah design system
 */

import { forwardRef, ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react'
import { Loader2, CheckCircle, AlertCircle, Info, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

// ============================================================================
// Button Component
// ============================================================================

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    loading, 
    leftIcon, 
    rightIcon, 
    children, 
    className = '',
    disabled,
    ...props 
  }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-300 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed'
    
    const variants = {
      primary: 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/40 hover:-translate-y-0.5 active:translate-y-0',
      secondary: 'bg-slate-800/80 text-slate-200 border border-slate-700/50 hover:bg-slate-700/80 hover:border-slate-600/50 backdrop-blur-sm',
      outline: 'bg-transparent border-2 border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10 hover:border-indigo-400',
      ghost: 'bg-transparent text-slate-400 hover:bg-slate-800/50 hover:text-white',
      danger: 'bg-red-600/90 text-white hover:bg-red-600 shadow-lg shadow-red-500/20'
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-5 py-2.5 text-sm',
      lg: 'px-8 py-3.5 text-base'
    }

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : leftIcon}
        {children}
        {!loading && rightIcon}
      </button>
    )
  }
)

Button.displayName = 'Button'

// ============================================================================
// Input Component
// ============================================================================

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, leftIcon, rightIcon, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-slate-300 mb-2">
            {label}
            {props.required && <span className="text-red-400 ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            className={`
              w-full px-4 py-3.5 bg-slate-900/50 border rounded-xl text-white 
              placeholder-slate-500 transition-all duration-300
              focus:bg-slate-900/80 focus:ring-0
              ${leftIcon ? 'pl-12' : ''}
              ${rightIcon ? 'pr-12' : ''}
              ${error 
                ? 'border-red-500/50 focus:border-red-500' 
                : 'border-slate-800 focus:border-indigo-500/50'
              }
              ${className}
            `}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-400 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4" />
            {error}
          </p>
        )}
        {hint && !error && (
          <p className="mt-2 text-sm text-slate-500">{hint}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

// ============================================================================
// Card Component
// ============================================================================

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({ children, className = '', hover = false, padding = 'md' }: CardProps) {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }

  return (
    <div className={`
      bg-slate-900/60 backdrop-blur-xl border border-slate-800/50 rounded-2xl
      transition-all duration-500
      ${hover ? 'hover:border-indigo-500/30 hover:bg-slate-900/80 hover:shadow-2xl hover:shadow-indigo-500/5' : ''}
      ${paddings[padding]}
      ${className}
    `}>
      {children}
    </div>
  )
}

// ============================================================================
// Badge Component
// ============================================================================

interface BadgeProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  children: ReactNode
  className?: string
  icon?: ReactNode
}

export function Badge({ variant = 'primary', children, className = '', icon }: BadgeProps) {
  const variants = {
    primary: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/20',
    secondary: 'bg-slate-500/15 text-slate-400 border-slate-500/20',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
    error: 'bg-rose-500/15 text-rose-400 border-rose-500/20',
    info: 'bg-sky-500/15 text-sky-400 border-sky-500/20'
  }

  return (
    <span className={`
      inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs 
      font-semibold tracking-wide border
      ${variants[variant]}
      ${className}
    `}>
      {icon}
      {children}
    </span>
  )
}

// ============================================================================
// Alert Component
// ============================================================================

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  children: ReactNode
  className?: string
  dismissible?: boolean
  onDismiss?: () => void
}

export function Alert({ 
  type = 'info', 
  title, 
  children, 
  className = '', 
  dismissible,
  onDismiss 
}: AlertProps) {
  const types = {
    info: {
      bg: 'bg-sky-500/10 border-sky-500/20',
      icon: <Info className="w-5 h-5 text-sky-400" />,
      titleColor: 'text-sky-400'
    },
    success: {
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />,
      titleColor: 'text-emerald-400'
    },
    warning: {
      bg: 'bg-amber-500/10 border-amber-500/20',
      icon: <AlertCircle className="w-5 h-5 text-amber-400" />,
      titleColor: 'text-amber-400'
    },
    error: {
      bg: 'bg-red-500/10 border-red-500/20',
      icon: <AlertCircle className="w-5 h-5 text-red-400" />,
      titleColor: 'text-red-400'
    }
  }

  const config = types[type]

  return (
    <div className={`
      p-4 rounded-xl border ${config.bg} ${className}
    `}>
      <div className="flex gap-3">
        <div className="shrink-0">{config.icon}</div>
        <div className="flex-1">
          {title && (
            <h5 className={`font-semibold ${config.titleColor} mb-1`}>{title}</h5>
          )}
          <div className="text-sm text-slate-300">{children}</div>
        </div>
        {dismissible && (
          <button 
            onClick={onDismiss}
            className="shrink-0 text-slate-500 hover:text-slate-300 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Progress Bar Component
// ============================================================================

interface ProgressProps {
  value: number
  max?: number
  label?: string
  showValue?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'gradient'
}

export function Progress({ 
  value, 
  max = 100, 
  label, 
  showValue = false,
  size = 'md',
  variant = 'default'
}: ProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }

  const barColors = {
    default: 'bg-indigo-500',
    gradient: 'bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500'
  }

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm text-slate-400">{label}</span>}
          {showValue && (
            <span className="text-sm font-medium text-white">{percentage.toFixed(0)}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-slate-800 rounded-full overflow-hidden ${sizes[size]}`}>
        <motion.div
          className={`h-full ${barColors[variant]} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// ============================================================================
// Modal Component
// ============================================================================

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export function Modal({ isOpen, onClose, title, children, size = 'md' }: ModalProps) {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl'
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className={`fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full ${sizes[size]} p-4`}
          >
            <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl">
              {title && (
                <div className="flex items-center justify-between p-6 border-b border-slate-800">
                  <h3 className="text-lg font-semibold text-white">{title}</h3>
                  <button
                    onClick={onClose}
                    className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
              )}
              <div className="p-6">{children}</div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// ============================================================================
// Stat Card Component (for Dashboard)
// ============================================================================

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: ReactNode
  gradient: string
}

export function StatCard({ title, value, change, icon, gradient }: StatCardProps) {
  return (
    <Card hover className="p-6">
      <div className="flex items-start justify-between">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${gradient} p-0.5`}>
          <div className="w-full h-full bg-slate-900 rounded-xl flex items-center justify-center">
            {icon}
          </div>
        </div>
        {change !== undefined && change !== null && (
          <Badge variant={change >= 0 ? 'success' : 'error'}>
            {change >= 0 ? '+' : ''}{change}%
          </Badge>
        )}
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-slate-400 mt-1">{title}</p>
      </div>
    </Card>
  )
}

// ============================================================================
// Empty State Component
// ============================================================================

interface EmptyStateProps {
  icon: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-16">
      <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-6">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      {description && (
        <p className="text-slate-400 max-w-md mx-auto mb-6">{description}</p>
      )}
      {action}
    </div>
  )
}

// ============================================================================
// Drainage Legend Component
// ============================================================================

interface DrainageLegendProps {
  showPrimary?: boolean
  showSecondary?: boolean
  showTertiary?: boolean
  className?: string
}

export function DrainageLegend({ 
  showPrimary = true, 
  showSecondary = true, 
  showTertiary = true,
  className = ''
}: DrainageLegendProps) {
  const types = [
    { key: 'primary', label: 'Primary', color: 'bg-sky-600', show: showPrimary },
    { key: 'secondary', label: 'Secondary', color: 'bg-teal-500', show: showSecondary },
    { key: 'tertiary', label: 'Tertiary', color: 'bg-green-500', show: showTertiary }
  ]

  return (
    <div className={`flex items-center gap-4 ${className}`}>
      {types.filter(t => t.show).map(type => (
        <div key={type.key} className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${type.color}`} />
          <span className="text-sm text-slate-300">{type.label}</span>
        </div>
      ))}
    </div>
  )
}

// ============================================================================
// File Upload Zone Component
// ============================================================================

interface UploadZoneProps {
  onFileSelect: (file: File) => void
  accept?: string
  maxSize?: number // in bytes
  isDragging?: boolean
  onDragOver?: (e: React.DragEvent) => void
  onDragLeave?: (e: React.DragEvent) => void
  onDrop?: (e: React.DragEvent) => void
  disabled?: boolean
  className?: string
}

export function UploadZone({
  onFileSelect,
  accept = '.tif,.tiff,.las,.laz',
  maxSize = 500 * 1024 * 1024,
  isDragging = false,
  onDragOver,
  onDragLeave,
  onDrop,
  disabled = false,
  className = ''
}: UploadZoneProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFileSelect(file)
  }

  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={`
        relative border-2 border-dashed rounded-2xl p-12 text-center
        transition-all duration-300 cursor-pointer
        ${isDragging 
          ? 'border-indigo-500 bg-indigo-500/5' 
          : 'border-slate-700 hover:border-slate-600 bg-slate-900/30'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleFileChange}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <p className="text-lg font-medium text-white mb-1">
        {isDragging ? 'Drop your file here' : 'Drag & drop your file here'}
      </p>
      <p className="text-sm text-slate-400 mb-4">
        or click to browse
      </p>
      <p className="text-xs text-slate-500">
        Supported: GeoTIFF (.tif, .tiff), LiDAR (.las, .laz) • Max size: {(maxSize / (1024 * 1024)).toFixed(0)}MB
      </p>
    </div>
  )
}
