/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Paleta oficial de Vino Nuevo extraída de style.css, admin.css y design_tokens/figma_tokens.json
        vino: {
          DEFAULT: '#4A0203',
          hover: '#780204',
          dark: '#290101',
          light: '#96292b',
        },
        primary: {
          DEFAULT: '#390002',
          container: '#5c0a0a',
          fixed: '#ffdad6',
        },
        brand: {
          red: '#7f1d1d',
        },
        surface: {
          DEFAULT: '#fff8f7',
          container: '#fee9e9',
          low: '#fff0f0',
          high: '#f8e4e3',
          lowest: '#ffffff',
          sidebar: '#f5f5f4',
        },
        text: {
          main: '#2b1111',
          muted: '#6e5553',
        },
        border: {
          subtle: '#e8d0cc',
          variant: '#ddc0bd',
        },
        metric: {
          regular: '#7a2222',
          ninos: '#c86b6b',
          visitas: '#e9b9b9',
          comprometidos: '#2b0000',
        },
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        serif: ['Noto Serif', 'serif'],
        public: ['"Times New Roman"', 'Times', 'serif'],
      },
      boxShadow: {
        card: '0 4px 20px rgba(35, 25, 25, 0.04)',
        elevated: '0 8px 30px rgba(74, 2, 3, 0.08)',
      },
    },
  },
  plugins: [],
}

