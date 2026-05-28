'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, Sparkles, FileText, Bot, BarChart3, Globe, RefreshCw, Shield, Film, ArrowRight, Zap } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';

// ── GeoAuditForm (inline component) ─────────────────────────────────────────

function GeoAuditForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    companyName: '',
    companyUrl: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://rivaledge-production.up.railway.app/api/leads/capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          company_name: formData.companyName || null,
          company_url: formData.companyUrl || null,
          competitor_url: null,
          capture_source: 'geo_audit',
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || data.message || 'Something went wrong');
      }

      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 text-center">
        <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check className="w-6 h-6 text-green-400" />
        </div>
        <h3 className="text-lg font-semibold text-green-400 mb-2">Audit request received!</h3>
        <p className="text-slate-300 text-sm">
          We&apos;ll scan your brand across 5 AI platforms and email your report within 24 hours.
        </p>
      </div>
    );
  }

  const inputClasses =
    'w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all text-sm';

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <input
          type="text"
          placeholder="Your name *"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={inputClasses}
        />
        <input
          type="email"
          placeholder="Work email *"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className={inputClasses}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <input
          type="text"
          placeholder="Company name *"
          required
          value={formData.companyName}
          onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
          className={inputClasses}
        />
        <input
          type="url"
          placeholder="Company URL * (https://...)"
          required
          value={formData.companyUrl}
          onChange={(e) => setFormData({ ...formData, companyUrl: e.target.value })}
          className={inputClasses}
        />
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <RefreshCw className="w-4 h-4 animate-spin" />
            Submitting...
          </>
        ) : (
          <>
            Request Free Audit
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>

      <p className="text-slate-500 text-xs text-center">
        We respect your privacy. No spam — just your audit report.
      </p>
    </form>
  );
}

