'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, Sparkles, FileText, Bot, BarChart3, Globe, RefreshCw, Shield, Film } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';

export default function GeoPage() {
  const { getToken, isSignedIn } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [termsAccepted, setTermsAccepted] = useState(false);

  const handleGeoCheckout = async () => {
    if (!termsAccepted) {
      setError('Please agree to the Terms of Service before continuing.');
      return;
    }
    if (!isSignedIn) {
      window.location.href = '/sign-up';
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ checkout_url: string }>('/api/billing/addon-checkout', {
        method: 'POST',
        body: JSON.stringify({ plan: 'geo' }),
        token: token || undefined,
      });
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-blue-400">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            RivalEdge
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">Pricing</Link>
            <Link href="/sign-in" className="text-slate-400 hover:text-white text-sm transition-colors">Sign in</Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 bg-purple-600/20 border border-purple-500/30 text-purple-300 text-sm px-4 py-1.5 rounded-full mb-6">
          <Sparkles className="w-4 h-4" />
          Generative Engine Optimization
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
          Get found when buyers ask
          <br />
          <span className="text-purple-400">AI about your category.</span>
        </h1>
        <p className="text-xl text-slate-400 mb-6 max-w-2xl mx-auto">
          Over 40% of B2B discovery now starts with ChatGPT, Claude, Perplexity, and Google AI — 
          not traditional search. If you&apos;re not cited when buyers ask, you&apos;re invisible.
        </p>
        <p className="text-slate-500 text-sm mb-4">Standalone service — no CI subscription required.</p>

        {error && (
          <div className="max-w-lg mx-auto mb-4 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}
      </section>

      {/* Pricing Card */}
      <section className="max-w-xl mx-auto px-6 pb-16">
        <div className="bg-purple-600/5 border border-purple-500/30 rounded-2xl p-8 md:p-10">
          {/* Setup Fee */}
          <div className="mb-8 pb-8 border-b border-purple-500/20">
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-4xl font-bold">$799</span>
              <span className="text-slate-400 text-sm">one-time</span>
            </div>
            <p className="text-slate-300 text-sm mb-4">Setup &amp; full visibility audit</p>
            <ul className="space-y-2">
              {[
                'AI search visibility audit across 5 platforms',
                'Competitor AI mention benchmarking',
                'llms.txt + robots.txt generation & optimization',
                'Content audit & gap analysis',
                'Distribution strategy (GitHub, social, video)',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
          </div>

          {/* Monthly */}
          <div className="mb-8">
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-4xl font-bold">$299</span>
              <span className="text-slate-400 text-sm">/month</span>
            </div>
            <p className="text-slate-300 text-sm mb-4">Ongoing monitoring &amp; optimization</p>
            <ul className="space-y-2">
              {[
                'Monthly AI citation monitoring report',
                'Sentiment & narrative analysis',
                'Competitor AI visibility tracking',
                'Content optimization & structured data',
                'Priority index refresh requests',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
          </div>

          {/* First billing explanation */}
          <div className="mb-5 bg-slate-900/80 border border-purple-500/20 rounded-lg p-4">
            <p className="text-sm text-slate-200 mb-2 font-semibold">📋 Your first billing</p>
            <p className="text-sm text-slate-300 leading-relaxed">
              The <span className="text-white font-semibold">$799 setup fee</span> covers your full AI visibility audit, 
              competitor benchmarking, and crawler infrastructure build-out — everything listed above. 
              It&apos;s a one-time charge added to your first invoice alongside the monthly subscription.
            </p>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">$1,098</span>
              <span className="text-slate-400 text-sm">first month</span>
              <span className="text-slate-500 text-xs">($799 setup + $299/mo)</span>
            </div>
            <p className="text-slate-500 text-xs mt-1">Then $299/month. Cancel anytime.</p>
          </div>

          <label className="flex items-start gap-3 text-left text-sm text-slate-300 mb-5">
            <input
              type="checkbox"
              checked={termsAccepted}
              onChange={(event) => setTermsAccepted(event.target.checked)}
              className="mt-1 h-4 w-4 rounded border-slate-600 bg-slate-900 text-purple-600 focus:ring-purple-500"
            />
            <span>
              I agree to the{' '}
              <Link href="/terms" className="text-purple-300 hover:text-purple-200 underline underline-offset-2">
                Terms of Service
              </Link>
              {' '}and{' '}
              <Link href="/privacy" className="text-purple-300 hover:text-purple-200 underline underline-offset-2">
                Privacy Policy
              </Link>
              .
            </span>
          </label>

          <button
            onClick={handleGeoCheckout}
            disabled={loading || !termsAccepted}
            className="w-full bg-purple-600 hover:bg-purple-500 text-white py-4 rounded-xl font-semibold text-lg transition-colors disabled:opacity-50 shadow-lg shadow-purple-600/20"
          >
            {loading ? 'Redirecting to checkout...' : 'Get found by AI search →'}
          </button>
          <p className="text-slate-500 text-xs text-center mt-4">Secure checkout via Stripe. Cancel anytime.</p>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { icon: Bot, title: '1. Audit', desc: 'We query ChatGPT, Claude, Perplexity, Google AI, and Bing Copilot to map your current visibility — and your competitors\'.' },
            { icon: FileText, title: '2. Build', desc: 'We generate optimized llms.txt, robots.txt, structured content, and distribution assets that AI models use for citation.' },
            { icon: RefreshCw, title: '3. Monitor', desc: 'Monthly tracking: which AIs cite you vs competitors, sentiment shifts, trending narratives in your category.' },
            { icon: BarChart3, title: '4. Adapt', desc: 'We tell you exactly what content to publish next — and where — to close visibility gaps and maintain presence.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="w-10 h-10 bg-purple-600/10 rounded-lg flex items-center justify-center mb-4">
                <Icon className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-semibold mb-2">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* What's Included — Detailed */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-12">Everything included</h2>
        <div className="grid md:grid-cols-2 gap-5">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <Globe className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">AI Crawler Infrastructure</h3>
            </div>
            <p className="text-slate-400 text-sm">
              robots.txt + llms.txt configured for 8 platforms — ChatGPT, Claude, Perplexity, Google AI, Meta, Amazon, Apple, and Anthropic.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <Bot className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">5-Platform Visibility Audit</h3>
            </div>
            <p className="text-slate-400 text-sm">
              ChatGPT, Claude, Perplexity, Google AI Overviews, and Bing Copilot — benchmarked against your top 3 competitors.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Competitor AI Visibility Analysis</h3>
            </div>
            <p className="text-slate-400 text-sm">
              We identify exactly why competitors get recommended instead of you — and build the asset gap to close the distance.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <FileText className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Content & Structured Data Strategy</h3>
            </div>
            <p className="text-slate-400 text-sm">
              We map high-intent AI queries to content assets — comparison pages, FAQs, entity descriptions — that drive AI citations.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <Film className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Distribution Blueprint</h3>
            </div>
            <p className="text-slate-400 text-sm">
              GitHub repos, YouTube demos, LinkedIn activity, Reddit presence — the authority signals AI models use for weighting.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <RefreshCw className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Monthly Monitoring Report</h3>
            </div>
            <p className="text-slate-400 text-sm">
              AI citation changes, sentiment shifts, competitor movement, trending narratives — with specific content recommendations.
            </p>
          </div>
        </div>
      </section>

      {/* Risk Reversal */}
      <section className="max-w-3xl mx-auto px-6 pb-20 text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8">
          <Shield className="w-8 h-8 text-purple-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No overpromises. Just structured execution.</h3>
          <p className="text-slate-400 text-sm max-w-lg mx-auto">
            AI recommendations are probabilistic — we don&apos;t claim to control them. What we do: systematically 
            increase your representation across every signal AI models use for citation, then monitor 
            and adapt as models evolve. If you have zero AI mentions today, we&apos;ll tell you — 
            and show you exactly what to build first.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-xl mx-auto px-6 pb-20 text-center">
        <button
          onClick={handleGeoCheckout}
          disabled={loading || !termsAccepted}
          className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-10 py-4 rounded-xl font-semibold text-lg transition-colors disabled:opacity-50 shadow-lg shadow-purple-600/20"
        >
          {loading ? 'Redirecting...' : 'Get found by AI search →'}
        </button>
        <p className="text-slate-500 text-sm mt-3">$799 one-time setup + $299/month monitoring</p>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-slate-500 text-sm">© 2026 RivalEdge · Aether Holding LLC</span>
          <div className="flex gap-4">
            <Link href="/privacy" className="text-slate-500 text-sm hover:text-slate-300">Privacy Policy</Link>
            <Link href="/terms" className="text-slate-500 text-sm hover:text-slate-300">Terms of Service</Link>
            <Link href="/pricing" className="text-slate-500 text-sm hover:text-slate-300">Pricing</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
