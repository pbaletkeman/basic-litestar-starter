/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static-files/**/*.{html,js}"],

  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
}