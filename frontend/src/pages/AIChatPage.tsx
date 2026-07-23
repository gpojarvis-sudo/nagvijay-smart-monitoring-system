import { useState } from 'react'
import { Bot, Send, Sparkles } from 'lucide-react'
import api from '@/services/api'

interface Message { role: 'user' | 'assistant'; content: string; suggestions?: string[] }

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Namaste! 🙏 I am NagVijay AI Assistant for India Post. I can help you analyze performance, identify low offices, generate insights. Try: "Show low performing BOs in Nagpur East" or "Which schemes need attention?"', suggestions: ['Show overall stats', 'Top performers?', 'Low offices needing support?'] }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async (text: string = input) => {
    if (!text.trim()) return
    const userMsg: Message = { role: 'user', content: text }
    setMessages(m => [...m, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await api.post('/ai/chat', { message: text, context: { division: 'Nagpur City' } })
      const data = res.data.data
      setMessages(m => [...m, { role: 'assistant', content: data.response, suggestions: data.suggestions }])
    } catch (e: any) {
      setMessages(m => [...m, { role: 'assistant', content: `AI is not configured yet. Set GEMINI_API_KEY in backend .env. Error: ${e.message}. Meanwhile, you can view dashboard for insights.` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-xl flex items-center justify-center text-white"><Bot size={20} /></div>
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">AI Assistant <span className="px-2 py-0.5 bg-violet-100 text-violet-700 rounded-full text-xs">Gemini 1.5 Flash</span></h1>
          <p className="text-sm text-gray-600">Context-aware analytics for India Post • Nagpur City Division</p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-violet-50 to-indigo-50 border border-violet-200 rounded-xl p-4 flex gap-3">
        <Sparkles className="text-violet-600 flex-shrink-0" size={18} />
        <p className="text-sm text-violet-900"><strong>Capabilities:</strong> Natural language queries, anomaly detection, report summarization, RAG over office/employee data. Example: "Why is Itwari BO low?" • "Compare PLI vs RPLI this month"</p>
      </div>

      <div className="bg-white border rounded-xl shadow-sm flex flex-col h-[600px]">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-red-600 text-white rounded-br-sm' : 'bg-gray-100 text-gray-900 rounded-bl-sm'}`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.suggestions && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.suggestions.map((s, idx) => (
                      <button key={idx} onClick={() => sendMessage(s)} className="px-3 py-1 bg-white text-violet-700 border border-violet-200 rounded-full text-xs hover:bg-violet-50">{s}</button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="flex justify-start"><div className="bg-gray-100 rounded-2xl px-4 py-3 text-sm animate-pulse">Thinking...</div></div>}
        </div>

        <div className="p-4 border-t flex gap-3">
          <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Ask about performance, offices, targets..." className="flex-1 px-4 py-3 border rounded-xl focus:ring-2 focus:ring-violet-500" />
          <button onClick={() => sendMessage()} disabled={loading} className="px-5 py-3 bg-violet-600 text-white rounded-xl hover:bg-violet-700 disabled:opacity-50 flex items-center gap-2"><Send size={18} /> Send</button>
        </div>
      </div>
    </div>
  )
}
