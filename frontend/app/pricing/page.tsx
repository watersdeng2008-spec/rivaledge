'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';

export default function PricingPage() {
  const { getToken, isSignedIn } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async (plan: 'solo' | 'pro') => {
    if (!isSignedIn) {
      window.location.href = '/sign-up';
      return;
    }
    setLoading(plan);
    setError(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ checkout_url: string }>('/api/billing/checkout', {
        method: 'POST',
        body: JSON.stringify({ plan }),
        token: token || undefined,
      });
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Checkout failed');
    } finally {
      setLoading(null);
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
            <Link href="/sign-in" className="text-slate-400 hover:text-white text-sm transition-colors">Sign in</Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-6 py-20">
        <h1 className="text-4xl font-bold text-center mb-4">Simple, honest pricing</h1>
        <p className="text-slate-400 text-center mb-2">No hidden fees. No enterprise quotes. Cancel anytime.</p>
        <p className="text-blue-400 text-center font-medium mb-16">✨ 14-day free trial — no credit card required</p>

        {error && (
          <div className="max-w-lg mx-auto mb-8 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {/* Solo */}
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-8">
            <h3 className="text-xl font-semibold mb-1">Solo</h3>
            <p className="text-slate-400 text-sm mb-6">For indie founders and small teams</p>
            <div className="text-4xl font-bold mb-8">
              $49<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['5 competitors', true],
                ['Weekly AI digest', true],
                ['Email alerts', true],
                ['Battle card generator', true],
                ['Daily AI digest', false],
                ['Slack alerts', false],
                ['API access', false],
              ].map(([feature, included]) => (
                <div key={String(feature)} className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 flex-shrink-0 ${included ? 'text-blue-400' : 'text-slate-700'}`} />
                  <span className={included ? 'text-slate-300' : 'text-slate-600'}>{String(feature)}</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => handleCheckout('solo')}
              disabled={loading === 'solo'}
              className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading === 'solo' ? 'Redirecting...' : 'Start 14-day free trial'}
            </button>
          </div>

          {/* Pro */}
          <div className="bg-blue-600/10 border border-blue-500/50 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              MOST POPULAR
            </div>
            <h3 className="text-xl font-semibold mb-1">Pro</h3>
            <p className="text-slate-400 text-sm mb-6">For growing teams and agencies</p>
            <div className="text-4xl font-bold mb-8">
              $99<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['20 competitors', true],
                ['Daily AI digest', true],
                ['Email + Slack alerts', true],
                ['Battle card generator', true],
                ['API access', true],
                ['Priority support', true],
                ['Custom integrations', true],
              ].map(([feature, included]) => (
                <div key={String(feature)} className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 flex-shrink-0 ${included ? 'text-blue-400' : 'text-slate-700'}`} />
                  <span className={included ? 'text-slate-300' : 'text-slate-600'}>{String(feature)}</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => handleCheckout('pro')}
              disabled={loading === 'pro'}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading === 'pro' ? 'Redirecting...' : 'Start 14-day free trial'}
            </button>
          </div>
        </div>

        {/* Feature comparison */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-2xl font-bold text-center mb-8">Everything included</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left px-6 py-4 text-slate-400 font-medium">Feature</th>
                  <th className="text-center px-6 py-4 text-slate-400 font-medium">Solo</th>
                  <th className="text-center px-6 py-4 text-slate-400 font-medium">Pro</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Competitor tracking', '5', '20'],
                  ['AI briefing frequency', 'Weekly', 'Daily'],
                  ['Email alerts', '✓', '✓'],
                  ['Slack alerts', '—', '✓'],
                  ['Battle cards', '✓', '✓'],
                  ['API access', '—', '✓'],
                  ['Priority support', '—', '✓'],
                ].map(([feature, solo, pro]) => (
                  <tr key={feature} className="border-b border-slate-800/50 last:border-0">
                    <td className="px-6 py-3 text-slate-300">{feature}</td>
                    <td className="px-6 py-3 text-center text-slate-400">{solo}</td>
                    <td className="px-6 py-3 text-center text-blue-400 font-medium">{pro}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
