'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useChatStore } from '@/store/chatStore'
import FileUpload from '@/components/FileUpload'

export default function FilesPage() {
    const { documentIds } = useChatStore()
    const [token] = useState(() =>
        typeof window !== 'undefined' ? localStorage.getItem('jwt_token') || '' : ''
    )

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text)]">File Manager</h1>
                        <p className="text-sm text-[var(--text-muted)] mt-0.5">Upload and manage your documents</p>
                    </div>
                    <Link href="/chat" className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium transition-colors">
                        Go to Chat
                    </Link>
                </div>

                <div className="surface rounded-2xl p-6 shadow-sm">
                    <h2 className="text-sm font-semibold text-[var(--text)] mb-4">Upload Documents</h2>
                    <FileUpload token={token} />
                </div>

                {documentIds.length > 0 && (
                    <div className="surface rounded-2xl p-6 shadow-sm">
                        <h2 className="text-sm font-semibold text-[var(--text)] mb-4">Loaded Documents ({documentIds.length})</h2>
                        <div className="space-y-2">
                            {documentIds.map((id, i) => (
                                <div key={id} className="surface2 rounded-lg px-4 py-3 flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center flex-shrink-0">
                                        <svg className="w-4 h-4 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-medium text-[var(--text)]">Document {i + 1}</p>
                                        <p className="text-xs text-[var(--text-muted)] truncate font-mono">{id}</p>
                                    </div>
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 font-medium">Indexed</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
