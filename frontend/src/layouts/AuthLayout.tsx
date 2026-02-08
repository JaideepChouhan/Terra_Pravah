import { Outlet } from 'react-router-dom'
import { Link } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-dark-800">
        <Outlet />
      </div>

      {/* Right side - Branding */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 p-12 items-center justify-center relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/20 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-500/20 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 max-w-lg text-center">
          <Link to="/" className="inline-block mb-8">
            <span className="text-4xl font-bold font-display gradient-text">Terra Pravah</span>
          </Link>
          
          <h2 className="text-3xl font-bold mb-4">
            Design Drainage Networks with AI Precision
          </h2>
          <p className="text-dark-300 mb-8">
            Join thousands of engineers using the most advanced platform for 
            hydrological analysis and drainage design.
          </p>

          <div className="grid grid-cols-2 gap-6 text-left">
            <div className="card bg-dark-800/50">
              <div className="text-3xl font-bold text-primary-400 mb-1">10,000+</div>
              <div className="text-sm text-dark-400">Projects Analyzed</div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="text-3xl font-bold text-secondary-400 mb-1">500+</div>
              <div className="text-sm text-dark-400">Engineering Firms</div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="text-3xl font-bold text-accent-400 mb-1">99.9%</div>
              <div className="text-sm text-dark-400">Uptime SLA</div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="text-3xl font-bold text-green-400 mb-1">&lt;5min</div>
              <div className="text-sm text-dark-400">Avg Analysis Time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
