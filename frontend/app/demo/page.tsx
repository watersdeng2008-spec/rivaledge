'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Search, TrendingUp, ArrowRight } from 'lucide-react';
import { demoExamples, type DemoExample } from './data';

const aiMeta = [
  { key: 'chatgpt' as const, label: 'ChatGPT', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: '🤖' },
  { key: 'claude' as const, label: 'Claude', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: '🧠' },
  { key: 'perplexity' as const, label: 'Perplexity', color: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/20', icon: '🔍' },
];

export default function DemoPage() {
  const [selected, setSelected] = useState<DemoExample>(demoExamples[0]);
  const [customCompany, setCustomCompany] = useState('');
  const [customCompetitor, setCustomCompetitor] = useState('');

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link href="/">
              <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            </Link>
            <Link href="/" className="text-xl font-bold text-blue-400 hover:text-blue-300 transition-colors">
              RivalEdge
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/demo" className="text-sm text-blue-400 font-medium">Demo</Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">Pricing</Link>
            <Link href="/sign-in" className="text-slate-400 hover:text-white text-sm transition-colors">Sign in</Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-16 pb-8 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-1.5 text-sm text-blue-400 mb-6">
          <Sparkles className="w-4 h-4" />
          Interactive Demo
        </div>
        <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-4">
          See What AI Says About
          <br />
          <span className="text-blue-400">You vs Your Competitors</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Pick a comparison below to see how ChatGPT, Claude, and Perplexity describe each company.
          Then imagine tracking this every week.
        </p>
      </section>

      {/* Example Selector */}
      <section className="max-w-6xl mx-auto px-6 pb-8">
        <div className="flex flex-wrap justify-center gap-3">
          {demoExamples.map((ex) => (
            <button
              key={ex.id}
              onClick={() => setSelected(ex)}
              className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                selected.id === ex.id
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'
              }`}
            >
              {ex.company} vs {ex.competitor}
            </button>
          ))}
        </div>
      </section>

      {/* AI Response Cards */}
      <section className="max-w-6xl mx-auto px-6 pb-12">
        <div className="grid md:grid-cols-3 gap-6">
          {aiMeta.map((ai) => (
            <div
              key={ai.key}
              className={`${ai.bg} ${ai.border} border rounded-2xl p-6 flex flex-col`}
            >
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xl">{ai.icon}</span>
                <h3 className={`text-lg font-semibold ${ai.color}`}>{ai.label}</h3>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed flex-1">
                {selected.responses[ai.key]}
              </p>
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-xs text-slate-500">
                  This is a canned example. Live queries return fresh AI responses.
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Try Your Own (Tier 2 placeholder) */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold mb-3">Try Your Own Comparison</h2>
          <p className="text-slate-400 mb-6">
            Enter any two companies and get real AI responses. Coming soon.
          </p>
          <form onSubmit={(e) => e.preventDefault()} className="flex flex-col sm:flex-row gap-4 justify-center max-w-lg mx-auto">
            <input
              type="text"
              placeholder="Your company"
              value={customCompany}
              onChange={(e) => setCustomCompany(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <span className="hidden sm:flex items-center text-slate-500 font-medium">vs</span>
            <input
              type="text"
              placeholder="Competitor"
              value={customCompetitor}
              onChange={(e) => setCustomCompetitor(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="submit"
              disabled={!customCompany || !customCompetitor}
              className="bg-slate-700 text-slate-400 px-6 py-3 rounded-xl text-sm font-medium cursor-not-allowed"
            >
              Coming Soon
            </button>
          </form>
          <p className="text-xs text-slate-500 mt-4">
            Live multi-AI queries cost us API credits. We&apos;re making it free for trial users soon.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="bg-gradient-to-br from-blue-600/20 to-violet-600/20 border border-blue-500/20 rounded-2xl p-10 text-center">
          <h2 className="text-3xl font-bold mb-3">Want real-time AI monitoring?</h2>
          <p className="text-slate-400 mb-6 max-w-lg mx-auto">
            Track how ChatGPT, Claude, and Perplexity describe your company — and your competitors — every week. From $49/mo.
          </p>
          <Link
            href="/sign-up"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl text-lg font-semibold transition-colors shadow-lg shadow-blue-500/20"
          >
            Start free trial <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8 text-center text-sm text-slate-500">
        <p>© {new Date().getFullYear()} RivalEdge. All rights reserved.</p>
      </footer>
    </div>
  );
}
