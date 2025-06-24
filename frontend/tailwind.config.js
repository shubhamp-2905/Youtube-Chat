/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'youtube-red': '#FF0000',
        'youtube-dark': '#282828',
        'youtube-light': '#f9f9f9',
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        youtube: {
          "primary": "#FF0000",
          "secondary": "#ffffff",
          "accent": "#FF0000",
          "neutral": "#282828",
          "base-100": "#ffffff",
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
      },
    ],
  },
}