/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rubbish: {
          light: '#6b7280',
          DEFAULT: '#374151',
          dark: '#1f2937'
        },
        recycling: {
          light: '#60a5fa',
          DEFAULT: '#3b82f6',
          dark: '#1d4ed8'
        },
        garden: {
          light: '#4ade80',
          DEFAULT: '#22c55e',
          dark: '#15803d'
        },
        plastics: {
          light: '#fbbf24',
          DEFAULT: '#f59e0b',
          dark: '#b45309'
        }
      }
    },
  },
  plugins: [],
}
