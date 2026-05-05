/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        ink: {
          950: '#080b14',
          900: '#0d1220',
          800: '#131a2c',
          700: '#1c2540',
          600: '#2a345a',
          500: '#3a4670',
        },
        accent: {
          DEFAULT: '#5b9dff',
          hover: '#3d86f3',
          glow: '#5b9dff33',
        },
        severity: {
          critical: '#ef4444',
          high: '#f97316',
          medium: '#eab308',
          low: '#3b82f6',
          info: '#94a3b8',
        },
      },
      boxShadow: {
        glow: '0 0 24px -4px rgba(91, 157, 255, 0.45)',
        'glow-danger': '0 0 24px -4px rgba(239, 68, 68, 0.55)',
      },
      keyframes: {
        pulse_ring: {
          '0%': { boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.55)' },
          '70%': { boxShadow: '0 0 0 10px rgba(239, 68, 68, 0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(239, 68, 68, 0)' },
        },
        fade_in: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'pulse-ring': 'pulse_ring 1.6s ease-out infinite',
        'fade-in': 'fade_in 0.18s ease-out',
      },
    },
  },
  plugins: [],
};
