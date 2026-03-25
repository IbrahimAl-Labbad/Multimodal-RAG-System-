import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/ThemeProvider'

export const metadata: Metadata = {
    title: 'Multimodal RAG — Chat with Docs & Images',
    description: 'Production-grade open-source RAG system: chat with PDFs and images using local LLMs via Ollama',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body>
                <ThemeProvider>{children}</ThemeProvider>
            </body>
        </html>
    )
}
