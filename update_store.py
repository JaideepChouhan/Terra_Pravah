import sys

with open('frontend/src/store/authStore.ts', 'r') as f:
    code = f.read()

code = code.replace("logout: () => void", "logout: () => void\n  demoLogin: () => void")

demo_func = """      clearError: () => {
        set({ error: null })
      },
      
      demoLogin: () => {
        const token = 'demo-token-123';
        localStorage.setItem('token', token);
        // api.defaults.headers.common['Authorization'] = Bearer \ // Ignoring for demo
        set({
          user: {
            id: 'demo-user',
            email: 'demo@terrapravah.com',
            firstName: 'Demo',
            lastName: 'Engineer',
            role: 'admin',
            company: 'Terra Pravah',
            createdAt: new Date().toISOString()
          },
          token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        })
      },"""

code = code.replace("""      clearError: () => {
        set({ error: null })
      },""", demo_func)

with open('frontend/src/store/authStore.ts', 'w') as f:
    f.write(code)
print("Updated authStore")
