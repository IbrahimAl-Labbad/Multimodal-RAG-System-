'use client'

import ChatWindow from '@/components/ChatWindow'
import { useTheme } from '@/components/ThemeProvider'
import Link from 'next/link'

export default function ChatPage() {
    const { theme, toggle } = useTheme()

    return (
        <div className="h-screen flex flex-col">
            {/* Navbar */}
            <header className="glass border-b flex items-center justify-between px-6 py-3 flex-shrink-0">
                <Link href="/" className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                    </div>
                    <span className="font-semibold text-[var(--text)]">Multimodal RAG</span>
                </Link>
                <div className="flex items-center gap-3">
                    <Link href="/files" className="text-sm text-[var(--text-muted)] hover:text-[var(--text)] transition-colors">
                        Files
                    </Link>
                    <button
                        onClick={toggle}
                        className="w-8 h-8 rounded-lg surface flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
                        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                    >
                        {theme === 'dark' ? (
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        ) : (
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                        )}
                    </button>
                </div>
            </header>

            {/* Main chat area */}
            <div className="flex-1 overflow-hidden max-w-4xl w-full mx-auto px-4 py-4">
                <div className="surface rounded-2xl h-full overflow-hidden shadow-xl shadow-black/5 dark:shadow-black/30">
                    <ChatWindow />
                </div>
            </div>
        </div>
    )
}
