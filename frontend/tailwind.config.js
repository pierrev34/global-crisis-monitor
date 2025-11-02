/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Professional analyst dashboard palette - cool severity ramp
        'primary': '#1d4ed8',
        'primary-light': '#0ea5e9',
        'primary-pale': '#dbeafe',
        'dark': '#0f172a',
        'text-primary': '#0f172a',
        'text-secondary': '#1e293b',
        'text-body': '#475569',
        'text-muted': '#64748b',
        'bg': '#f4f5f7',
        'border': '#e2e8f0',
        'neutral-light': '#e5e7eb',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      letterSpacing: {
        'wide-caps': '0.04em',
      },
    },
  },
  plugins: [],
}
