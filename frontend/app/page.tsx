import Link from 'next/link'

export default function HomePage() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center p-8">
            <div className="max-w-2xl w-full text-center space-y-8 animate-fade-in">
                {/* Logo */}
                <div className="flex items-center justify-center gap-3">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-500/30">
                        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                    </div>
                    <div className="text-left">
                        <h1 className="text-3xl font-bold tracking-tight text-[var(--text)]">Multimodal RAG</h1>
                        <p className="text-sm text-[var(--text-muted)]">100% Open Source · Powered by Ollama</p>
                    </div>
                </div>

                {/* Tagline */}
                <p className="text-xl text-[var(--text-muted)] leading-relaxed">
                    Chat with your <span className="text-[var(--brand)] font-semibold">PDFs</span> and{' '}
                    <span className="text-[var(--brand)] font-semibold">images</span> using local LLMs.
                    <br />Fully private, fully open-source.
                </p>

                {/* CTA Buttons */}
                <div className="flex gap-4 justify-center flex-wrap">
                    <Link
                        href="/chat"
                        className="px-8 py-3 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold transition-all duration-200 shadow-lg shadow-brand-500/30 hover:shadow-brand-500/50 hover:-translate-y-0.5"
                    >
                        Start Chatting
                    </Link>
                    <Link
                        href="/files"
                        className="px-8 py-3 rounded-xl surface hover:bg-[var(--surface2)] text-[var(--text)] font-semibold transition-all duration-200 hover:-translate-y-0.5"
                    >
                        Manage Files
                    </Link>
                </div>

                {/* Feature pills */}
                <div className="flex flex-wrap gap-2 justify-center">
                    {['LangGraph Agents', 'Qdrant Vector DB', 'LLaVA Vision', 'SSE Streaming', 'CLIP Embeddings', 'JWT Auth'].map((f) => (
                        <span key={f} className="px-3 py-1 rounded-full text-xs font-medium surface2 text-[var(--text-muted)]">{f}</span>
                    ))}
                </div>
            </div>
        </main>
    )
}
