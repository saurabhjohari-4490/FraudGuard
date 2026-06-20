/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        fraud: {
          approve: '#10b981',
          verify: '#f59e0b',
          review: '#f97316',
          block: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
