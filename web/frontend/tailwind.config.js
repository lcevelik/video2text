/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#020617",  // slate-950
        sidebar: "#0f172a",     // slate-900
        "bg-tertiary": "#1e293b", // slate-800
        accent: "#06b6d4",      // cyan-400
        "accent-hover": "#22d3ee", // cyan-300
        "text-primary": "#ffffff",
        "text-secondary": "#94a3b8", // slate-400
        border: "#334155",      // slate-700
        success: "#22c55e",     // green-400
        error: "#ef4444",       // red-500
        warning: "#f59e0b",     // amber-500
        info: "#06b6d4",        // cyan-400
        "card-bg": "#0f172a",   // slate-900
      },
      animation: {
        'blob': 'blob 7s infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        blob: {
          '0%': { transform: 'translate(0px, 0px) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
          '100%': { transform: 'translate(0px, 0px) scale(1)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
