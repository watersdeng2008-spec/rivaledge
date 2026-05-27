import Link from 'next/link';
import { ArrowLeft, Calendar, Clock, Check, X } from 'lucide-react';

export const metadata = {
  title: 'RivalEdge vs Crayon: A Side-by-Side Comparison — RivalEdge',
  description: 'Why pay $20K+/year when you can get 80% of the value for $49/month? A detailed comparison of features, pricing, and setup time.',
};

export default function ComparisonPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
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
          <span className="flex items-center gap-1 text-slate-500 text-sm"><Clock className="w-3.5 h-3.5" />5 min read</span>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold mb-6">RivalEdge vs Crayon: A Side-by-Side Comparison</h1>
        <p className="text-sm text-slate-500 mb-6">
          By{' '}
          <Link href="/blog/authors/waters-deng" className="text-slate-300 hover:text-white underline underline-offset-2">
            Waters Deng
          </Link>
          , Founder of RivalEdge.ai
        </p>
        <p className="text-lg text-slate-400 mb-8">Why pay $20K+/year when you can get 80% of the value for $49/month?</p>

        {/* At a Glance */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">At a Glance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 pr-4">Feature</th>
                  <th className="text-left py-3 pr-4 text-blue-400">RivalEdge</th>
                  <th className="text-left py-3">Crayon</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Starting Price</td><td className="py-3 pr-4">$49/month</td><td className="py-3">$20,000+/year</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Setup Time</td><td className="py-3 pr-4">5 minutes</td><td className="py-3">2-3 months</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">Free Trial</td><td className="py-3 pr-4">14 days, no CC</td><td className="py-3">Demo only</td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">AI-Generated Reports</td><td className="py-3 pr-4"><Check className="w-4 h-4 text-green-400" /></td><td className="py-3"><X className="w-4 h-4 text-red-400" /></td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">GEO Monitoring</td><td className="py-3 pr-4"><Check className="w-4 h-4 text-green-400" /></td><td className="py-3"><X className="w-4 h-4 text-red-400" /></td></tr>
                <tr className="border-b border-slate-800"><td className="py-3 pr-4 font-medium text-white">API Access</td><td className="py-3 pr-4">Pro plan</td><td className="py-3">Enterprise only</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Pricing */}
        <h2 className="text-2xl font-bold mb-4">Pricing</h2>
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <div className="bg-blue-600/10 border border-blue-600/20 rounded-xl p-5">
            <h3 className="font-bold text-blue-400 mb-2">RivalEdge</h3>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>Solo: $49/month</li>
              <li>Pro: $99/month</li>
              <li>GEO Add-on: $799 setup + $299/month</li>
            </ul>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-bold text-slate-400 mb-2">Crayon</h3>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>Starting: $20,000/year</li>
              <li>Enterprise: $30,000-$50,000+/year</li>
              <li>No self-serve signup</li>
            </ul>
          </div>
        </div>
        <p className="text-lg font-medium text-blue-400 mb-8">RivalEdge is 40x cheaper than Crayon.</p>

        {/* Setup */}
        <h2 className="text-2xl font-bold mb-4">Setup & Onboarding</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-bold text-blue-400 mb-2">RivalEdge — 5 Minutes</h3>
            <ol className="text-sm text-slate-300 list-decimal list-inside space-y-1">
              <li>Create account</li>
              <li>Add competitor URLs</li>
              <li>Start monitoring immediately</li>
            </ol>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-bold text-slate-400 mb-2">Crayon — 2-3 Months</h3>
            <ol className="text-sm text-slate-300 list-decimal list-inside space-y-1">
              <li>Schedule sales demo</li>
              <li>Negotiate contract</li>
              <li>Implementation period</li>
              <li>Training sessions</li>
              <li>Go live</li>
            </ol>
          </div>
        </div>

        {/* Bottom Line */}
        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-3">The Bottom Line</h2>
          <p className="text-slate-300 mb-4">
            Crayon is the enterprise standard. It's powerful, comprehensive, and expensive.
          </p>
          <p className="text-slate-300 mb-4">
            RivalEdge is the modern alternative. It delivers 80% of Crayon's value at 2.5% of the cost, with AI features Crayon doesn't have.
          </p>
          <p className="font-medium text-white">
            If you're a lean team that needs competitive intelligence this week, not next quarter, RivalEdge is the clear choice.
          </p>
        </div>

        <Link href="/sign-up" className="inline-block bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors">
          Start RivalEdge free trial →
        </Link>
      </article>
    </div>
  );
}
