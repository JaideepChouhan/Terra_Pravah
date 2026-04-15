import sys

with open('frontend/src/components/Navbar.tsx', 'r') as f:
    code = f.read()

desktop_cta = """        {/* Desktop CTA */}
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
        </div>"""

code = code.replace("""        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-4">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn-primary">
              Dashboard
            </Link>
          ) : (
            <Link to="/register" className="btn-primary flex items-center gap-2 group">
              <span>Request Access</span>
            </Link>
          )}
        </div>""", desktop_cta)

mobile_cta = """            <div className="flex flex-col gap-2 pt-4 border-t border-muted">
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
            </div>"""

code = code.replace("""            <div className="flex flex-col gap-2 pt-4 border-t border-muted">
              {isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="btn-primary w-full text-center"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="btn-primary w-full text-center"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Request Access
                </Link>
              )}
            </div>""", mobile_cta)

with open('frontend/src/components/Navbar.tsx', 'w') as f:
    f.write(code)
print("Updated Navbar")
