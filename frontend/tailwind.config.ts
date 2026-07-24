import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0a0a0f",
          card: "#111827",
          cardHover: "#1f2937",
        },
        border: {
          subtle: "#1f2937",
          emphasis: "#4c1d95",
        },
        fg: {
          primary: "#e5e7eb",
          muted: "#9ca3af",
          faint: "#6b7280",
        },
        tier: {
          strong: "#22c55e",
          good: "#84cc16",
          moderate: "#eab308",
          stretch: "#f97316",
          low: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      backgroundImage: {
        "gradient-purple": "linear-gradient(135deg, #a855f7, #ec4899)",
        "gradient-purple-deep": "linear-gradient(135deg, #1e1b4b, #312e81)",
      },
      borderRadius: {
        card: "16px",
      },
    },
  },
  plugins: [],
};

export default config;
