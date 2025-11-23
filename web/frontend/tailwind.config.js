/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#1a1b1e",
        sidebar: "#25262b",
        accent: "#3b82f6",
        "text-primary": "#ffffff",
        "text-secondary": "#a1a1aa",
      },
    },
  },
  plugins: [],
}
