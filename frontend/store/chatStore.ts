'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Citation {
    chunk_id: string
    document_id: string
    filename: string
    page_number: number | null
    chunk_type: string
    excerpt: string
    relevance_score: number
}

export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    citations?: Citation[]
    timestamp: number
}

interface ChatStore {
    messages: Message[]
    isStreaming: boolean
    sessionId: string | null
    documentIds: string[]
    addMessage: (msg: Message) => void
    appendToken: (id: string, token: string) => void
    setStreamingId: (id: string | null) => void
    setCitations: (id: string, citations: Citation[]) => void
    setStreaming: (v: boolean) => void
    setSessionId: (id: string) => void
    addDocumentId: (id: string) => void
    clearMessages: () => void
}

export const useChatStore = create<ChatStore>()(
    persist(
        (set) => ({
            messages: [],
            isStreaming: false,
            sessionId: null,
            documentIds: [],

            addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

            appendToken: (id, token) =>
                set((s) => ({
                    messages: s.messages.map((m) =>
                        m.id === id ? { ...m, content: m.content + token } : m,
                    ),
                })),

            setStreamingId: (_id) => set({}),

            setCitations: (id, citations) =>
                set((s) => ({
                    messages: s.messages.map((m) =>
                        m.id === id ? { ...m, citations } : m,
                    ),
                })),

            setStreaming: (v) => set({ isStreaming: v }),
            setSessionId: (id) => set({ sessionId: id }),
            addDocumentId: (id) => set((s) => ({ documentIds: [...new Set([...s.documentIds, id])] })),
            clearMessages: () => set({ messages: [] }),
        }),
        { name: 'rag-chat-store' },
    ),
)
