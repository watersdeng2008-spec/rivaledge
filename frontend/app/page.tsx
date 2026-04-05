import Link from 'next/link';
import { Check, Zap, Bell, Shield } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm mr-2 inline-block" />
          <span className="text-xl font-bold text-blue-400">RivalEdge</span>
          <div className="flex items-center gap-4">
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">
              Pricing
            </Link>
            <Link
              href="/sign-in"
              className="text-slate-400 hover:text-white text-sm transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors"
            >
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20 text-center">
        <div className="inline-block bg-blue-600/10 border border-blue-600/20 text-blue-400 text-sm px-3 py-1 rounded-full mb-6">
          AI-powered competitor monitoring
        </div>
        <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
          Finally. Competitive intelligence
          <br />
          <span className="text-blue-400">that doesn&apos;t cost $30k/year.</span>
        </h1>
        <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
          Track your rivals. Get weekly AI briefings. $49/month.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/sign-up"
            className="bg-blue-600 hover:bg-blue-500 text-white text-lg px-8 py-4 rounded-xl font-semibold transition-colors"
          >
            Start free trial →
          </Link>
          <Link
            href="/pricing"
            className="border border-slate-700 hover:border-slate-500 text-slate-300 text-lg px-8 py-4 rounded-xl font-semibold transition-colors"
          >
            See pricing
          </Link>
        </div>
        <p className="text-slate-500 text-sm mt-4">No credit card required. 14-day free trial.</p>
        <div className="mt-12 flex justify-center">
          <img src="/hero.jpg" alt="RivalEdge in action" className="rounded-2xl shadow-2xl max-w-2xl w-full" />
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Automated scraping</h3>
            <p className="text-slate-400 text-sm">
              We monitor your competitors&apos; websites, pricing pages, and product updates automatically — no manual work.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Bell className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Weekly AI briefings</h3>
            <p className="text-slate-400 text-sm">
              Get a concise digest every week summarizing what changed, what matters, and what to do about it.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Battle cards</h3>
            <p className="text-slate-400 text-sm">
              Generate AI-powered battle cards for any competitor — perfect for sales calls and competitive positioning.
            </p>
          </div>
        </div>
      </section>

      {/* Why RivalEdge */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-4">Why RivalEdge?</h2>
        <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
          Competitive intelligence used to be a luxury. We&apos;re making it a standard tool for every team.
        </p>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Left column */}
          <div className="space-y-8">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">$</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Priced for real businesses</h3>
                <p className="text-slate-400 text-sm">
                  Enterprise tools cost $20,000+/year and require months of implementation. 
                  RivalEdge is $49/month and works in 5 minutes. No sales calls, no contracts.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">⚡</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Intelligence that never sleeps</h3>
                <p className="text-slate-400 text-sm">
                  Most tools give you a one-time snapshot. We monitor continuously and deliver 
                  weekly AI briefings so you&apos;re always ahead of the curve, not reacting to it.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">🎯</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Built for action, not analysis</h3>
                <p className="text-slate-400 text-sm">
                  We don&apos;t just track prices. We analyze messaging, feature launches, and positioning 
                  — then tell you exactly how to win. Battle cards included, not extra.
                </p>
              </div>
            </div>
          </div>
          
          {/* Right column */}
          <div className="space-y-8">
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">🚀</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Zero setup, zero maintenance</h3>
                <p className="text-slate-400 text-sm">
                  Add a competitor URL. That&apos;s it. We handle the scraping, analysis, and delivery. 
                  No integrations to configure, no dashboards to check, no data to interpret.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">🔒</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Works everywhere</h3>
                <p className="text-slate-400 text-sm">
                  Track any competitor with a website — SaaS, e-commerce, services, B2B, B2C. 
                  Not limited to Amazon or specific platforms. If they have a web presence, 
                  we can monitor them.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="w-12 h-12 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl font-bold text-blue-400">💡</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">AI that understands context</h3>
                <p className="text-slate-400 text-sm">
                  Our AI doesn&apos;t just detect changes — it interprets significance. 
                  A price drop gets flagged differently than a messaging pivot. 
                  You get insights, not just alerts.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Trust badge */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-full px-4 py-2">
            <span className="text-green-400">●</span>
            <span className="text-slate-300 text-sm">Trusted by 0 teams... so far. Be the first.</span>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-6xl mx-auto px-6 py-16" id="pricing">
        <h2 className="text-3xl font-bold text-center mb-12">Simple, honest pricing</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {/* Solo */}
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-8">
            <h3 className="text-xl font-semibold mb-1">Solo</h3>
            <p className="text-slate-400 text-sm mb-6">For indie founders and small teams</p>
            <div className="text-4xl font-bold mb-6">
              $49<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>
            <ul className="space-y-3 mb-8">
              {['Track up to 5 competitors', 'Weekly AI digest', 'Email alerts', 'Battle card generator'].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href="/sign-up"
              className="block text-center bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Get started
            </Link>
          </div>

          {/* Pro */}
          <div className="bg-blue-600/10 border border-blue-500/50 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              MOST POPULAR
            </div>
            <h3 className="text-xl font-semibold mb-1">Pro</h3>
            <p className="text-slate-400 text-sm mb-6">For growing teams and agencies</p>
            <div className="text-4xl font-bold mb-6">
              $99<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>
            <ul className="space-y-3 mb-8">
              {[
                'Track up to 20 competitors',
                'Daily AI digest',
                'Slack + email alerts',
                'Battle card generator',
                'API access',
                'Priority support',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href="/sign-up"
              className="block text-center bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Get started
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8 mt-16">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-slate-500 text-sm">© 2026 RivalEdge · Aether Holding LLC</span>
          <div className="flex gap-4 mt-2">
            <a href="/privacy" className="text-slate-500 text-sm hover:text-slate-300">Privacy Policy</a>
            <a href="/terms" className="text-slate-500 text-sm hover:text-slate-300">Terms of Service</a>
            <a href="mailto:support@rivaledge.ai" className="text-slate-500 text-sm hover:text-slate-300">Support</a>
          </div>
          <div className="flex gap-6 text-slate-500 text-sm">
            <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="/sign-in" className="hover:text-white transition-colors">Sign in</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
