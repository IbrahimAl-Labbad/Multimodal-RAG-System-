import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './app/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                brand: {
                    50: '#f0f4ff',
                    100: '#dde7ff',
                    200: '#c3d2fe',
                    300: '#9db3fc',
                    400: '#7589f8',
                    500: '#5a67f2',
                    600: '#4548e6',
                    700: '#3a3ac9',
                    800: '#3133a2',
                    900: '#2c3080',
                },
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
                slideUp: { from: { transform: 'translateY(8px)', opacity: '0' }, to: { transform: 'translateY(0)', opacity: '1' } },
            },
        },
    },
    plugins: [],
}
export default config
