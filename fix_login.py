import re

with open('frontend/src/pages/auth/Login.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

end_proper = """          <button
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
"""

new_content = re.sub(r'          <button\s+type="button"\s+onClick=\{\(\) => \{\s+demoLogin\(\)\s+navigate\(\'/dashboard\'\)\s+\}\}\s+disabled=\{isLoading\}.*', end_proper, content, flags=re.DOTALL)

with open('frontend/src/pages/auth/Login.tsx', 'w', encoding='utf-8') as f:
    f.write(new_content)