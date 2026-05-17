import Link from 'next/link';
import { ArrowLeft, Calendar, Clock, Check, X } from 'lucide-react';

export const metadata = {
  title: 'RivalEdge vs Klue: A Side-by-Side Comparison — RivalEdge',
  description: 'Enterprise CI vs startup-friendly AI. See why lean teams are choosing RivalEdge over Klue.',
};

export default function ComparisonPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/" className="text-slate-400 hover:text-white text-sm transition-colors">Home</Link>
            <Link href="/blog" className="text-slate-400 hover:text-white text-sm transition-colors">Blog</Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">Pricing</Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">Start free trial</Link>
          </div>
        </div>
      </nav>

      <article className="max-w-4xl mx-auto px-6 pt-12 pb-20">
        <Link href="/blog" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to blog
        </Link>

        <div className="flex items-center gap-3 mb-4">
          <span className="bg-purple-600/10 text-purple-400 text-xs px-2 py-1 rounded-full">Comparison</span>
          <span className="flex items-center gap-1 text-slate-500 text-sm"><Calendar className="w-3.5 h-3.5" />May 17, 2026</span>
          <span className="flex items-center gap-1 text-slate-500 text-sm"><Clock className="w-3.5 h-3.5" />4 min read</span>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold mb-6">RivalEdge vs Klue: A Side-by-Side Comparison</h1>
        <p className="text-lg text-slate-400 mb-8">Enterprise CI vs startup-friendly AI. See why lean teams are choosing RivalEdge.</p>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">At a Glance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 pr-4">Feature</th>
                  <th className="text-left py-3 pr-4 text-blue-400">RivalEdge</th>
                  <th className="text-left py-3">Klue</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Starting Price</td><td className="py-3 pr-4">$49/month</td><td className="py-3">Custom (enterprise)</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Setup Time</td><td className="py-3 pr-4">5 minutes</td><td className="py-3">1-2 months</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Self-Serve Signup</td><td className="py-3 pr-4"><Check className="w-4 h-4 text-green-400" /></td><td className="py-3"><X className="w-4 h-4 text-red-400" /></td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">AI-Generated Reports</td><td className="py-3 pr-4"><Check className="w-4 h-4 text-green-400" /></td><td className="py-3"><X className="w-4 h-4 text-red-400" /></td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">GEO Monitoring</td><td className="py-3 pr-4"><Check className="w-4 h-4 text-green-400" /></td><td className="py-3"><X className="w-4 h-4 text-red-400" /></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-3">The Bottom Line</h2>
          <p className="text-slate-300 mb-4">Klue is the sales-focused enterprise choice. Strong for win/loss and sales enablement.</p>
          <p className="text-slate-300 mb-4">RivalEdge is the agile, AI-powered alternative. Faster setup, AI features, and 30-80x cheaper.</p>
          <p className="font-medium text-white">If you need competitive intelligence now with AI-generated insights, RivalEdge wins.</p>
        </div>

        <Link href="/sign-up" className="inline-block bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors">
          Start RivalEdge free trial →
        </Link>
      </article>
    </div>
  );
}
