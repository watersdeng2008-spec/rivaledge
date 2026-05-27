'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';
import LeadCaptureForm from '../components/LeadCaptureForm';

const PRICING_FAQ_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'Does RivalEdge have a free trial?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Yes. RivalEdge offers a 14-day free trial with no credit card required.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is included in RivalEdge Solo?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Solo costs $49 per month and includes tracking for up to 3 competitors, weekly AI digests, email alerts, and battle card generation.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is included in RivalEdge Pro?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Pro costs $99 per month and includes tracking for up to 10 competitors, daily AI digests, email and Slack alerts, API access, priority support, and battle card generation.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is Enterprise GEO?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Enterprise GEO is a full-service AI visibility plan at $999 per month plus a $3,500 one-time setup fee. It includes dedicated account management, content optimization, Slack integration, citation monitoring, and competitor GEO analysis.',
      },
    },
  ],
};

export default function PricingPage() {
  const { getToken, isSignedIn } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showGeoDetails, setShowGeoDetails] = useState(false);

  const handleCheckout = async (plan: 'solo' | 'pro' | 'geo_selfservice') => {
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

  const handleAddonCheckout = async (plan: 'geo') => {
    if (!isSignedIn) {
      window.location.href = '/sign-up';
      return;
    }
    setLoading(plan);
    setError(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ checkout_url: string }>('/api/billing/addon-checkout', {
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
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(PRICING_FAQ_SCHEMA) }}
      />
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

        {/* Lead Capture — Free Competitor Snapshot */}
        <div className="max-w-xl mx-auto mb-16">
          <LeadCaptureForm
            source="pricing"
            variant="inline"
            title="Not ready to commit?"
            subtitle="Get a free snapshot of any competitor — see what RivalEdge tracks before you buy"
            buttonText="Get free competitor snapshot"
          />
        </div>

        {error && (
          <div className="max-w-lg mx-auto mb-8 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {/* Solo */}
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-8">
            <h3 className="text-xl font-semibold mb-1">Solo</h3>
            <p className="text-slate-400 text-sm mb-6">For indie founders and small teams</p>
            <div className="text-4xl font-bold mb-8">
              $49<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['3 competitors', true],
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

            <div className="mb-4">
              <Link href="/demo" className="text-blue-400 hover:text-blue-300 text-sm underline underline-offset-2">
                See sample report →
              </Link>
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
                ['10 competitors', true],
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

            <div className="mb-4">
              <Link href="/demo" className="text-blue-400 hover:text-blue-300 text-sm underline underline-offset-2">
                See sample report →
              </Link>
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

        {/* GEO Self-Service */}
        <div className="max-w-5xl mx-auto mt-20">
          <div className="border-t border-slate-800 pt-16">
            <div className="text-center mb-4">
              <span className="bg-purple-600/20 text-purple-400 text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide">
                AI Visibility
              </span>
            </div>
            <h2 className="text-3xl font-bold text-center mb-3">
              Know what competitors are doing.
              <br />
              <span className="text-purple-400">Get found when buyers ask AI about your category.</span>
            </h2>
            <p className="text-slate-400 text-center max-w-2xl mx-auto mb-10">
              Already tracking competitors? Add GEO to ensure ChatGPT, Claude, Perplexity, 
              and Google AI cite <em>your</em> company when buyers search. Over 40% of B2B discovery 
              now happens through AI platforms — not Google SERPs.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* GEO Self-Service */}
            <div className="bg-purple-600/5 border border-purple-500/30 rounded-xl p-8">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xl font-semibold">GEO Self-Service</h3>
              </div>
              <p className="text-slate-400 text-sm mb-4">Self-service AI visibility tools + Pro-level CI reports</p>
              
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-3xl font-bold">$299</span>
                <span className="text-slate-400 text-sm">/mo</span>
              </div>

              <div className="space-y-3 mb-6">
                {[
                  '10 competitors tracked (Pro CI)',
                  'Daily AI digest + email alerts',
                  'llms.txt auto-generator',
                  'robots.txt for 8 AI crawlers',
                  'Monthly AI visibility scorecard',
                  'Competitor GEO comparison',
                  'Quarterly strategy refresh',
                  'API access',
                ].map((feature) => (
                  <div key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 flex-shrink-0 text-purple-400" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleCheckout('geo_selfservice')}
                disabled={loading === 'geo_selfservice'}
                className="w-full bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
              >
                {loading === 'geo_selfservice' ? 'Redirecting...' : 'Get GEO Self-Service'}
              </button>
            </div>

            {/* Enterprise GEO */}
            <div className="bg-purple-600/10 border border-purple-500/50 rounded-xl p-8 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
                WHITE-GLOVE
              </div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xl font-semibold">Enterprise GEO</h3>
              </div>
              <p className="text-slate-400 text-sm mb-4">Full-service GEO with bundled CI + Slack integration</p>
              
              <div className="flex items-baseline gap-2 mb-4">
                <span className="text-3xl font-bold">$999</span>
                <span className="text-slate-400 text-sm">/mo</span>
                <span className="text-slate-500 text-sm group relative cursor-help">
                  + $3,500 one-time setup
                  <span className="inline-block ml-1 text-slate-600 group-hover:text-purple-400 transition-colors">ⓘ</span>
                  <span className="absolute bottom-full left-0 mb-2 w-64 bg-slate-800 border border-slate-600 text-slate-300 text-xs rounded-lg px-3 py-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    Comprehensive AI citation audit, robotstxt configuration for 8 AI crawlers, llmstxt creation, and initial content optimization across ChatGPT, Claude, Perplexity, and Google AI.
                  </span>
                </span>
              </div>

              <button
                onClick={() => setShowGeoDetails(!showGeoDetails)}
                className="text-sm text-purple-400 hover:text-purple-300 underline underline-offset-2 mb-6 block"
              >
                {showGeoDetails ? 'Hide details' : "What's included"}
              </button>

              <div className="space-y-3 mb-6">
                {[
                  '20 competitors tracked (CI bundled)',
                  'Daily + custom AI digests',
                  'Slack integration',
                  'Everything in Self-Service',
                  'Hands-on content optimization',
                  'Dedicated account manager',
                  'Priority support',
                ].map((feature) => (
                  <div key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 flex-shrink-0 text-purple-400" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleAddonCheckout('geo')}
                disabled={loading === 'geo'}
                className="w-full bg-purple-700 hover:bg-purple-600 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
              >
                {loading === 'geo' ? 'Redirecting...' : 'Get Enterprise GEO'}
              </button>
            </div>
          </div>

          {showGeoDetails && (
            <div className="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-8">
              <h4 className="font-semibold mb-4">Enterprise GEO Full Details</h4>
              <div className="grid md:grid-cols-2 gap-3">
                {[
                  'AI search visibility audit',
                  'llms.txt optimization & maintenance',
                  'robots.txt configured for 8 AI crawlers',
                  'Monthly AI citation monitoring report',
                  'Competitor GEO posture analysis',
                  'Content pipeline optimization',
                  'GitHub + YouTube distribution strategy',
                  'Priority index refresh requests',
                ].map((feature) => (
                  <div key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="w-4 h-4 flex-shrink-0 text-purple-400" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Feature comparison */}
        <div className="max-w-4xl mx-auto mt-20">
          <h2 className="text-2xl font-bold text-center mb-8">Everything included</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left px-6 py-4 text-slate-400 font-medium">Feature</th>
                  <th className="text-center px-6 py-4 text-slate-400 font-medium">Solo</th>
                  <th className="text-center px-6 py-4 text-slate-400 font-medium">Pro</th>
                  <th className="text-center px-6 py-4 text-purple-400 font-medium">GEO Self-Service</th>
                  <th className="text-center px-6 py-4 text-purple-400 font-medium">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Competitor tracking', '3', '10', '10', '20'],
                  ['AI briefing frequency', 'Weekly', 'Daily', 'Daily', 'Daily + custom'],
                  ['Email alerts', '✓', '✓', '✓', '✓'],
                  ['Slack alerts', '—', '—', '—', '✓'],
                  ['Battle cards', '✓', '✓', '✓', '✓'],
                  ['API access', '—', '✓', '✓', '✓'],
                  ['Priority support', '—', '✓', '✓', '✓'],
                  ['GEO tools', '—', '—', '✓', '✓'],
                  ['llms.txt generator', '—', '—', '✓', '✓'],
                  ['AI citation audit', '—', '—', 'Automated', 'Full-service'],
                  ['Content optimization', '—', '—', '—', '✓'],
                  ['Account manager', '—', '—', '—', '✓'],
                ].map(([feature, solo, pro, geo, ent]) => (
                  <tr key={feature} className="border-b border-slate-800/50 last:border-0">
                    <td className="px-6 py-3 text-slate-300">{feature}</td>
                    <td className="px-6 py-3 text-center text-slate-400">{solo}</td>
                    <td className="px-6 py-3 text-center text-blue-400 font-medium">{pro}</td>
                    <td className="px-6 py-3 text-center text-purple-400 font-medium">{geo}</td>
                    <td className="px-6 py-3 text-center text-purple-400 font-medium">{ent}</td>
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
