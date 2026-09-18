import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#1F4E8C",
        "primary-light": "#EAF1FB",
      },
    },
  },
  plugins: [],
};
export default config;
