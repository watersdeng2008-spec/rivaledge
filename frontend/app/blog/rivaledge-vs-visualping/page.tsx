import Link from 'next/link';
import { ArrowLeft, Calendar, Clock } from 'lucide-react';

export const metadata = {
  title: 'RivalEdge vs Visualping: A Side-by-Side Comparison — RivalEdge',
  description: 'Change detection vs AI-powered intelligence. Why RivalEdge delivers 10x more value for $50 less per month.',
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
          <span className="flex items-center gap-1 text-slate-500 text-sm"><Clock className="w-3.5 h-3.5" />3 min read</span>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold mb-6">RivalEdge vs Visualping: A Side-by-Side Comparison</h1>
        <p className="text-lg text-slate-400 mb-8">Change detection vs AI-powered intelligence. Why RivalEdge delivers 10x more value for $50 less per month.</p>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">At a Glance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 pr-4">Feature</th>
                  <th className="text-left py-3 pr-4 text-blue-400">RivalEdge</th>
                  <th className="text-left py-3">Visualping</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Starting Price</td><td className="py-3 pr-4">$49/month</td><td className="py-3">$99/month</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">AI Analysis</td><td className="py-3 pr-4">✅ Yes</td><td className="py-3">❌ No</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Battle Cards</td><td className="py-3 pr-4">✅ Yes</td><td className="py-3">❌ No</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">GEO Monitoring</td><td className="py-3 pr-4">✅ Yes</td><td className="py-3">❌ No</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Weekly Reports</td><td className="py-3 pr-4">✅ AI-generated</td><td className="py-3">❌ Change alerts only</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-3">The Bottom Line</h2>
          <p className="text-slate-300 mb-4 font-medium">Visualping tells you <em>what</em> changed.</p>
          <p className="text-slate-300 mb-4 font-medium">RivalEdge tells you <em>what</em> changed, <em>why</em> it matters, and <em>what to do</em> about it.</p>
          <p className="text-white">For $50 less per month, RivalEdge delivers 10x more value.</p>
        </div>

        <Link href="/sign-up" className="inline-block bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors">
          Start RivalEdge free trial →
        </Link>
      </article>
    </div>
  );
}
