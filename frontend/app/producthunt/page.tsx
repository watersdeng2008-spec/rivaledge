import Link from 'next/link';
import { Check, ArrowRight, Sparkles, BarChart3, Zap, Shield } from 'lucide-react';

export const metadata = {
  title: 'RivalEdge — Product Hunt Exclusive Offer',
  description: 'Special offer for Product Hunt community. 25% off AI-powered competitive intelligence.',
  robots: { index: false, follow: false },
};

export default function ProductHuntPage() {
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
            <span className="bg-purple-600/20 text-purple-400 text-xs px-3 py-1 rounded-full border border-purple-600/30">
              🚀 Product Hunt Exclusive
            </span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-16 pb-12 text-center">
        <div className="inline-flex items-center gap-2 bg-purple-600/10 border border-purple-600/20 text-purple-400 px-4 py-2 rounded-full mb-6">
          <Sparkles className="w-4 h-4" />
          Welcome Product Hunt community!
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold mb-6">
          Win visibility in your market
          <br />
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">and in AI.</span>
        </h1>
        
        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">
          AI-powered competitive intelligence that monitors competitors 24/7 and delivers weekly AI-generated briefings.
        </p>

        {/* PH Offer */}
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-2xl p-6 max-w-xl mx-auto mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="text-2xl">🎉</span>
            <span className="text-lg font-bold text-purple-300">Product Hunt Exclusive</span>
          </div>
          <div className="text-3xl font-bold mb-2">
            25% OFF
          </div>
          <p className="text-slate-300 mb-4">
            Your first 3 months. Use code <code className="bg-purple-600/30 px-2 py-1 rounded text-purple-300 font-mono">PHUNT25</code>
          </p>
          <div className="text-sm text-slate-400">
            Solo: <span className="line-through">$49</span> <span className="text-green-400 font-bold">$36.75/mo</span>
            <span className="mx-2">•</span>
            Pro: <span className="line-through">$99</span> <span className="text-green-400 font-bold">$74.25/mo</span>
          </div>
        </div>

        <Link 
          href="/sign-up"
          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
        >
          Start 14-day free trial
          <ArrowRight className="w-5 h-5" />
        </Link>
        
        <p className="text-slate-500 text-sm mt-4">No credit card required</p>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">What you get</h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="w-12 h-12 bg-blue-600/10 rounded-xl flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-bold mb-2">Competitor Monitoring</h3>
            <p className="text-slate-400">
              Track pricing, features, messaging, hiring, and news across all your competitors automatically.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="w-12 h-12 bg-purple-600/10 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold mb-2">AI Weekly Briefings</h3>
            <p className="text-slate-400">
              Get AI-generated weekly reports with insights, trends, and recommended actions.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="w-12 h-12 bg-green-600/10 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-xl font-bold mb-2">GEO Monitoring</h3>
            <p className="text-slate-400">
              Track your AI search visibility across ChatGPT, Claude, Perplexity, and more.
            </p>
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why teams choose RivalEdge</h2>
        
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-4 px-6">Feature</th>
                <th className="text-left py-4 px-6 text-blue-400">RivalEdge</th>
                <th className="text-left py-4 px-6 text-slate-400">Enterprise CI</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              <tr className="border-b border-slate-800">
                <td className="py-4 px-6">Price</td>
                <td className="py-4 px-6 text-blue-400 font-bold">$49/mo</td>
                <td className="py-4 px-6">$20,000+/yr</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-4 px-6">Setup time</td>
                <td className="py-4 px-6 text-blue-400 font-bold">5 minutes</td>
                <td className="py-4 px-6">2-3 months</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-4 px-6">AI-generated reports</td>
                <td className="py-4 px-6"><Check className="w-5 h-5 text-green-400" /></td>
                <td className="py-4 px-6"><span className="text-slate-500">❌</span></td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-4 px-6">Battle cards</td>
                <td className="py-4 px-6"><Check className="w-5 h-5 text-green-400" /></td>
                <td className="py-4 px-6"><span className="text-slate-500">Manual only</span></td>
              </tr>
              <tr>
                <td className="py-4 px-6">GEO monitoring</td>
                <td className="py-4 px-6"><Check className="w-5 h-5 text-green-400" /></td>
                <td className="py-4 px-6"><span className="text-slate-500">❌</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-4xl mx-auto px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-6">Ready to outsmart your competition?</h2>
        <p className="text-xl text-slate-400 mb-8">
          Join 100+ teams using RivalEdge to stay ahead.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link 
            href="/sign-up"
            className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
          >
            Start free trial
            <ArrowRight className="w-5 h-5" />
          </Link>
          
          <Link 
            href="/demo"
            className="inline-flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
          >
            See demo
          </Link>
        </div>
        
        <p className="text-slate-500 text-sm mt-6">
          14-day free trial • No credit card • Cancel anytime
        </p>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img src="/logo.jpg" alt="RivalEdge" className="h-6 w-6 rounded-sm" />
            <span className="text-slate-400">RivalEdge.ai</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <Link href="/" className="hover:text-white transition-colors">Home</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="/blog" className="hover:text-white transition-colors">Blog</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
