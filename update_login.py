import sys

with open("frontend/src/pages/auth/Login.tsx", "r") as f:
    code = f.read()

# adding a demo login button
button_html = """          <button
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
          </button>"""

code = code.replace("""          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-navy text-background-light py-4 px-6 rounded-none flex justify-center items-center gap-2 hover:bg-navy-muted transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy focus:ring-offset-primary disabled:opacity-50"
          >
            <span className="text-base font-medium tracking-[0.05em] uppercase">
              {isLoading ? 'Signing in...' : 'Sign In'}
            </span>
            <ArrowRightIcon className="w-5 h-5" />
          </button>""", button_html)

with open("frontend/src/pages/auth/Login.tsx", "w") as f:
    f.write(code)

print("Updated Login")
