'use client'

import { useState } from 'react'
import { ArrowLeft, Send, Copy, Check, AlertCircle, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'

export default function AgentPage() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const exampleMessages = [
    "Where is my order?",
    "I received the wrong item",
    "I can't log into my account",
    "What are your business hours?",
  ]

  const handleAnalyze = async () => {
    if (!message.trim()) return
    
    setLoading(true)
    setResult(null)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/predict`, { message })
      setResult(response.data)
    } catch (error) {
      console.error('Error:', error)
      setResult({ error: 'Failed to analyze message. Make sure the backend is running.' })
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getDecisionColor = (decision: string) => {
    return decision === 'AUTO_HANDLE' 
      ? 'bg-green-100 text-green-800 border-green-200' 
      : 'bg-amber-100 text-amber-800 border-amber-200'
  }

  const getDecisionIcon = (decision: string) => {
    return decision === 'AUTO_HANDLE' ? <CheckCircle className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 text-slate-600 hover:text-slate-900">
              <ArrowLeft className="h-5 w-5" />
              <span className="font-medium">Back</span>
            </Link>
            <h1 className="text-xl font-semibold text-slate-900">AI Support Agent</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Customer Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter a customer support message..."
            className="w-full h-32 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
          />
          
          {/* Example Messages */}
          <div className="mt-4 flex flex-wrap gap-2">
            {exampleMessages.map((msg) => (
              <button
                key={msg}
                onClick={() => setMessage(msg)}
                className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md transition-colors"
              >
                {msg}
              </button>
            ))}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !message.trim()}
            className="mt-4 w-full bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="h-5 w-5" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Error */}
            {result.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                {result.error}
              </div>
            )}

            {!result.error && (
              <>
                {/* Intent Card */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">Intent Classification</h2>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold text-slate-900">{result.intent}</div>
                      <div className="text-sm text-slate-600 mt-1">
                        Confidence: {(result.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="w-32">
                      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary-600 transition-all duration-500"
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Decision Card */}
                <div className={`rounded-lg shadow-sm border p-6 ${getDecisionColor(result.decision)}`}>
                  <h2 className="text-lg font-semibold mb-4">Escalation Decision</h2>
                  <div className="flex items-center space-x-3">
                    {getDecisionIcon(result.decision)}
                    <span className="text-2xl font-bold">{result.decision}</span>
                  </div>
                  <p className="mt-3 text-sm opacity-90">{result.reason}</p>
                </div>

                {/* Draft Reply Card */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900">Draft Reply</h2>
                    <button
                      onClick={() => handleCopy(result.reply)}
                      className="flex items-center space-x-1 text-sm text-slate-600 hover:text-slate-900"
                    >
                      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-4 text-slate-800">
                    {result.reply}
                  </div>
                  <div className="mt-2 text-xs text-slate-500">
                    Based on {result.evidence.length} similar historical cases
                  </div>
                </div>

                {/* Historical Evidence */}
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">Historical Evidence</h2>
                  <div className="space-y-4">
                    {result.evidence.slice(0, 5).map((evidence: any, index: number) => (
                      <div key={index} className="border border-slate-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-slate-600">
                            Similarity: {(evidence.similarity * 100).toFixed(1)}%
                          </span>
                          <span className="text-xs text-slate-500">{evidence.conversation_id}</span>
                        </div>
                        <div className="space-y-2">
                          <div>
                            <div className="text-xs font-medium text-slate-600 mb-1">Customer:</div>
                            <div className="text-sm text-slate-800">{evidence.customer_message}</div>
                          </div>
                          <div>
                            <div className="text-xs font-medium text-slate-600 mb-1">Brand Response:</div>
                            <div className="text-sm text-slate-800">{evidence.brand_response}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
