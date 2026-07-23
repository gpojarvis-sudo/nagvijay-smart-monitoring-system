/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'india-post': {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#DC2626',
          700: '#B91C1C',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui'],
        'display': ['Poppins', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