const GEO_FAQ_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'What is Generative Engine Optimization?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Generative Engine Optimization is the practice of improving how often and how accurately a brand appears in AI-generated answers from systems like ChatGPT, Claude, Perplexity, Google AI, and Bing Copilot.',
      },
    },
    {
      '@type': 'Question',
      name: 'What does RivalEdge GEO include?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'RivalEdge GEO includes an AI search visibility audit, competitor mention benchmarking, llms.txt and robots.txt optimization, content and structured data strategy, distribution planning, and monthly citation monitoring.',
      },
    },
    {
      '@type': 'Question',
      name: 'How much does RivalEdge GEO cost?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'RivalEdge Enterprise GEO costs $3,500 for one-time setup and $999 per month for ongoing monitoring and optimization. GEO Self-Service is $299 per month.',
      },
    },
    {
      '@type': 'Question',
      name: 'Which AI platforms does RivalEdge GEO monitor?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'RivalEdge GEO monitors visibility across ChatGPT, Claude, Perplexity, Google AI Overviews, and Bing Copilot.',
      },
    },
    {
      '@type': 'Question',
      name: 'What is the difference between SEO and GEO?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'SEO optimizes for Google search rankings. GEO optimizes for AI model citations — when ChatGPT, Claude, or Perplexity recommend brands in response to user questions. Different signals, different strategies.',
      },
    },
  ],
};

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
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ checkout_url: string }>('/api/billing/addon-checkout', {
        method: 'POST',
        body: JSON.stringify({ plan: 'geo', terms_accepted: true }),
        token: token || undefined,
      });
      if (data.checkout_url && typeof data.checkout_url === 'string' && data.checkout_url.startsWith('https://')) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('Checkout URL not received. Please try again or contact support.');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Checkout failed. Please try again or contact support.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(GEO_FAQ_SCHEMA) }}
      />
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
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-12 text-center">
        <div className="inline-flex items-center gap-2 bg-purple-600/20 border border-purple-500/30 text-purple-300 text-sm px-4 py-1.5 rounded-full mb-6">
          <Sparkles className="w-4 h-4" />
          Generative Engine Optimization
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
          Get cited by AI when buyers ask
          <br />
          <span className="text-purple-400">about your category.</span>
        </h1>
        <p className="text-xl text-slate-400 mb-6 max-w-2xl mx-auto">
          Over 40% of B2B discovery now starts with ChatGPT, Claude, Perplexity, and Google AI — 
          not traditional search. If you&apos;re not cited when buyers ask, you&apos;re invisible.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
          <a 
            href="#audit" 
            className="bg-purple-600 hover:bg-purple-500 text-white px-8 py-3 rounded-lg font-semibold transition-colors inline-flex items-center gap-2"
          >
            Get Free AI Visibility Audit
            <ArrowRight className="w-4 h-4" />
          </a>
          <Link 
            href="/pricing" 
            className="text-slate-400 hover:text-white text-sm transition-colors underline underline-offset-2"
          >
            Compare with CI plans →
          </Link>
        </div>
        <p className="text-slate-500 text-sm">
          Read our breakdown: <a href="https://open.substack.com/pub/dengw/p/geo-is-not-seo-20?r=6qf1gl&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300 underline underline-offset-2">GEO ≠ SEO 2.0</a>
        </p>
      </section>

      {/* Free Audit Lead Capture */}
      <section id="audit" className="max-w-xl mx-auto px-6 pb-16">
        <div className="bg-slate-900 border border-purple-500/30 rounded-xl p-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-white mb-2">Free AI Visibility Audit</h2>
            <p className="text-slate-400 text-sm">
              See how AI platforms see your brand. We&apos;ll scan 5 platforms and send you a score + roadmap.
            </p>
          </div>
          <GeoAuditForm />
        </div>
      </section>

      {/* The Shift Section */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-8">The shift nobody&apos;s talking about</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-slate-400 mb-4">Before</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Buyers Googled &quot;best [category] tools&quot; → clicked your SEO-optimized page → became a lead.
            </p>
          </div>
          <div className="bg-purple-600/5 border border-purple-500/30 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-purple-400 mb-4">Now</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Buyers ask ChatGPT &quot;what&apos;s the best [category] tool?&quot; → AI cites 3-5 brands → buyer never visits Google.
            </p>
          </div>
        </div>
        <p className="text-center text-slate-300 mt-8 max-w-2xl mx-auto">
          <strong className="text-white">If you&apos;re not in those 3-5 citations, you don&apos;t exist in that conversation.</strong>
        </p>
      </section>

      {/* What We Built Section */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <div className="text-center mb-4">
          <span className="bg-purple-600/20 text-purple-400 text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide">
            What We Built
          </span>
        </div>
        <h2 className="text-3xl font-bold text-center mb-3">Institutional-grade GEO infrastructure</h2>
        <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
          We spent months building and battle-testing our own AI visibility platform. Here&apos;s what&apos;s live:
        </p>

        <div className="grid md:grid-cols-2 gap-5 mb-12">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <Zap className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Phase 1: Technical Foundation</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> AI crawler tracking (8+ crawlers)</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> llms.txt — structured brand data</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> robots.txt optimized for AI bots</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> Schema markup (Organization, Product, FAQ)</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> GEO Audit API — 100-point scoring</li>
            </ul>
            <p className="text-purple-400 text-sm mt-3 font-medium">Our score: 100/100 (Grade A)</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold">Phase 2: Intelligence & Execution</h3>
            </div>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> Brand Knowledge Graph</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> 30/60/90-Day Roadmap Generator</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> CI-Powered Content Briefs</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> Monthly citation monitoring (5 platforms)</li>
              <li className="flex items-center gap-2"><Check className="w-3 h-3 text-purple-400" /> Competitor GEO posture tracking</li>
            </ul>
          </div>
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

      {/* Pricing Section */}
      <section id="pricing" className="max-w-5xl mx-auto px-6 py-16 border-t border-slate-800">
        <div className="text-center mb-4">
          <span className="bg-purple-600/20 text-purple-400 text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide">
            Pricing
          </span>
        </div>
        <h2 className="text-3xl font-bold text-center mb-3">Choose your GEO plan</h2>
        <p className="text-slate-400 text-center max-w-2xl mx-auto mb-12">
          Start with Self-Service tools or let us execute everything white-glove.
        </p>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {/* GEO Self-Service */}
          <div className="bg-purple-600/5 border border-purple-500/30 rounded-xl p-8">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-xl font-semibold">GEO Self-Service</h3>
            </div>
            <p className="text-slate-400 text-sm mb-4">Tools + roadmap. You execute.</p>
            
            <div className="flex items-baseline gap-2 mb-6">
              <span className="text-3xl font-bold">$299</span>
              <span className="text-slate-400 text-sm">/mo</span>
            </div>

            <div className="space-y-3 mb-6">
              {[
                'Unlimited GEO audits (100-point scoring)',
                'Brand Knowledge Graph builder',
                '30/60/90-Day Roadmap generator',
                '4 CI-powered content briefs/month',
                'Monthly score tracking dashboard',
                'AI crawler visit logs',
                'Email support',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 flex-shrink-0 text-purple-400" />
                  <span className="text-slate-300">{feature}</span>
                </div>
              ))}
            </div>

            <Link
              href="/pricing"
              className="block w-full text-center bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Get GEO Self-Service
            </Link>
          </div>

          {/* Enterprise GEO */}
          <div className="bg-purple-600/10 border border-purple-500/50 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              WHITE-GLOVE
            </div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-xl font-semibold">Enterprise GEO</h3>
            </div>
            <p className="text-slate-400 text-sm mb-4">We do everything. Full-service.</p>
            
            <div className="flex items-baseline gap-2 mb-6">
              <span className="text-3xl font-bold">$999</span>
              <span className="text-slate-400 text-sm">/mo</span>
              <span className="text-slate-500 text-sm">+ $3,500 setup</span>
            </div>

            <div className="space-y-3 mb-6">
              {[
                'Everything in Self-Service',
                'We execute the full roadmap',
                'Hands-on content optimization',
                'Monthly citation monitoring (5 platforms)',
                '20 competitors tracked (CI bundled)',
                'Slack integration',
                'Dedicated account manager',
                'Priority support (24h response)',
              ].map((feature) => (
                <div key={feature} className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 flex-shrink-0 text-purple-400" />
                  <span className="text-slate-300">{feature}</span>
                </div>
              ))}
            </div>

            <button
              onClick={handleGeoCheckout}
              disabled={loading || !termsAccepted}
              className="w-full bg-purple-700 hover:bg-purple-600 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading ? 'Redirecting...' : 'Get Enterprise GEO'}
            </button>
          </div>
        </div>

        {/* Terms checkbox for Enterprise */}
        <div className="max-w-md mx-auto mt-6">
          <label className="flex items-start gap-3 text-left text-sm text-slate-300">
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
          {error && (
            <div className="mt-3 bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
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
              q: "What's the setup fee for?",
              a: 'The $3,500 Enterprise setup covers: comprehensive AI visibility audit, competitor benchmarking, llms.txt creation, robots.txt optimization, schema markup implementation, and initial content strategy. One-time charge.',
            },
            {
              q: 'Can we start with Self-Service and upgrade to Enterprise?',
              a: 'Yes. Self-Service credits apply toward Enterprise setup fee.',
            },
          ].map(({ q, a }) => (
            <div key={q}>
              <h3 className="font-semibold text-white mb-2">{q}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{a}</p>
            </div>
          ))}
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
