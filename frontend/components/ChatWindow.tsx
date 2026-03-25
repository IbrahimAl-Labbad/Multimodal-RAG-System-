'use client'

import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/store/chatStore'
import { useStream } from '@/hooks/useStream'
import MessageBubble from './MessageBubble'
import FileUpload from './FileUpload'

// In production, retrieve from auth context; demo uses a static token
const DEMO_TOKEN = typeof window !== 'undefined' ? (localStorage.getItem('jwt_token') || '') : ''

export default function ChatWindow() {
    const [input, setInput] = useState('')
    const { messages, isStreaming, documentIds, clearMessages } = useChatStore()
    const { sendMessage } = useStream()
    const bottomRef = useRef<HTMLDivElement>(null)
    const [token] = useState(DEMO_TOKEN)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || isStreaming) return
        const q = input.trim()
        setInput('')
        await sendMessage(q, documentIds, token)
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="flex flex-col h-full">
            {/* Upload section */}
            <div className="p-4 border-b border-[var(--border)]">
                <FileUpload token={token} />
                {documentIds.length > 0 && (
                    <p className="mt-2 text-xs text-[var(--text-muted)] text-center">
                        {documentIds.length} document{documentIds.length !== 1 ? 's' : ''} loaded
                    </p>
                )}
            </div>

            {/* Messages area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-3 opacity-50">
                        <div className="w-16 h-16 rounded-full bg-brand-500/10 flex items-center justify-center">
                            <svg className="w-8 h-8 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                        </div>
                        <div>
                            <p className="font-medium text-[var(--text)]">Start a conversation</p>
                            <p className="text-sm text-[var(--text-muted)]">Upload a document and ask anything about it</p>
                        </div>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <MessageBubble
                        key={msg.id}
                        message={msg}
                        isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'assistant'}
                    />
                ))}
                <div ref={bottomRef} />
            </div>

            {/* Input area */}
            <div className="p-4 border-t border-[var(--border)]">
                <div className="flex gap-2 items-end">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question about your documents…"
                        rows={1}
                        className="flex-1 resize-none rounded-xl px-4 py-3 text-sm surface focus:outline-none focus:ring-2 focus:ring-brand-500/50 text-[var(--text)] placeholder-[var(--text-muted)] max-h-32 overflow-y-auto"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isStreaming}
                        className="w-10 h-10 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center transition-all duration-200 flex-shrink-0"
                    >
                        {isStreaming ? (
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                    </button>
                </div>
                {messages.length > 0 && (
                    <button onClick={clearMessages} className="mt-2 text-xs text-[var(--text-muted)] hover:text-[var(--text)] transition-colors w-full text-center">
                        Clear conversation
                    </button>
                )}
            </div>
        </div>
    )
}
