'use client'

import type { Message } from '@/store/chatStore'
import SourceCitation from './SourceCitation'

interface Props {
    message: Message
    isStreaming?: boolean
}

export default function MessageBubble({ message, isStreaming }: Props) {
    const isUser = message.role === 'user'

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}>
            <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
                {/* Avatar */}
                {!isUser && (
                    <div className="flex items-center gap-2 mb-1.5">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
                            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                            </svg>
                        </div>
                        <span className="text-xs text-[var(--text-muted)] font-medium">RAG Assistant</span>
                    </div>
                )}

                {/* Bubble */}
                <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${isUser
                            ? 'bg-brand-600 text-white rounded-tr-sm'
                            : 'surface rounded-tl-sm text-[var(--text)]'
                        }`}
                >
                    {message.content}
                    {isStreaming && !isUser && (
                        <span className="inline-block w-1.5 h-4 bg-brand-500 ml-0.5 animate-pulse-slow rounded-full" />
                    )}
                </div>

                {/* Citations */}
                {!isUser && message.citations && message.citations.length > 0 && (
                    <SourceCitation citations={message.citations} />
                )}
            </div>
        </div>
    )
}
