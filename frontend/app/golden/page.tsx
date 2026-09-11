'use client'

import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Save, Download, Upload, CheckCircle, AlertCircle } from 'lucide-react'
import Link from 'next/link'

const INTENTS = [
  'order_status',
  'order_issue',
  'refund_request',
  'billing_issue',
  'account_access',
  'account_issue',
  'product_info',
  'general_inquiry',
  'complaint',
  'escalation_required'
]

const ACTIONS = ['AUTO_HANDLE', 'ESCALATE']

interface AnnotationData {
  id: number
  message: string
  heuristic_intent: string
  human_intent: string
  heuristic_action: string
  human_action: string
  annotation_notes: string
  source_conversation: string
}

export default function GoldenSetAnnotation() {
  const [data, setData] = useState<AnnotationData[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [currentAnnotation, setCurrentAnnotation] = useState({
    human_intent: '',
    human_action: '',
    annotation_notes: ''
  })

  useEffect(() => {
    loadAnnotationData()
  }, [])

  useEffect(() => {
    if (data.length > 0 && currentIndex < data.length) {
      setCurrentAnnotation({
        human_intent: data[currentIndex].human_intent || '',
        human_action: data[currentIndex].human_action || '',
        annotation_notes: data[currentIndex].annotation_notes || ''
      })
    }
  }, [currentIndex, data])

  const loadAnnotationData = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/golden`)
      if (response.ok) {
        const jsonData = await response.json()
        setData(jsonData)
      }
    } catch (error) {
      console.error('Failed to load annotation data:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveCurrentAnnotation = async () => {
    setSaving(true)
    setSaveStatus('idle')
    
    try {
      const updatedData = [...data]
      updatedData[currentIndex] = {
        ...updatedData[currentIndex],
        human_intent: currentAnnotation.human_intent,
        human_action: currentAnnotation.human_action,
        annotation_notes: currentAnnotation.annotation_notes
      }
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/golden`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: updatedData })
      })
      
      if (response.ok) {
        setData(updatedData)
        setSaveStatus('success')
        setTimeout(() => setSaveStatus('idle'), 2000)
      } else {
        setSaveStatus('error')
      }
    } catch (error) {
      console.error('Failed to save annotation:', error)
      setSaveStatus('error')
    } finally {
      setSaving(false)
    }
  }

  const exportAnnotations = () => {
    const csv = [
      ['id', 'message', 'heuristic_intent', 'human_intent', 'heuristic_action', 'human_action', 'annotation_notes', 'source_conversation'],
      ...data.map(row => [
        row.id,
        `"${row.message.replace(/"/g, '""')}"`,
        row.heuristic_intent,
        row.human_intent || '',
        row.heuristic_action,
        row.human_action || '',
        `"${(row.annotation_notes || '').replace(/"/g, '""')}"`,
        row.source_conversation
      ])
    ].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'golden_annotated.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const goToNext = () => {
    if (currentIndex < data.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const goToUnannotated = () => {
    const nextUnannotated = data.findIndex((_, i) => i > currentIndex && !data[i].human_intent)
    if (nextUnannotated !== -1) {
      setCurrentIndex(nextUnannotated)
    }
  }

  const annotatedCount = data.filter(d => d.human_intent).length
  const progress = data.length > 0 ? (annotatedCount / data.length) * 100 : 0

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-slate-600">Loading annotation data...</div>
      </div>
    )
  }

  const currentItem = data[currentIndex]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link href="/" className="text-slate-600 hover:text-primary-600">
                <ChevronLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Golden Set Annotation</h1>
                <p className="text-sm text-slate-600">Human-label the evaluation set</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-slate-600">
                Progress: {annotatedCount}/{data.length} ({progress.toFixed(1)}%)
              </div>
              <button
                onClick={exportAnnotations}
                className="flex items-center space-x-2 bg-slate-600 text-white px-4 py-2 rounded-md hover:bg-slate-700 transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentItem && (
          <div className="space-y-6">
            {/* Navigation */}
            <div className="flex items-center justify-between bg-white rounded-lg shadow-sm border border-slate-200 p-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={goToPrevious}
                  disabled={currentIndex === 0}
                  className="flex items-center space-x-2 px-4 py-2 rounded-md border border-slate-300 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </button>
                <div className="text-slate-600">
                  Example {currentIndex + 1} of {data.length}
                </div>
                <button
                  onClick={goToNext}
                  disabled={currentIndex === data.length - 1}
                  className="flex items-center space-x-2 px-4 py-2 rounded-md border border-slate-300 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
              <button
                onClick={goToUnannotated}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Skip to next unannotated
              </button>
            </div>

            {/* Customer Message */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Customer Message</h3>
              <div className="bg-slate-50 rounded-md p-4 text-slate-700 border border-slate-200">
                {currentItem.message}
              </div>
              <div className="mt-2 text-sm text-slate-500">
                Source: {currentItem.source_conversation}
              </div>
            </div>

            {/* Heuristic Suggestion */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Heuristic Suggestion</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Suggested Intent
                  </label>
                  <div className="bg-amber-50 rounded-md p-3 text-amber-800 border border-amber-200">
                    {currentItem.heuristic_intent}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Suggested Action
                  </label>
                  <div className="bg-amber-50 rounded-md p-3 text-amber-800 border border-amber-200">
                    {currentItem.heuristic_action}
                  </div>
                </div>
              </div>
              <p className="mt-3 text-sm text-slate-500">
                This is a heuristic suggestion based on keyword matching. Please verify independently.
              </p>
            </div>

            {/* Human Annotation */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Human Annotation</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Correct Intent <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={currentAnnotation.human_intent}
                    onChange={(e) => setCurrentAnnotation({ ...currentAnnotation, human_intent: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Select intent...</option>
                    {INTENTS.map(intent => (
                      <option key={intent} value={intent}>{intent}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Correct Action <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={currentAnnotation.human_action}
                    onChange={(e) => setCurrentAnnotation({ ...currentAnnotation, human_action: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Select action...</option>
                    {ACTIONS.map(action => (
                      <option key={action} value={action}>{action}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Annotation Notes (optional)
                  </label>
                  <textarea
                    value={currentAnnotation.annotation_notes}
                    onChange={(e) => setCurrentAnnotation({ ...currentAnnotation, annotation_notes: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Add any notes about this annotation..."
                  />
                </div>

                <div className="flex items-center space-x-4 pt-4">
                  <button
                    onClick={saveCurrentAnnotation}
                    disabled={saving || !currentAnnotation.human_intent || !currentAnnotation.human_action}
                    className="flex items-center space-x-2 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Save className="h-4 w-4" />
                    <span>{saving ? 'Saving...' : 'Save Annotation'}</span>
                  </button>
                  {saveStatus === 'success' && (
                    <div className="flex items-center space-x-2 text-green-600">
                      <CheckCircle className="h-5 w-5" />
                      <span>Saved successfully</span>
                    </div>
                  )}
                  {saveStatus === 'error' && (
                    <div className="flex items-center space-x-2 text-red-600">
                      <AlertCircle className="h-5 w-5" />
                      <span>Failed to save</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Intent Reference */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-3">Intent Reference</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <div><strong>order_status:</strong> Order tracking and delivery inquiries</div>
                  <div><strong>order_issue:</strong> Problems with received orders</div>
                  <div><strong>refund_request:</strong> Refund and return requests</div>
                  <div><strong>billing_issue:</strong> Payment and billing problems</div>
                  <div><strong>account_access:</strong> Login and account access issues</div>
                </div>
                <div className="space-y-2">
                  <div><strong>account_issue:</strong> Account settings and updates</div>
                  <div><strong>product_info:</strong> Product information and availability</div>
                  <div><strong>general_inquiry:</strong> General questions and policies</div>
                  <div><strong>complaint:</strong> Customer dissatisfaction and feedback</div>
                  <div><strong>escalation_required:</strong> Legal threats, security issues, regulatory complaints</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
