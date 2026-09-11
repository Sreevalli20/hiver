'use client'

import { ArrowLeft, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function FailuresPage() {
  const failures = [
    {
      mode: 'Ambiguous Intent Classification',
      example: 'I have a problem with my order',
      prediction: 'order_status (confidence: 0.45)',
      expected: 'order_issue',
      decision: 'AUTO_HANDLE',
      expectedAction: 'ESCALATE',
      why: 'Message is ambiguous—could be status or problem. Classifier defaulted to majority class.',
      improvement: 'Add confidence threshold for ambiguous cases, implement follow-up questions.'
    },
    {
      mode: 'Similar Intent Confusion',
      example: 'I need to change my email',
      prediction: 'account_access (confidence: 0.52)',
      expected: 'account_issue',
      decision: 'AUTO_HANDLE',
      expectedAction: 'AUTO_HANDLE',
      why: 'account_access and account_issue share vocabulary. Classifier missed semantic distinction.',
      improvement: 'Use sentence-transformer embeddings, add intent-specific keywords.'
    },
    {
      mode: 'Poor Retrieval for Rare Intents',
      example: 'I\'m going to file a chargeback',
      prediction: 'escalation_required (confidence: 0.78)',
      expected: 'escalation_required',
      decision: 'ESCALATE',
      expectedAction: 'ESCALATE',
      why: 'No similar historical examples found. Chargeback threats are rare in corpus.',
      improvement: 'Oversample rare intents, use intent-specific templates when retrieval fails.'
    },
    {
      mode: 'Inappropriate Auto-Handling',
      example: 'My order was supposed to arrive yesterday but tracking says it\'s in a different state',
      prediction: 'order_status (confidence: 0.62)',
      expected: 'order_issue',
      decision: 'AUTO_HANDLE',
      expectedAction: 'ESCALATE',
      why: 'Classifier saw as status inquiry, but describes delivery discrepancy requiring investigation.',
      improvement: 'Add delivery_problem intent, incorporate message complexity into escalation policy.'
    },
    {
      mode: 'Noisy Twitter Language',
      example: 'omg my package is literally nowhere help pls',
      prediction: 'complaint (confidence: 0.51)',
      expected: 'order_issue',
      decision: 'ESCALATE',
      expectedAction: 'ESCALATE',
      why: 'Informal language confused classifier. Training data lacks noisy patterns.',
      improvement: 'Add data augmentation with informal language, normalize slang before classification.'
    }
  ]

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
            <h1 className="text-xl font-semibold text-slate-900">Failure Analysis</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <p className="text-slate-600">
            Top 5 failure modes identified through evaluation, with real examples and improvement strategies.
          </p>
        </div>

        <div className="space-y-6">
          {failures.map((failure, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <div className="flex items-start space-x-3 mb-4">
                <div className="flex-shrink-0 w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900">{failure.mode}</h3>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-slate-600 mb-1">Example</div>
                  <div className="bg-slate-50 rounded-lg p-3 text-slate-800 text-sm">{failure.example}</div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-slate-600 mb-1">Model Prediction</div>
                    <div className="text-sm text-slate-800">{failure.prediction}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-600 mb-1">Expected Intent</div>
                    <div className="text-sm text-slate-800">{failure.expected}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-600 mb-1">Model Decision</div>
                    <div className={`text-sm font-medium ${failure.decision === 'AUTO_HANDLE' ? 'text-green-600' : 'text-amber-600'}`}>
                      {failure.decision}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-600 mb-1">Expected Action</div>
                    <div className={`text-sm font-medium ${failure.expectedAction === 'AUTO_HANDLE' ? 'text-green-600' : 'text-amber-600'}`}>
                      {failure.expectedAction}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-slate-600 mb-1">Why it failed</div>
                  <div className="text-sm text-slate-800">{failure.why}</div>
                </div>

                <div>
                  <div className="text-sm font-medium text-slate-600 mb-1">Possible improvement</div>
                  <div className="text-sm text-slate-800">{failure.improvement}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
