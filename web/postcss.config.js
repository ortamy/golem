/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.html",
    "./**/*.js",
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
  plugins: [require("preline/plugin")],
};
</content>
</｜｜DSML｜｜>
<write_to_file>
<path>web/postcss.config.js</path>
<content>module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};