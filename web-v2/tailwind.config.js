/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.{html,js}", "./node_modules/preline/dist/*.js"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        accent: "#ff4d00",
        gold: "#d4a843",
        parchment: "#f5e6c8",
        stone: "#2a2a2a",
        "dark-bg": "#1a1a1a",
        "light-bg": "#fafafa",
      },
    },
  },
  plugins: [],
};