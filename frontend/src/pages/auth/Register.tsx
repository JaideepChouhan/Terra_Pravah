import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { motion } from 'framer-motion'
import { ArrowRightIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'

export default function Register() {
  const navigate = useNavigate()
  const { register, isLoading, error, clearError } = useAuthStore()
  const [formError, setFormError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    password: '',
    confirmPassword: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setFormError(null)

    if (formData.password !== formData.confirmPassword) {
      setFormError('Passwords do not match.')
      return
    }

    try {
      await register({
        firstName: formData.firstName,
        lastName: formData.lastName || 'User', // Minimal form design drops last name for simplicity, handling logic if missing
        email: formData.email,
        password: formData.password,
      })
      navigate('/dashboard')
    } catch (err: any) {
      setFormError(err.message || 'An error occurred during registration.')
    }
  }

  return (
    <motion.main 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full max-w-[400px] mx-auto px-6 py-8 md:py-12 flex flex-col items-center min-h-screen justify-center"
    >
      {/* Header */}
      <header className="w-full text-center mb-8">
        <h1 className="text-navy text-[40px] md:text-[48px] font-black leading-tight tracking-tightest mb-3 font-heading">
          Join the Vanguard.
        </h1>
        <p className="text-navy/80 text-base md:text-lg">
          Request access to our precision planetary scale platform.
        </p>
      </header>

      {/* Form */}
      <form onSubmit={handleSubmit} className="w-full flex flex-col gap-6">

        {(error || formError) && (
          <div className="p-3 rounded bg-error-dark/10 text-error-dark text-sm border border-error-dark/20 text-center">
            {error || formError}
          </div>
        )}

        {/* Input Group: Full Name */}
        <div className="relative w-full pt-4">
          <input
            type="text"
            id="fullname"
            name="fullname"
            placeholder=" "
            required
            className="minimal-input peer w-full h-9 text-navy text-base focus:ring-0"
            value={formData.firstName}
            onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
          />
          <label
            htmlFor="fullname"
            className="floating-label absolute left-0 top-4 text-navy-muted text-base peer-focus:-translate-y-5 peer-focus:text-xs peer-focus:text-navy peer-[:not(:placeholder-shown)]:-translate-y-5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:text-navy"
          >
            Full Name
          </label>
        </div>

        {/* Input Group: Work Email */}
        <div className="relative w-full pt-4">
          <input
            type="email"
            id="email"
            name="email"
            placeholder=" "
            required
            className="minimal-input peer w-full h-9 text-navy text-base focus:ring-0"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <label
            htmlFor="email"
            className="floating-label absolute left-0 top-4 text-navy-muted text-base peer-focus:-translate-y-5 peer-focus:text-xs peer-focus:text-navy peer-[:not(:placeholder-shown)]:-translate-y-5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:text-navy"
          >
            Work Email
          </label>
        </div>

        {/* Input Group: Company */}
        <div className="relative w-full pt-4">
          <input
            type="text"
            id="company"
            name="company"
            placeholder=" "
            className="minimal-input peer w-full h-9 text-navy text-base focus:ring-0"
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
          />
          <label
            htmlFor="company"
            className="floating-label absolute left-0 top-4 text-navy-muted text-base peer-focus:-translate-y-5 peer-focus:text-xs peer-focus:text-navy peer-[:not(:placeholder-shown)]:-translate-y-5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:text-navy"
          >
            Company
          </label>
        </div>

        {/* Input Group: Password */}
        <div className="relative w-full pt-4">
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            name="password"
            placeholder=" "
            required
            className="minimal-input peer w-full h-9 text-navy text-base focus:ring-0 pr-10"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <label
            htmlFor="password"
            className="floating-label absolute left-0 top-4 text-navy-muted text-base peer-focus:-translate-y-5 peer-focus:text-xs peer-focus:text-navy peer-[:not(:placeholder-shown)]:-translate-y-5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:text-navy"
          >
            Password
          </label>
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-0 top-4 h-9 px-2 text-navy-muted hover:text-navy transition-colors"
            tabIndex={-1}
          >
            {showPassword ? (
              <EyeSlashIcon className="w-5 h-5" />
            ) : (
              <EyeIcon className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Input Group: Confirm Password */}
        <div className="relative w-full pt-4">
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            id="confirmPassword"
            name="confirmPassword"
            placeholder=" "
            required
            className="minimal-input peer w-full h-9 text-navy text-base focus:ring-0 pr-10"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
          />
          <label
            htmlFor="confirmPassword"
            className="floating-label absolute left-0 top-4 text-navy-muted text-base peer-focus:-translate-y-5 peer-focus:text-xs peer-focus:text-navy peer-[:not(:placeholder-shown)]:-translate-y-5 peer-[:not(:placeholder-shown)]:text-xs peer-[:not(:placeholder-shown)]:text-navy"
          >
            Confirm Password
          </label>
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-0 top-4 h-9 px-2 text-navy-muted hover:text-navy transition-colors"
            tabIndex={-1}
          >
            {showConfirmPassword ? (
              <EyeSlashIcon className="w-5 h-5" />
            ) : (
              <EyeIcon className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Submit Button */}
        <div className="mt-4 w-full">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-navy text-background-light py-3 px-6 rounded-none flex justify-center items-center gap-2 hover:bg-navy-muted transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy focus:ring-offset-primary disabled:opacity-50"
          >
            <span className="text-base font-medium tracking-[0.05em] uppercase">
              {isLoading ? 'Submitting...' : 'Request Access'}
            </span>
            <ArrowRightIcon className="w-5 h-5" />
          </button>
        </div>
      </form>

      {/* Footer Note */}
      <div className="mt-6 text-center flex flex-col gap-2">
        <p className="text-xs text-navy/60 flex items-center justify-center gap-1">
          Secure application process
        </p>
        <p className="text-sm text-navy/80">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold underline hover:text-navy">
            Sign In
          </Link>
        </p>
      </div>
    </motion.main>
  )
}
