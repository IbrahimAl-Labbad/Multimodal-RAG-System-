'use client'

import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext<{ theme: string; toggle: () => void }>({
    theme: 'light',
    toggle: () => { },
})

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setTheme] = useState('light')

    useEffect(() => {
        const stored = localStorage.getItem('theme') || 'light'
        setTheme(stored)
        document.documentElement.classList.toggle('dark', stored === 'dark')
    }, [])

    const toggle = () => {
        const next = theme === 'light' ? 'dark' : 'light'
        setTheme(next)
        localStorage.setItem('theme', next)
        document.documentElement.classList.toggle('dark', next === 'dark')
    }

    return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
}

export const useTheme = () => useContext(ThemeContext)
