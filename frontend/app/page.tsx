'use client'

import { useState } from 'react'
import Link from 'next/link'
import { MessageSquare, BarChart3, AlertTriangle, Info, CheckSquare } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <MessageSquare className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-slate-900">Hiver AI Support Agent</h1>
            </div>
            <nav className="flex space-x-4">
              <Link href="/" className="text-slate-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Agent
              </Link>
              <Link href="/evaluation" className="text-slate-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Evaluation
              </Link>
              <Link href="/golden" className="text-slate-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Golden Set
              </Link>
              <Link href="/failures" className="text-slate-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Failures
              </Link>
              <Link href="/about" className="text-slate-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                About
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Agent Card */}
          <Link href="/agent" className="group">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <MessageSquare className="h-8 w-8 text-primary-600" />
                <h2 className="text-xl font-semibold text-slate-900">AI Agent</h2>
              </div>
              <p className="text-slate-600 mb-4">
                Classify customer messages, retrieve historical evidence, and generate grounded responses.
              </p>
              <div className="text-primary-600 text-sm font-medium group-hover:underline">
                Try the agent →
              </div>
            </div>
          </Link>

          {/* Evaluation Card */}
          <Link href="/evaluation" className="group">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <BarChart3 className="h-8 w-8 text-primary-600" />
                <h2 className="text-xl font-semibold text-slate-900">Evaluation Dashboard</h2>
              </div>
              <p className="text-slate-600 mb-4">
                View intent classification metrics, escalation performance, and baseline comparisons.
              </p>
              <div className="text-primary-600 text-sm font-medium group-hover:underline">
                View metrics →
              </div>
            </div>
          </Link>

          {/* Golden Set Card */}
          <Link href="/golden" className="group">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <CheckSquare className="h-8 w-8 text-primary-600" />
                <h2 className="text-xl font-semibold text-slate-900">Golden Set Annotation</h2>
              </div>
              <p className="text-slate-600 mb-4">
                Human-label the 200-example evaluation set with intent and action annotations.
              </p>
              <div className="text-primary-600 text-sm font-medium group-hover:underline">
                Annotate examples →
              </div>
            </div>
          </Link>

          {/* Failure Analysis Card */}
          <Link href="/failures" className="group">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <AlertTriangle className="h-8 w-8 text-primary-600" />
                <h2 className="text-xl font-semibold text-slate-900">Failure Analysis</h2>
              </div>
              <p className="text-slate-600 mb-4">
                Explore the top 5 failure modes with real examples and improvement strategies.
              </p>
              <div className="text-primary-600 text-sm font-medium group-hover:underline">
                Analyze failures →
              </div>
            </div>
          </Link>

          {/* About Card */}
          <Link href="/about" className="group">
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <Info className="h-8 w-8 text-primary-600" />
                <h2 className="text-xl font-semibold text-slate-900">Methodology</h2>
              </div>
              <p className="text-slate-600 mb-4">
                Learn about the dataset, intent taxonomy, retrieval system, and evaluation methodology.
              </p>
              <div className="text-primary-600 text-sm font-medium group-hover:underline">
                Read methodology →
              </div>
            </div>
          </Link>
        </div>
      </main>
    </div>
  )
}
