import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import { useAuthStore } from '../store/authStore'

const navigation = [
  { name: 'Mission', href: '#mission' },
  { name: 'Solutions', href: '#solutions' },
  { name: 'Cases', href: '#cases' },
]

export default function Navbar() {
  const { isAuthenticated } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="fixed top-0 w-full z-50 bg-[#F7F3EB] border-b border-muted">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3 text-text-main hover:text-primary transition-colors">
            <div className="text-primary">
              <svg fill="none" height="24" viewBox="0 0 48 48" width="24" xmlns="http://www.w3.org/2000/svg">
                <path clipRule="evenodd" d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z" fill="currentColor" fillRule="evenodd"></path>
              </svg>
            </div>
            <span className="text-xl font-bold tracking-tight text-text-main font-heading">Terra Pravah</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navigation.map((item) => (
            <a
              key={item.name}
              href={item.href}
              className="nav-link text-sm font-medium text-text-main hover:text-primary transition-colors"
            >
              {item.name}
            </a>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-4">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn-primary">
              Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="nav-link text-sm font-medium text-text-main hover:text-primary transition-colors">
                Sign In
              </Link>
              <Link to="/register" className="btn-primary flex items-center gap-2 group">
                <span>Request Access</span>
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden text-text-main hover:text-primary transition-colors"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Menu"
        >
          {mobileMenuOpen ? (
            <XMarkIcon className="w-6 h-6" />
          ) : (
            <Bars3Icon className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#F7F3EB] border-t border-muted py-4 absolute w-full top-20 ">
          <div className="flex flex-col gap-4 px-6">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="text-text-main hover:text-primary py-2 font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.name}
              </a>
            ))}
            <div className="flex flex-col gap-2 pt-4 border-t border-muted">
              {isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="btn-primary w-full text-center"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="btn-secondary w-full text-center"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="btn-primary w-full text-center"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Request Access
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
