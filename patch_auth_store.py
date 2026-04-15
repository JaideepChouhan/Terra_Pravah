import re

with open('frontend/src/store/authStore.ts', 'r', encoding='utf-8') as f:
    content = f.read()

check_auth_patch = """      checkAuth: async () => {
        const token = localStorage.getItem('token')
        if (!token) {
          set({ isLoading: false, isAuthenticated: false })
          return
        }

        if (token === 'demo-token-123') {
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
          })
          return;
        }

        set({ isLoading: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        try {
          const response = await api.get('/api/users/me')"""

content = re.sub(r"      checkAuth: async \(\) => \{\s*const token = localStorage\.getItem\('token'\)\s*if \(\!token\) \{\s*set\(\{ isLoading: false, isAuthenticated: false \}\)\s*return\s*\}\s*set\(\{ isLoading: true \}\)\s*api\.defaults\.headers\.common\['Authorization'\] = `Bearer \$\{token\}`\s*try \{\s*const response = await api\.get\('/api/users/me'\)", check_auth_patch, content)

with open('frontend/src/store/authStore.ts', 'w', encoding='utf-8') as f:
    f.write(content)
