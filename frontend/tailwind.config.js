/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f4ff",
          100: "#e0e9ff",
          500: "#4f6ef7",
          600: "#3d5ce6",
          700: "#2d4ad4",
          900: "#1a2d9a",
        }
      }
    }
  },
  plugins: [],
};
