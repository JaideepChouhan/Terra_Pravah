/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#e98963',
          50: '#fdf4f0',
          100: '#fae4da',
          200: '#f5c9b6',
          300: '#f0a283',
          400: '#e98963',
          500: '#e86a3d',
          600: '#db4f1f',
          700: '#b73c15',
          800: '#923318',
          900: '#752b16',
          950: '#3f1308',
        },
        background: {
          light: '#F7F3EB',
          dark: '#211611',
        },
        surface: '#212C43',
        text: {
          main: '#121826',
          inverse: '#F7F3EB',
        },
        muted: '#829AB1',
        accent: '#C3D2D5',
        'error-dark': '#991b1b',
        navy: {
          DEFAULT: '#121826',
          muted: '#212C43'
        },
        // Keeping legacy colors for compatibility but mapping some to new ones to ease transition, although we'll replace most usage
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        secondary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        display: ['Inter', 'DM Sans', 'sans-serif'],
        heading: ['Fraunces', 'serif'],
        sans: ['Inter', 'DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'DEFAULT': '2px',
        'lg': '2px',
        'xl': '2px',
        'full': '2px',
        'none': '0px',
        'sm': '2px',
        'md': '2px',
      },
      letterSpacing: {
        tightest: '-.04em',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'draw-path': 'drawPath 1.5s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        drawPath: {
          to: {
            strokeDashoffset: '0',
          }
        }
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
