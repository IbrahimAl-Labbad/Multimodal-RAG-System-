'use client'

import { useCallback } from 'react'
import { useChatStore, type Citation } from '@/store/chatStore'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useStream() {
    const { addMessage, appendToken, setCitations, setStreaming, setSessionId } = useChatStore()

    const sendMessage = useCallback(
        async (query: string, documentIds: string[], token: string) => {
            const msgId = crypto.randomUUID()
            const assistantMsgId = crypto.randomUUID()

            addMessage({ id: msgId, role: 'user', content: query, timestamp: Date.now() })
            addMessage({ id: assistantMsgId, role: 'assistant', content: '', timestamp: Date.now() })
            setStreaming(true)

            try {
                const response = await fetch(`${API_URL}/api/v1/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        query,
                        document_ids: documentIds.length > 0 ? documentIds : undefined,
                        top_k: 5,
                    }),
                })

                if (!response.body) throw new Error('No stream body')

                const reader = response.body.getReader()
                const decoder = new TextDecoder()

                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunk = decoder.decode(value)
                    const lines = chunk.split('\n').filter((l) => l.startsWith('data: '))

                    for (const line of lines) {
                        const data = line.replace('data: ', '').trim()
                        if (data === '[DONE]') break

                        try {
                            const parsed = JSON.parse(data)
                            if (parsed.type === 'token') {
                                appendToken(assistantMsgId, parsed.content)
                            } else if (parsed.type === 'session') {
                                setSessionId(parsed.session_id)
                            } else if (parsed.type === 'citations') {
                                setCitations(assistantMsgId, parsed.citations as Citation[])
                            } else if (parsed.type === 'cached') {
                                appendToken(assistantMsgId, parsed.answer)
                                setCitations(assistantMsgId, parsed.citations as Citation[])
                            }
                        } catch { }
                    }
                }
            } catch (err) {
                appendToken(assistantMsgId, '\n\n⚠️ Error: ' + (err as Error).message)
            } finally {
                setStreaming(false)
            }
        },
        [addMessage, appendToken, setCitations, setStreaming, setSessionId],
    )

    return { sendMessage }
}
