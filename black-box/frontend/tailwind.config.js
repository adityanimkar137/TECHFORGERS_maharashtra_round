// /** @type {import('tailwindcss').Config} */
// export default {
//   content: ['./index.html', './src/**/*.{js,jsx}'],
//   theme: {
//     extend: {
//       fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'], mono: ['JetBrains Mono', 'ui-monospace', 'monospace'] },
//       colors: {
//         base: 'rgb(247, 248, 250)', panel: '#12161d', raised: '#181d26', line: '#232a35',
//         ink: '#e6e9ef', muted: '#8a94a6', accent: '#7c9cff',
//         ok: '#3fb97f', bad: '#f0616d', warn: '#e3a008',
//       },
//     },
//   },
//   plugins: [],
// }
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],

  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },

      colors: {
        // Main background
        base: '#f8fafc',

        // Cards / panels
        panel: '#ffffff',
        raised: '#f1f5f9',

        // Borders
        line: '#e2e8f0',

        // Text
        ink: '#0f172a',
        muted: '#64748b',

        // Primary accent
        accent: '#4f46e5',

        // Status colors
        ok: '#16a34a',
        bad: '#dc2626',
        warn: '#d97706',
      },
    },
  },

  plugins: [],
}