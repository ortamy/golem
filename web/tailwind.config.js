/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./app.js",
    "./node_modules/preline/dist/*.js",
  ],
  theme: {
    extend: {
      colors: {
        accent: "#ff4d00",
        gold: "#d4a843",
        parchment: "#f5e6c8",
        stone: "#2a2a2a",
        dark: "#1a1a1a",
        light: "#fafafa",
      },
    },
  },
  plugins: [],
};