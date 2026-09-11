'use client'

import { ArrowLeft, Info } from 'lucide-react'
import Link from 'next/link'

export default function AboutPage() {
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
            <h1 className="text-xl font-semibold text-slate-900">Methodology</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Dataset */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Dataset</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                Customer Support on Twitter dataset from Kaggle (thoughtvector/customer-support-on-twitter). 
                Contains ~3M tweets from various brands' customer support accounts.
              </p>
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium text-slate-900">Selected Brand</div>
                    <div className="text-slate-600">AmazonHelp - highest volume with diverse conversation types</div>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium text-slate-900">Preprocessing</div>
                    <div className="text-slate-600">Text cleaning, conversation reconstruction, train/dev/test splits</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Intent Taxonomy */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Intent Taxonomy</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                10 intents derived from actual customer support conversations, not from Banking77.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
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
                ].map((intent) => (
                  <div key={intent} className="bg-slate-50 rounded-lg px-3 py-2 text-sm text-slate-700">
                    {intent}
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Classification */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Classification</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                TF-IDF + Logistic Regression classifier. Deterministic, interpretable, no external APIs required.
              </p>
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">TF-IDF vectorization with 5000 features, bigrams</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Logistic Regression with class weighting for imbalance</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Probability estimates for confidence-based escalation</div>
                </div>
              </div>
            </div>
          </section>

          {/* Retrieval */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Historical Retrieval</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                Semantic search using sentence-transformers + FAISS, with TF-IDF fallback.
              </p>
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Sentence-transformers (all-MiniLM-L6-v2) for embeddings</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">FAISS for efficient similarity search</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">TF-IDF cosine similarity fallback for compatibility</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Returns top 5 similar historical examples with similarity scores</div>
                </div>
              </div>
            </div>
          </section>

          {/* Escalation */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Escalation Policy</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                Transparent escalation based on confidence, evidence, and intent type.
              </p>
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Confidence threshold: 0.6 (below → escalate)</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Similarity threshold: 0.3 (below → escalate)</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Escalation-required intents always escalate</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Prefers escalation when evidence is insufficient</div>
                </div>
              </div>
            </div>
          </section>

          {/* Evaluation */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Evaluation</h2>
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <p className="text-slate-600 mb-4">
                200-example golden set with stratified sampling by intent and difficulty.
              </p>
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Intent: accuracy, macro F1, weighted F1, per-class metrics</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Escalation: accuracy, precision, recall, F1, false negative rate</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">Baselines: majority class, TF-IDF + LR</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <div className="text-slate-600">LLM-as-judge with deterministic fallback (no API required)</div>
                </div>
              </div>
            </div>
          </section>

          {/* Limitations */}
          <section>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Limitations</h2>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
              <ul className="space-y-2 text-slate-700">
                <li>• This is a demo/evaluation system, not a production customer support platform</li>
                <li>• No Twitter integration, real accounts, billing systems, or CRM integration</li>
                <li>• Training labels are synthetic for demonstration (real deployment requires human labeling)</li>
                <li>• Template-based responses (no generative AI due to API constraints)</li>
                <li>• Evaluation on curated golden set may not reflect real-world distribution</li>
                <li>• Deterministic judge is less nuanced than true LLM evaluation</li>
              </ul>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
