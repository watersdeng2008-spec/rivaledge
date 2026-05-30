import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export const metadata = {
  title: 'RivalEdge vs Klue: AI-Powered CI vs Traditional Battlecards',
  description: 'Compare RivalEdge vs Klue on pricing, AI features, and ease of use. See which competitive intelligence platform fits your team.',
  keywords: ['RivalEdge vs Klue', 'Klue alternative', 'competitive intelligence', 'AI battlecards'],
};

const COMPARISON_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'ComparisonPage',
  name: 'RivalEdge vs Klue Comparison',
  description: 'Detailed comparison of RivalEdge and Klue competitive intelligence platforms',
  url: 'https://www.rivaledge.ai/vs/klue',
  itemCompared: [
    {
      '@type': 'SoftwareApplication',
      name: 'RivalEdge',
      applicationCategory: 'BusinessApplication',
      offers: {
        '@type': 'Offer',
        price: '49',
        priceCurrency: 'USD',
        priceValidUntil: '2026-12-31',
      },
    },
    {
      '@type': 'SoftwareApplication',
      name: 'Klue',
      applicationCategory: 'BusinessApplication',
    },
  ],
};

export default function VsKluePage() {
  const features = [
    { name: 'Starting Price', rivaledge: '$49/mo', klue: 'Custom (enterprise)', winner: 'rivaledge' },
    { name: 'Free Trial', rivaledge: '14 days', klue: 'Demo only', winner: 'rivaledge' },
    { name: 'AI-Generated Insights', rivaledge: '✅ Native', klue: '⚠️ Limited', winner: 'rivaledge' },
    { name: 'GEO Optimization', rivaledge: '✅ Built-in', klue: '❌ None', winner: 'rivaledge' },
    { name: 'Battlecards', rivaledge: '✅ Auto-generated', klue: '✅ Manual + templates', winner: 'rivaledge' },
    { name: 'Price Tracking', rivaledge: '✅ Real-time', klue: '✅ Yes', winner: 'tie' },
    { name: 'Salesforce Integration', rivaledge: '✅ Yes', klue: '✅ Deep native', winner: 'klue' },
    { name: 'Setup Time', rivaledge: '< 5 minutes', klue: '1-2 weeks', winner: 'rivaledge' },
    { name: 'Self-Service', rivaledge: '✅ Full', klue: '❌ Sales-led', winner: 'rivaledge' },
    { name: 'Slack Integration', rivaledge: '✅ Yes', klue: '✅ Yes', winner: 'tie' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(COMPARISON_SCHEMA) }}
      />
      
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

      <div className="max-w-4xl mx-auto px-6 pt-12 pb-20">
        <Link href="/blog" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to blog
        </Link>

        <h1 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
          RivalEdge vs Klue
        </h1>
        <p className="text-lg text-slate-400 mb-8">
          AI-powered competitive intelligence vs traditional battlecard platforms. Which fits your team?
        </p>

        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-6 mb-12">
          <h2 className="text-xl font-bold mb-3">Quick Verdict</h2>
          <p className="text-slate-300 mb-4">
            <strong>Choose RivalEdge if:</strong> You want AI-generated insights, instant setup, and affordable pricing with built-in GEO optimization.
          </p>
          <p className="text-slate-300">
            <strong>Choose Klue if:</strong> You need deep Salesforce integration and have enterprise budget for sales-led onboarding.
          </p>
        </div>

        <div className="overflow-x-auto mb-12">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-4 pr-4 text-slate-400 font-medium">Feature</th>
                <th className="text-center py-4 pr-4 text-blue-400 font-bold">RivalEdge</th>
                <th className="text-center py-4 text-slate-400 font-medium">Klue</th>
              </tr>
            </thead>
            <tbody>
              {features.map((feature, i) => (
                <tr key={i} className="border-b border-slate-800">
                  <td className="py-4 pr-4 font-medium">{feature.name}</td>
                  <td className={`py-4 pr-4 text-center ${feature.winner === 'rivaledge' ? 'text-green-400 font-semibold' : 'text-slate-300'}`}>
                    {feature.rivaledge}
                  </td>
                  <td className={`py-4 text-center ${feature.winner === 'klue' ? 'text-green-400 font-semibold' : 'text-slate-300'}`}>
                    {feature.klue}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-12">
          <section>
            <h2 className="text-2xl font-bold mb-4">Pricing: RivalEdge is Transparent, Klue is Enterprise-Only</h2>
            <p className="text-slate-300 mb-4">
              RivalEdge starts at <strong>$49/month</strong> with clear, self-serve pricing. Klue requires <strong>custom enterprise quotes</strong> with no public pricing.
            </p>
            <p className="text-slate-300">
              For teams that want to get started today without a sales call, RivalEdge is the clear choice.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">AI Battlecards: RivalEdge Generates, Klue Templates</h2>
            <p className="text-slate-300 mb-4">
              RivalEdge uses AI to <strong>auto-generate battlecards</strong> from competitor data. Klue provides templates that your team fills in manually.
            </p>
            <p className="text-slate-300">
              For teams that want insights <strong>now</strong>, not after hours of manual work, RivalEdge delivers.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">GEO: RivalEdge's Exclusive Feature</h2>
            <p className="text-slate-300 mb-4">
              RivalEdge is the <strong>only CI platform with built-in GEO optimization</strong>. While Klue helps you track competitors, RivalEdge also ensures <strong>your own brand is discoverable by AI</strong>.
            </p>
            <p className="text-slate-300">
              In 2026, if ChatGPT doesn't know you exist, you're invisible to 50% of buyers. RivalEdge fixes that.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4">When to Choose Klue</h2>
            <p className="text-slate-300 mb-4">
              Klue makes sense for <strong>enterprise sales teams</strong> that:
            </p>
            <ul className="list-disc list-inside text-slate-300 space-y-2">
              <li>Need deep Salesforce CRM integration</li>
              <li>Have dedicated competitive intelligence analysts</li>
              <li>Require custom battlecard workflows</li>
              <li>Budget for enterprise software ($10K+/year)</li>
            </ul>
          </section>
        </div>

        <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-8 mt-12 text-center">
          <h3 className="text-2xl font-bold mb-3">Try RivalEdge Free for 14 Days</h3>
          <p className="text-slate-300 mb-6">
            See why teams are choosing RivalEdge over Klue. No credit card required.
          </p>
          <Link 
            href="/sign-up"
            className="inline-block bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
          >
            Start Free Trial →
          </Link>
        </div>
      </div>
    </div>
  );
}
