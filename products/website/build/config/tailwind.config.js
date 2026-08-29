/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../index.html",
    "../app.js",
    "../src/pages/**/*.html",
    "../src/js/**/*.js",
    "../src/locales/**/*.json",
  ],
  theme: {
    extend: {
      colors: {
        gold: "#b8860b",
        parchment: "#ede0c8",
        ivory: "#faf3e0",
        ink: "#2c1810",
        muted: "#5c4a3a",
        red: "#c0392b",
        green: "#4a7c3f",
        border: "#d4c4a8",
      },
      fontFamily: {
        heading: ['Cormorant Garamond', 'Georgia', 'Times New Roman', 'serif'],
        body: ['EB Garamond', 'Georgia', 'Times New Roman', 'serif'],
        mono: ['Courier New', 'Courier', 'monospace'],
      },
    },
  },
  plugins: [],
};
