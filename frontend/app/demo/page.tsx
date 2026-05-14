"use client";

import { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Play, ArrowRight, BookOpen, ExternalLink } from 'lucide-react';
import { demoExamples, type DemoExample } from './data';

const aiMeta = [
  { key: 'chatgpt' as const, label: 'ChatGPT', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: '🤖' },
  { key: 'claude' as const, label: 'Claude', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: '🧠' },
  { key: 'perplexity' as const, label: 'Perplexity', color: 'text-violet-400', bg: 'bg-violet-500/10', border: 'border-violet-500/20', icon: '🔍' },
];

export default function DemoPage() {
  const [selected, setSelected] = useState<DemoExample>(demoExamples[0]);

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

      {/* Demo Video */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <div className="bg-slate-900 border border-blue-500/20 rounded-2xl overflow-hidden">
          <video
            className="w-full"
            controls
            preload="metadata"
            poster="/rivaledge-demo-v3-poster.jpg"
          >
            <source src="/rivaledge-demo-v3-opt.mp4" type="video/mp4" />
        Your browser does not support the video tag.
          </video>
        </div>
      </section>

      {/* Substack Essay */}
      <section className="max-w-4xl mx-auto px-6 pb-16">
        <div className="bg-slate-900 border border-purple-500/20 rounded-2xl p-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 bg-purple-600/10 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-purple-400" />
            </div>
            <h2 className="text-xl font-bold">GEO ≠ SEO 2.0</h2>
          </div>
          <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed mb-6">
            Our CEO breaks down why AI discovery is a structural shift in how markets work —
            not just &quot;SEO with new buzzwords.&quot;
          </p>
          <a
            href="https://open.substack.com/pub/dengw/p/geo-is-not-seo-20?r=6qf1gl&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors"
          >
            Read the essay
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="bg-gradient-to-br from-blue-600/20 to-violet-600/20 border border-blue-500/20 rounded-2xl p-10 text-center">
          <h2 className="text-3xl font-bold mb-3">Want real-time AI monitoring?</h2>
          <p className="text-slate-400 mb-6 max-w-lg mx-auto">
            Track how ChatGPT, Claude, and Perplexity describe your company — and your competitors — every week. From $999/mo.
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
