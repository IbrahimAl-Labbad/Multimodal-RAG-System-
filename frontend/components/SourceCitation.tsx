'use client'

import type { Citation } from '@/store/chatStore'

interface Props {
    citations: Citation[]
}

export default function SourceCitation({ citations }: Props) {
    if (!citations.length) return null
    return (
        <div className="mt-3 space-y-2 animate-fade-in">
            <p className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Sources</p>
            {citations.map((c, i) => (
                <div key={c.chunk_id} className="surface2 rounded-lg p-3 text-xs">
                    <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-[var(--text)] truncate max-w-[60%]">
                            [{i + 1}] {c.filename}
                            {c.page_number != null && ` — p.${c.page_number}`}
                        </span>
                        <span className="ml-2 flex items-center gap-1">
                            <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: scoreColor(c.relevance_score) }} />
                            <span className="text-[var(--text-muted)]">{(c.relevance_score * 100).toFixed(0)}%</span>
                        </span>
                    </div>
                    <p className="text-[var(--text-muted)] line-clamp-2">{c.excerpt}</p>
                    <span className="mt-1 inline-block px-1.5 py-0.5 rounded text-[10px] bg-brand-500/10 text-brand-500">
                        {c.chunk_type}
                    </span>
                </div>
            ))}
        </div>
    )
}

function scoreColor(score: number): string {
    if (score >= 0.7) return '#22c55e'
    if (score >= 0.4) return '#f59e0b'
    return '#ef4444'
}
