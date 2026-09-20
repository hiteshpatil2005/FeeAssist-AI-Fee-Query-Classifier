import { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble.jsx'
import ChatInput from './ChatInput.jsx'
import { useAuth } from '../context/AuthContext'

function formatTime(date) {
  return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

let nextId = 100

export default function ChatWindow({ language, initialQuery }) {
  const { user } = useAuth()

  const [messages, setMessages] = useState(() => [
    {
      id: 1,
      role: 'assistant',
      content: `Hello${user?.name ? ' ' + user.name.split(' ')[0] : ''}! I'm FeeAssist AI. I'm connected to your student fee records. You can ask me about pending amounts, installment plans, due dates, scholarship status, or previous receipts in English, Hindi, or Marathi.`,
      timestamp: formatTime(new Date()),
    },
  ])
  const [waiting, setWaiting] = useState(false)
  const bottomRef = useRef(null)
  const initialQueryHandled = useRef(false)

  const DEMO_RESPONSES = {
    "How much fee do I have pending?":
      "Based on your student fee record, you currently have ₹25,000 pending for Semester 5 (AY 2025-26). Your ₹10,000 scholarship discount has already been applied.",
    "When is my fee due?":
      "Your pending installment for Semester 5 is due on 15th November 2026. Make sure to complete payment before the deadline to avoid late fees.",
    "Can I pay my fees in installments?":
      "Yes, installment payments are enabled for your department. You can pay the pending ₹25,000 in two installments before November 15th.",
    "Show my payment history":
      "Here is your recorded payment history:\n• 20 Aug 2025: ₹50,000 (Tuition Fee Installment 1 - UPI)\n• 15 Jan 2025: ₹70,000 (Tuition & Exam Fee - Net Banking) ✓",
  }

  const SUGGESTED_QUESTIONS = Object.keys(DEMO_RESPONSES)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, waiting])

  const sendMessage = (text) => {
    if (!text.trim()) return

    const userMsg = {
      id: nextId++,
      role: 'user',
      content: text,
      timestamp: formatTime(new Date()),
    }
    setMessages((prev) => [...prev, userMsg])
    setWaiting(true)

    // Match or fallback
    let responseText = DEMO_RESPONSES[text]
    if (!responseText) {
      if (text.toLowerCase().includes('pending') || text.toLowerCase().includes('balance')) {
        responseText = `You currently have ₹25,000 pending for Semester 5. Your total semester fee is ₹75,000 and ₹50,000 has been paid.`
      } else if (text.toLowerCase().includes('due') || text.toLowerCase().includes('date')) {
        responseText = `Your next fee deadline is 15th November 2026 for Semester 5.`
      } else if (text.toLowerCase().includes('payment') || text.toLowerCase().includes('paid')) {
        responseText = `You made a payment of ₹50,000 via UPI on 20 Aug 2025 (TXN192847192). You can view the full receipt in the Payment History tab.`
      } else {
        responseText = `I received your query: "${text}". I have cross-checked your student profile (${user?.name || 'Student'}, ${user?.course || 'Degree'}). Feel free to check the 'My Fees' tab for real-time itemized breakdown.`
      }
    }

    setTimeout(() => {
      const assistantMsg = {
        id: nextId++,
        role: 'assistant',
        content: responseText,
        timestamp: formatTime(new Date()),
      }
      setMessages((prev) => [...prev, assistantMsg])
      setWaiting(false)
    }, 700)
  }

  // Handle incoming initialQuery
  useEffect(() => {
    if (initialQuery && !initialQueryHandled.current) {
      initialQueryHandled.current = true
      sendMessage(initialQuery)
    }
  }, [initialQuery])

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}

        {/* Typing indicator while waiting */}
        {waiting && <MessageBubble role="assistant" isTyping />}

        {/* Suggested questions */}
        {messages.length === 1 && !waiting && (
          <div className="pt-2">
            <p className="text-xs text-[#6B7280] mb-2 font-medium uppercase tracking-wide">
              Suggested questions
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  id={`suggested-q-${q.replace(/\s+/g, '-').toLowerCase().slice(0, 30)}`}
                  type="button"
                  onClick={() => sendMessage(q)}
                  className="
                    px-3 py-2 text-sm rounded-lg cursor-pointer
                    bg-white border border-[#E5E7EB] text-[#1F2937]
                    hover:border-[#6D28D9] hover:text-[#6D28D9] hover:bg-[#F3E8FF]
                    transition-colors duration-150 text-left shadow-2xs
                  "
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Chat Input */}
      <ChatInput onSend={sendMessage} disabled={waiting} />
    </div>
  )
}
