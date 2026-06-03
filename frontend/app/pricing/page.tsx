'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, Info, Sparkles } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import posthog from 'posthog-js';
import { apiRequest } from '@/lib/api';
import DemoVideoEmbed from '../components/DemoVideoEmbed';
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
        text: 'Yes. RivalEdge offers a free trial with no credit card required.',
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
      name: 'What is Done-For-You?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Done-For-You costs $299 per month and includes Pro-level CI plus weekly intelligence reports, AI visibility tracking and comparison, GEO asset deployment, 10 competitors monitored 24/7, and immediate alerts on critical moves.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is Enterprise?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Enterprise is our custom full-service market intelligence tier. It includes Done-For-You delivery plus dedicated account management, custom integrations, and priority support.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is the AI Competitive Intelligence Partner tier?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Our AI Competitive Intelligence Partner tier is custom pricing starting at $2,500 per month. It includes everything in Enterprise plus full competitive intelligence (pricing changes, product launches, messaging shifts), AI recommendation share tracking, monthly strategic reports, category intelligence, and priority Slack support with quarterly business reviews.',
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
      plan_name: plan === 'solo' ? 'Solo' : plan === 'pro' ? 'Pro' : 'Done-For-You',
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
              Start Free Trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-12">
        <h1 className="text-4xl font-bold text-center mb-4">Simple, honest pricing</h1>
        <p className="text-slate-400 text-center mb-2">No hidden fees. Clear plans. Cancel anytime.</p>
        <p className="text-blue-400 text-center font-medium mb-16">✨ Start your free trial — no credit card required</p>

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

        <DemoVideoEmbed
          heading="Not sure? Watch a 60-second demo first 🎬"
          className="mb-16 max-w-3xl"
        />

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
              {loading === 'solo' ? 'Redirecting...' : 'Start Free Trial'}
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
                ['Custom integrations', false],
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
              {loading === 'pro' ? 'Redirecting...' : 'Start Free Trial'}
            </button>
          </div>

          {/* Done-For-You */}
          <div className="bg-blue-600/10 border-2 border-blue-500 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-semibold whitespace-nowrap">
              ⭐ RECOMMENDED
            </div>
            <h3 className="text-xl font-semibold mb-1 mt-2">Done-For-You</h3>
            <p className="text-slate-400 text-sm mb-6">For teams who want intelligence delivered, not tools to manage.</p>
            <div className="text-4xl font-bold mb-8">
              $299<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>
            <p className="text-sm text-blue-300 font-semibold mb-5">We do the work. You get the insights.</p>

            <div className="space-y-3 mb-6">
              {[
                'Everything in Pro, plus:',
                'Weekly intelligence reports',
                'AI visibility tracking & comparison',
                'GEO asset deployment (llms.txt, robots.txt)',
                '10 competitors monitored 24/7',
                'Immediate alerts on critical moves',
                'Email delivery every Monday',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 flex-shrink-0 text-blue-400" />
                  <span className="text-slate-300">{feature}</span>
                  {feature === 'GEO asset deployment (llms.txt, robots.txt)' && (
                    <span title="We generate llms.txt files and optimize robots.txt to help AI search engines discover and recommend your brand." className="inline-flex">
                      <Info className="w-3.5 h-3.5 text-slate-500" />
                    </span>
                  )}
                </div>
              ))}
            </div>
            <p className="mb-4 text-sm text-slate-500">Setup: 24 hours · Cancel anytime</p>
            <div className="mb-4 rounded-lg border border-slate-700 bg-slate-800/70 p-3 text-sm text-slate-300">
              <p className="font-semibold text-white">Optional add-on:</p>
              <p>Custom integrations (Slack, CRM) - $999 one-time</p>
            </div>

            <button
              onClick={() => handleCheckout('geo_selfservice')}
              disabled={loading === 'geo_selfservice'}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading === 'geo_selfservice' ? 'Redirecting...' : 'Start Free Trial'}
            </button>
          </div>

          {/* Enterprise */}
          <div className="bg-emerald-600/5 border border-emerald-500/30 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-emerald-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              CUSTOM
            </div>
            <h3 className="text-xl font-semibold mb-1">Enterprise</h3>
            <p className="text-slate-400 text-sm mb-6">Custom intelligence operations for larger teams.</p>
            <div className="text-4xl font-bold mb-8">
              Custom
            </div>

            <div className="space-y-3 mb-8">
              {[
                ['Everything in Done-For-You', true],
                ['Custom competitor coverage', true],
                ['Full AI visibility scorecards', true],
                ['Done-for-you monitoring and reports', true],
                ['Dedicated account manager', true],
                ['Custom integrations', true],
                ['Priority support', true],
              ].map(([feature, included]) => (
                <div key={String(feature)} className="flex items-center gap-2 text-sm">
                  <Check className={`w-4 h-4 flex-shrink-0 ${included ? 'text-emerald-400' : 'text-slate-700'}`} />
                  <span className={included ? 'text-slate-300' : 'text-slate-600'}>{String(feature)}</span>
                </div>
              ))}
            </div>

            <a
              href="mailto:ben.d@rivaledge.ai?subject=Enterprise%20Inquiry"
              className="block w-full bg-emerald-600 hover:bg-emerald-500 text-white py-3 rounded-lg font-semibold transition-colors text-center"
            >
              Contact Sales
            </a>
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
              'Everything in Enterprise',
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

          <a
            href="mailto:ben.d@rivaledge.ai?subject=Sales%20Inquiry"
            className="block w-full text-center bg-amber-600 hover:bg-amber-500 text-white py-3 rounded-lg font-semibold transition-colors"
          >
            Contact for Custom Pricing
          </a>
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
                <th className="text-center px-6 py-4 text-blue-400 font-medium">Done-For-You</th>
                <th className="text-center px-6 py-4 text-emerald-400 font-medium">Enterprise</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Competitors tracked', '3', '10', '10', 'Custom'],
                ['Monitoring', 'Self', 'Self', 'Done for you', 'Done for you'],
                ['Weekly reports', '-', '-', 'Yes', 'Yes'],
                ['AI visibility tracking', 'Basic', 'Advanced', 'Full', 'Full'],
                ['GEO asset deployment', '-', '-', 'Yes', 'Yes'],
                ['Email alerts', 'Weekly', 'Daily', 'Immediate', 'Immediate'],
                ['API access', '-', 'Yes', 'Yes', 'Yes'],
                ['Custom integrations', '-', '-', '$999', 'Yes'],
                ['Account manager', '-', '-', '-', 'Yes'],
              ].map(([feature, solo, pro, dfy, enterprise]) => (
                <tr key={feature} className="border-b border-slate-800/50 last:border-0">
                  <td className="px-6 py-3 text-slate-300">{feature}</td>
                  <td className="px-6 py-3 text-center text-slate-400">{solo}</td>
                  <td className="px-6 py-3 text-center text-blue-400 font-medium">{pro}</td>
                  <td className="px-6 py-3 text-center text-blue-300 font-semibold">{dfy}</td>
                  <td className="px-6 py-3 text-center text-emerald-400 font-medium">{enterprise}</td>
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
              q: "What's the difference between Pro and Done-For-You?",
              a: 'Pro gives you tools to track competitors yourself. Done-For-You ($299/mo) means we monitor competitors, track AI visibility, deploy GEO assets, and send weekly intelligence reports for you.',
            },
            {
              q: 'Can you connect alerts to Slack or our CRM?',
              a: 'Yes. Custom integrations are available as an optional $999 one-time add-on for Done-For-You and are included in Enterprise.',
            },
            {
              q: 'Can we start with Pro and upgrade to Done-For-You or Enterprise?',
              a: 'Yes. You can upgrade whenever you want more of the research and reporting handled for you.',
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
