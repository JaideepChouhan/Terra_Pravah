import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { motion } from 'framer-motion'
import { ArrowRightIcon } from '@heroicons/react/24/outline'

export default function Login() {
  const navigate = useNavigate()
  const { login, demoLogin, isLoading, error, clearError } = useAuthStore()
  const [formError, setFormError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setFormError(null)
    
    try {
      await login(formData.email, formData.password)
      navigate('/dashboard')
    } catch (err: any) {
      setFormError(err.message || 'Invalid email or password. Please try again.')
    }
  }

  return (
    <motion.main 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full max-w-[400px] mx-auto px-6 py-16 md:py-24 flex flex-col items-center"
    >
      {/* Header */}
      <header className="w-full text-center mb-12">
        <h1 className="text-navy text-[48px] font-black leading-tight tracking-tightest mb-4 font-heading">
          Welcome back.
        </h1>
        <p className="text-navy/80 text-lg">
          Sign in to access your platform.
        </p>
      </header>

      {/* Form */}
      <form onSubmit={handleSubmit} className="w-full flex flex-col gap-8">

        {(error || formError) && (
          <div className="p-4 rounded bg-error-dark/10 text-error-dark text-sm border border-error-dark/20 text-center">
            {error || formError}
          </div>
        )}

        {/* Input Group: Work Email */}
        <div className="relative w-full h-12 flex items-end">
          <input
            type="email"
            id="email"
            name="email"
            placeholder="Work Email"
            required
            className="minimal-input peer w-full h-8 text-navy text-lg placeholder-transparent focus:ring-0"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <label
            htmlFor="email"
            className="floating-label absolute left-0 bottom-2 text-navy-muted text-lg cursor-text peer-focus:-translate-y-7 peer-focus:text-sm peer-focus:text-navy peer-not-placeholder-shown:-translate-y-7 peer-not-placeholder-shown:text-sm peer-not-placeholder-shown:text-navy"
          >
            Work Email
          </label>
        </div>

        {/* Input Group: Password */}
        <div className="relative w-full h-12 flex items-end">
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Password"
            required
            className="minimal-input peer w-full h-8 text-navy text-lg placeholder-transparent focus:ring-0"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <label
            htmlFor="password"
            className="floating-label absolute left-0 bottom-2 text-navy-muted text-lg cursor-text peer-focus:-translate-y-7 peer-focus:text-sm peer-focus:text-navy peer-not-placeholder-shown:-translate-y-7 peer-not-placeholder-shown:text-sm peer-not-placeholder-shown:text-navy"
          >
            Password
          </label>
        </div>

        {/* Submit Button */}
        <div className="mt-8 w-full flex flex-col gap-4">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-navy text-background-light py-4 px-6 rounded-none flex justify-center items-center gap-2 hover:bg-navy-muted transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy focus:ring-offset-primary disabled:opacity-50"
          >
            <span className="text-base font-medium tracking-[0.05em] uppercase">
              {isLoading ? 'Signing in...' : 'Sign In'}
            </span>
            <ArrowRightIcon className="w-5 h-5" />
          </button>
          
          <button
            type="button"
            onClick={() => {
              demoLogin()
              navigate('/dashboard')
            }}
            disabled={isLoading}
            className="w-full bg-transparent border border-navy text-navy py-4 px-6 rounded-none flex justify-center items-center gap-2 hover:bg-navy/5 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy focus:ring-offset-primary disabled:opacity-50"
          >
            <span className="text-base font-medium tracking-[0.05em] uppercase">
              Demo Login
            </span>
          </button>
        </div>
      </form>

      {/* Footer Note */}
      <div className="mt-8 text-center flex flex-col gap-4">
        <p className="text-sm text-navy/80">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold underline hover:text-navy">
            Request Access
          </Link>
        </p>
      </div>
    </motion.main>
  )
}
