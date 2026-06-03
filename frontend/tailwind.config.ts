import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        surface: "#f6f8fb",
        accent: "#2563eb"
      }
    }
  },
  plugins: []
};

export default config;

