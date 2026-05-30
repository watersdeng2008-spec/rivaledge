'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, Sparkles } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import posthog from 'posthog-js';
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
        text: 'Yes. RivalEdge Solo and Pro offer a 14-day free trial with no credit card required. GEO Self-Service and Enterprise do not include a trial.',
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
      name: 'What is GEO Self-Service?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'GEO Self-Service costs $299 per month and includes Pro-level CI plus self-service AI visibility tools: llms.txt generator, robots.txt for 8 AI crawlers, monthly AI visibility scorecard, and competitor GEO comparison.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is GEO Managed?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'GEO Managed is our done-for-you service at $999 per month. We create and deploy llms.txt, robots.txt, schema markup, and sitemap optimization for you. Includes monthly GEO audits, score tracking, content intelligence briefs, and a 30-minute strategy call.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is the AI Competitive Intelligence Partner tier?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Our AI Competitive Intelligence Partner tier is custom pricing starting at $2,500 per month. It includes everything in GEO Managed plus full competitive intelligence (pricing changes, product launches, messaging shifts), AI recommendation share tracking, monthly strategic reports, category intelligence, and priority Slack support with quarterly business reviews.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is the difference between SEO and GEO?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'SEO optimizes for Google search rankings. GEO (Generative Engine Optimization) optimizes for AI model citations — when ChatGPT, Claude, or Perplexity recommend brands in response to user questions. Different signals, different strategies.',
      },
    },
  ],
};

