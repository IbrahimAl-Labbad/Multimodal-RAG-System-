'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useChatStore } from '@/store/chatStore'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Props { token: string }

export default function FileUpload({ token }: Props) {
    const [uploading, setUploading] = useState(false)
    const [status, setStatus] = useState<string | null>(null)
    const addDocumentId = useChatStore((s) => s.addDocumentId)

    const onDrop = useCallback(
        async (accepted: File[]) => {
            if (!accepted.length) return
            setUploading(true)
            setStatus(null)
            for (const file of accepted) {
                const form = new FormData()
                form.append('file', file)
                try {
                    const res = await fetch(`${API_URL}/api/v1/upload`, {
                        method: 'POST',
                        headers: { Authorization: `Bearer ${token}` },
                        body: form,
                    })
                    if (!res.ok) throw new Error(await res.text())
                    const data = await res.json()
                    addDocumentId(data.document_id)

                    // Trigger indexing
                    await fetch(`${API_URL}/api/v1/index`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                        body: JSON.stringify({ document_id: data.document_id, filename: file.name }),
                    })

                    setStatus(`✅ ${file.name} uploaded and indexing started`)
                } catch (err) {
                    setStatus(`❌ Error: ${(err as Error).message}`)
                }
            }
            setUploading(false)
        },
        [addDocumentId, token],
    )

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
        maxFiles: 10,
    })

    return (
        <div className="space-y-3">
            <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive ? 'border-brand-500 bg-brand-500/5' : 'border-[var(--border)] hover:border-brand-400 hover:bg-brand-500/5'}`}
            >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-brand-500/10 flex items-center justify-center">
                        <svg className="w-6 h-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                    </div>
                    {uploading ? (
                        <p className="text-sm text-[var(--text-muted)]">Uploading…</p>
                    ) : isDragActive ? (
                        <p className="text-sm font-medium text-brand-500">Drop files here</p>
                    ) : (
                        <>
                            <p className="text-sm font-medium text-[var(--text)]">Drag & drop files here</p>
                            <p className="text-xs text-[var(--text-muted)]">PDF, JPG, PNG, WEBP · Max 50MB each</p>
                        </>
                    )}
                </div>
            </div>
            {status && (
                <p className="text-xs text-center text-[var(--text-muted)] animate-fade-in">{status}</p>
            )}
        </div>
    )
}
