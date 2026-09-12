'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, BarChart3, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.get(`${apiUrl}/metrics`)
      setMetrics(response.data)
      setError(null)
    } catch (error) {
      console.error('Error fetching metrics:', error)
      setError('Failed to load evaluation metrics')
    } finally {
      setLoading(false)
    }
  }

  const hasEvaluationData = metrics && (
    metrics.intent_macro_f1 !== null || 
    metrics.intent_accuracy !== null ||
    metrics.escalation_f1 !== null ||
    metrics.reply_quality !== null
  )

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
            <h1 className="text-xl font-semibold text-slate-900">Evaluation Dashboard</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading evaluation metrics...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-6 w-6 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-900">Error Loading Metrics</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        ) : !hasEvaluationData ? (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <Clock className="h-6 w-6 text-amber-600" />
              <div>
                <h3 className="font-semibold text-amber-900">Evaluation Not Run Yet</h3>
                <p className="text-sm text-amber-700 mt-1">
                  Run the evaluation script to generate metrics: <code className="bg-amber-100 px-1 rounded">python evaluation/run_evaluation.py</code>
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Evaluation Status */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                  <div>
                    <h3 className="font-semibold text-slate-900">Evaluation Complete</h3>
                    <p className="text-sm text-slate-600">Metrics based on heuristic labels</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-600">Label Source</div>
                  <div className="font-medium text-slate-900">HEURISTIC</div>
                </div>
              </div>
            </div>

            {/* Headline Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard
                title="Intent Macro F1"
                value={metrics?.intent_macro_f1}
                format="percentage"
              />
              <MetricCard
                title="Intent Accuracy"
                value={metrics?.intent_accuracy}
                format="percentage"
              />
              <MetricCard
                title="Escalation F1"
                value={metrics?.escalation_f1}
                format="percentage"
              />
              <MetricCard
                title="Escalation Recall"
                value={metrics?.escalation_recall}
                format="percentage"
              />
            </div>

            {/* Reply Quality */}
            {metrics?.reply_quality !== null && metrics?.reply_quality !== undefined && (
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Reply Quality</h2>
                <div className="text-3xl font-bold text-slate-900">
                  {metrics.reply_quality.toFixed(2)}/5.0
                </div>
                <p className="text-sm text-slate-600 mt-1">Overall quality score</p>
              </div>
            )}

            {/* Baseline Comparison */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Baseline Comparison</h2>
              {metrics?.baseline_comparison ? (
                <div className="space-y-4">
                  {Object.entries(metrics.baseline_comparison).map(([name, data]: [string, any]) => (
                    <div key={name} className="border border-slate-200 rounded-lg p-4">
                      <div className="font-medium text-slate-900 capitalize">{name.replace('_', ' ')}</div>
                      <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-slate-600">Accuracy:</span>
                          <span className="ml-2 font-medium">{data.accuracy ? (data.accuracy * 100).toFixed(1) + '%' : 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-slate-600">Macro F1:</span>
                          <span className="ml-2 font-medium">{data.macro_f1 ? (data.macro_f1 * 100).toFixed(1) + '%' : 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-600">No baseline comparison data available</p>
              )}
            </div>

            {/* Label Source Warning */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
                <div className="text-sm text-amber-800">
                  <strong>Heuristic Labels:</strong> These metrics are based on heuristic labels. 
                  For production-grade evaluation, complete human annotation of the golden set is recommended.
                  Visit the <Link href="/golden" className="underline font-medium">Golden Set</Link> page to add human labels.
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function MetricCard({ title, value, format }: { title: string; value: any; format: 'percentage' | 'number' | 'text' }) {
  const displayValue = value === null || value === undefined 
    ? 'N/A' 
    : format === 'percentage' 
      ? `${(value * 100).toFixed(1)}%` 
      : format === 'number' 
        ? value.toFixed(2) 
        : value

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="text-sm font-medium text-slate-600 mb-2">{title}</div>
      <div className="text-3xl font-bold text-slate-900">{displayValue}</div>
    </div>
  )
}