export default function PricingPage() {
  const { getToken, isSignedIn } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async (plan: 'solo' | 'pro' | 'geo_selfservice') => {
    if (!isSignedIn) {
      window.location.href = '/sign-up';
      return;
    }
    setLoading(plan);
    setError(null);
    posthog.capture('checkout_started', {
      plan,
      plan_name: plan === 'solo' ? 'Solo' : plan === 'pro' ? 'Pro' : 'GEO Self-Service',
      price: plan === 'solo' ? 49 : plan === 'pro' ? 99 : 299,
      source: document.referrer || 'direct',
    });

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

  const handleAddonCheckout = async (plan: 'geo' | 'geo_managed') => {
    if (!isSignedIn) {
      window.location.href = '/sign-up';
      return;
    }
    setLoading(plan);
    setError(null);
    posthog.capture('checkout_started', {
      plan,
      plan_name: plan === 'geo' ? 'GEO Add-on' : 'GEO Managed',
      price: plan === 'geo' ? 299 : 999,
      source: document.referrer || 'direct',
    });

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

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-12">
        <h1 className="text-4xl font-bold text-center mb-4">Simple, honest pricing</h1>
        <p className="text-slate-400 text-center mb-2">No hidden fees. No enterprise quotes. Cancel anytime.</p>
        <p className="text-blue-400 text-center font-medium mb-16">✨ 14-day free trial on Solo & Pro — no credit card required</p>

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

        {/* CI + GEO Tiers */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
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

          {/* GEO Self-Service */}
          <div className="bg-purple-600/5 border border-purple-500/30 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              AI VISIBILITY
            </div>
            <h3 className="text-xl font-semibold mb-1">GEO Self-Service</h3>
            <p className="text-slate-400 text-sm mb-6">AI visibility tools + Pro-level CI</p>
            <div className="text-4xl font-bold mb-8">
              $299<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['10 competitors tracked', true],
                ['Daily AI digest + email alerts', true],
                ['llms.txt auto-generator', true],
                ['robots.txt for 8 AI crawlers', true],
                ['Monthly AI visibility scorecard', true],
                ['Competitor GEO comparison', true],
                ['API access', true],
              ].map(([feature, included]) => (
                <div key={String(feature)} className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 flex-shrink-0 ${included ? 'text-purple-400' : 'text-slate-700'}`} />
                  <span className={included ? 'text-slate-300' : 'text-slate-600'}>{String(feature)}</span>
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

          {/* GEO Managed */}
          <div className="bg-emerald-600/5 border border-emerald-500/30 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-emerald-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              DONE-FOR-YOU
            </div>
            <h3 className="text-xl font-semibold mb-1">GEO Managed</h3>
            <p className="text-slate-400 text-sm mb-6">We deploy GEO assets + monitor monthly</p>
            <div className="text-4xl font-bold mb-8">
              $999<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['Everything in Self-Service', true],
                ['We create & deploy llms.txt', true],
                ['We create & deploy robots.txt', true],
                ['Schema markup implementation', true],
                ['Sitemap optimization', true],
                ['Monthly GEO audit + score tracking', true],
                ['Monthly 30-min strategy call', true],
                ['Content intelligence briefs', true],
                ['5 competitor GEO tracking', true],
              ].map(([feature, included]) => (
                <div key={String(feature)} className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 flex-shrink-0 ${included ? 'text-emerald-400' : 'text-slate-700'}`} />
                  <span className={included ? 'text-slate-300' : 'text-slate-600'}>{String(feature)}</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => handleAddonCheckout('geo_managed')}
              disabled={loading === 'geo_managed'}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading === 'geo_managed' ? 'Redirecting...' : 'Get GEO Managed'}
            </button>
          </div>
        </div>
      </section>

      {/* GEO Section */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <div className="text-center mb-4">
          <span className="bg-purple-600/20 text-purple-400 text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide">
            White-Glove Service
          </span>
        </div>
        <h2 className="text-3xl font-bold text-center mb-3">
          Get cited by ChatGPT, Claude, Perplexity & Google AI
        </h2>
        <p className="text-slate-400 text-center max-w-2xl mx-auto mb-10">
          Over 40% of B2B discovery now happens through AI platforms — not Google SERPs.
          If AI models don&apos;t know you exist, you&apos;re losing deals before buyers even hit search.
        </p>

        <div className="bg-amber-600/10 border border-amber-500/50 rounded-xl p-8 md:p-10 max-w-3xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-6 h-6 text-amber-400" />
            <h3 className="text-2xl font-semibold">AI Competitive Intelligence Partner</h3>
          </div>
          <p className="text-slate-400 mb-6">Full intelligence + strategy + execution. Custom pricing.</p>

          <div className="flex items-baseline gap-3 mb-6">
            <span className="text-4xl font-bold">Custom</span>
            <span className="text-slate-400">starting at $2,500/mo</span>
          </div>

          <div className="grid md:grid-cols-2 gap-3 mb-8">
            {[
              'Everything in GEO Managed',
              'Full competitive intelligence (CI + GEO)',
              'Competitor pricing + launch monitoring',
              'AI recommendation share tracking',
              'Monthly "State of Your Market" report',
              'Positioning analysis + recommendations',
              'Category intelligence + trends',
              'Priority Slack support',
              'Monthly 60-min strategy call',
              'Quarterly business reviews',
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-2 text-sm">
                <Check className="w-4 h-4 flex-shrink-0 text-amber-400" />
                <span className="text-slate-300">{feature}</span>
              </div>
            ))}
          </div>

          <button
            onClick={() => window.location.href = '/contact?tier=intelligence'}
            className="w-full bg-amber-600 hover:bg-amber-500 text-white py-3 rounded-lg font-semibold transition-colors"
          >
            Contact for Custom Pricing
          </button>
        </div>
      </section>

      {/* Feature comparison */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-2xl font-bold text-center mb-8">Compare all plans</h2>
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-6 py-4 text-slate-400 font-medium">Feature</th>
                <th className="text-center px-6 py-4 text-slate-400 font-medium">Solo</th>
                <th className="text-center px-6 py-4 text-slate-400 font-medium">Pro</th>
                <th className="text-center px-6 py-4 text-purple-400 font-medium">GEO Self-Service</th>
                <th className="text-center px-6 py-4 text-emerald-400 font-medium">GEO Managed</th>
                <th className="text-center px-6 py-4 text-amber-400 font-medium">Intelligence Partner</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Competitor tracking', '3', '10', '10', '10', '20'],
                ['AI briefing frequency', 'Weekly', 'Daily', 'Daily', 'Daily', 'Daily + custom'],
                ['Email alerts', '✓', '✓', '✓', '✓', '✓'],
                ['Slack alerts', '—', '—', '—', '—', '✓'],
                ['Battle cards', '✓', '✓', '✓', '✓', '✓'],
                ['API access', '—', '✓', '✓', '✓', '✓'],
                ['Priority support', '—', '✓', '✓', '✓', '✓'],
                ['GEO tools', '—', '—', '✓', '✓', '✓'],
                ['llms.txt generator', '—', '—', '✓', '✓', '✓'],
                ['AI citation audit', '—', '—', 'Automated', 'Automated', 'Full-service'],
                ['GEO asset deployment', '—', '—', '—', '✓', '✓'],
                ['Monthly strategy call', '—', '—', '—', '30 min', '60 min'],
                ['Content intelligence', '—', '—', '—', '✓', '✓'],
                ['Competitor CI monitoring', '—', '—', '—', '—', '✓'],
                ['Category intelligence', '—', '—', '—', '—', '✓'],
                ['Account manager', '—', '—', '—', '—', '✓'],
              ].map(([feature, solo, pro, geo, managed, partner]) => (
                <tr key={feature} className="border-b border-slate-800/50 last:border-0">
                  <td className="px-6 py-3 text-slate-300">{feature}</td>
                  <td className="px-6 py-3 text-center text-slate-400">{solo}</td>
                  <td className="px-6 py-3 text-center text-blue-400 font-medium">{pro}</td>
                  <td className="px-6 py-3 text-center text-purple-400 font-medium">{geo}</td>
                  <td className="px-6 py-3 text-center text-emerald-400 font-medium">{managed}</td>
                  <td className="px-6 py-3 text-center text-amber-400 font-medium">{partner}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-3xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-2xl font-bold text-center mb-8">Frequently asked questions</h2>
        <div className="space-y-6">
          {[
            {
              q: 'What is the difference between SEO and GEO?',
              a: 'SEO optimizes for Google search rankings. GEO (Generative Engine Optimization) optimizes for AI model citations — when ChatGPT, Claude, or Perplexity recommend brands in response to user questions. Different signals, different strategies.',
            },
            {
              q: 'How long until we see results?',
              a: 'Technical fixes (llms.txt, robots.txt, schema) show impact in 2-4 weeks. Content and authority signals take 60-90 days. We track monthly so you can see progress.',
            },
            {
              q: 'Do we need to change our website platform?',
              a: 'No. Our fixes work on any platform — Next.js, WordPress, Webflow, custom. We provide copy-paste code snippets.',
            },
            {
              q: "What's the difference between GEO Managed and Self-Service?",
              a: 'GEO Self-Service ($299/mo) gives you tools to generate llms.txt, robots.txt, and track AI visibility yourself. GEO Managed ($999/mo) means we create and deploy all GEO assets for you, monitor monthly, and provide strategy calls. You get the same results without doing the work.',
            },
            {
              q: "What's the setup fee for?",
              a: 'The one-time setup fee covers: comprehensive AI visibility audit, competitor benchmarking, llms.txt creation, robots.txt optimization, schema markup implementation, and initial content strategy. This is included in GEO Managed and Intelligence Partner tiers.',
            },
            {
              q: 'Can we start with Self-Service and upgrade to Managed or Intelligence Partner?',
              a: 'Yes. Self-Service credits apply toward Managed or Intelligence Partner setup.',
            },
          ].map(({ q, a }) => (
            <div key={q}>
              <h3 className="font-semibold text-white mb-2">{q}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{a}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
