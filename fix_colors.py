import os
import re

files_to_fix = [
    'frontend/src/pages/dashboard/Dashboard.tsx',
    'frontend/src/pages/dashboard/Analysis.tsx',
    'frontend/src/pages/dashboard/NewProject.tsx',
    'frontend/src/components/DrainageViewer.tsx',
    'frontend/src/pages/dashboard/Projects.tsx',
    'frontend/src/pages/dashboard/Reports.tsx',
    'frontend/src/pages/dashboard/Teams.tsx',
    'frontend/src/pages/dashboard/Profile.tsx',
    'frontend/src/pages/dashboard/Settings.tsx',
    'frontend/src/pages/dashboard/ProjectDetail.tsx',
    'frontend/src/layouts/DashboardLayout.tsx',
]

replacements = [
    (r'bg-dark-900', 'bg-background-light'),
    (r'bg-dark-800', 'bg-white'),
    (r'bg-dark-700', 'bg-neutral-100'),
    (r'bg-dark-600', 'bg-neutral-200'),
    (r'text-white', 'text-navy'),
    (r'text-dark-200', 'text-navy-muted'),
    (r'text-dark-300', 'text-navy-muted'),
    (r'text-dark-400', 'text-navy/60'),
    (r'border-dark-700', 'border-navy/10'),
    (r'border-dark-600', 'border-navy/20'),
    (r'bg-dark-500', 'bg-neutral-300'),
    # Specific dashboard text cleanup
    (r'Welcome back, Demo\! 👋', 'Welcome back, Demo!'),
    # Analysis page text fixes
    (r'text-right', ''),  # Fix right alignment issues requested by user
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for old, new in replacements:
            content = re.sub(old, new, content)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {file_path}')
