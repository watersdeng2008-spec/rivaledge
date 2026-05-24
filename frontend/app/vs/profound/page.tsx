import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "RivalEdge vs. Profound: GEO + CI Comparison",
  description: "Compare RivalEdge vs. Profound for AI search visibility. RivalEdge combines competitive intelligence with GEO at 10x lower cost.",
};

export default function RivalEdgeVsProfound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="mb-12">
          <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to RivalEdge
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            RivalEdge vs. Profound
          </h1>
          <p className="text-xl text-slate-400">
            Competitive intelligence + AI search visibility in one platform
          </p>
        </div>

        {/* Quick Answer */}
        <div className="bg-slate-800/50 rounded-xl p-6 mb-12 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">The Short Answer</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose Profound if:</strong></p>
              <p className="text-sm text-slate-400">You're a large enterprise (Ramp, US Bank scale), need HIPAA compliance, want 10+ AI model tracking, and have $500-$5,000+/month budget.</p>
            </div>
            <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose RivalEdge if:</strong></p>
              <p className="text-sm text-slate-400">You want AI search visibility WITH competitive intelligence context — at 10x lower cost, with competitive benchmarking built in, not bolted on.</p>
            </div>
          </div>
        </div>

        {/* Feature Comparison */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Feature Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="pb-3 text-slate-400 font-medium">Feature</th>
                  <th className="pb-3 text-blue-400 font-medium">RivalEdge</th>
                  <th className="pb-3 text-slate-400 font-medium">Profound</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {[
                  ["Starting Price", "$49/month", "$499/month"],
                  ["Setup Time", "Minutes", "Days"],
                  ["AI Models Tracked", "5 (major)", "10+"],
                  ["Competitive Intelligence", "✅ Yes — built in", "⚠️ Limited"],
                  ["AI Recommendation Share", "✅ Yes", "❌ No"],
                  ["Competitor Benchmarking", "✅ Yes — core", "⚠️ Basic"],
                  ["Battlecards", "✅ AI-generated", "❌ No"],
                  ["CI Reports", "✅ Weekly automated", "❌ No"],
                  ["Slack Integration", "✅ Yes", "✅ Yes"],
                  ["HIPAA Compliance", "🔄 Planned", "✅ Yes"],
                  ["Free Trial", "✅ Yes", "❌ Demo only"],
                ].map(([feature, rival, profound], i) => (
                  <tr key={i} className="border-b border-slate-800">
                    <td className="py-3 text-slate-300">{feature}</td>
                    <td className="py-3 text-blue-400">{rival}</td>
                    <td className="py-3 text-slate-400">{profound}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Key Differences */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Key Differences</h2>
          
          <div className="space-y-6">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">1. Competitive Context</h3>
              <p className="text-slate-300 mb-2"><strong>Profound tracks:</strong> How AI sees YOUR brand across 10+ models</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge tracks:</strong> How AI sees your brand COMPARED TO YOUR COMPETITORS across 5 major models</p>
              <p className="text-slate-400 text-sm">Why it matters: Knowing "ChatGPT mentions us 12 times" is useless without knowing "ChatGPT mentions Competitor X 47 times." RivalEdge gives you the competitive ratio, not just raw mentions.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">2. CI + GEO Integration</h3>
              <p className="text-slate-300 mb-2"><strong>Profound:</strong> Pure GEO platform. No competitive intelligence, no battlecards, no strategic interpretation.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> CI + GEO in one platform. Track competitors AND optimize your AI visibility — because they're the same problem.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">3. Pricing Accessibility</h3>
              <p className="text-slate-300 mb-2"><strong>Profound:</strong> $499/month minimum (Lite plan). Agency plan $1,499/month. Enterprise custom.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> $49/month to start. Pro at $99/month. Enterprise at $299-$999/month.</p>
              <p className="text-slate-400 text-sm">The math: Profound costs 10x more for GEO-only. RivalEdge gives you CI + GEO for the price of Profound's entry tier.</p>
            </div>
          </div>
        </div>

        {/* Who Should Choose */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-4">Who Should Choose Profound?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Enterprise brands (Fortune 500, major retailers)</li>
              <li>• Healthcare/pharma (HIPAA compliance required)</li>
              <li>• Companies needing 10+ AI model coverage</li>
              <li>• Organizations with $500+/month dedicated GEO budget</li>
              <li>• Teams that already have separate CI tools</li>
            </ul>
          </div>
          <div className="bg-blue-900/30 rounded-xl p-6 border border-blue-700/50">
            <h3 className="text-lg font-semibold mb-4 text-blue-400">Who Should Choose RivalEdge?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Growth-stage companies ($5M-$100M revenue)</li>
              <li>• Teams that need CI + GEO together</li>
              <li>• Companies where competitive context matters</li>
              <li>• Founders who want insights, not dashboards</li>
              <li>• Teams with lean budgets that need maximum value</li>
            </ul>
          </div>
        </div>

        {/* The RivalEdge Advantage */}
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-6 mb-12 border border-blue-700/50">
          <h3 className="text-lg font-semibold mb-4 text-blue-400">The RivalEdge Advantage: Competitive GEO</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm mb-2">Profound shows you:</p>
              <p className="text-slate-300 italic">"Your brand was cited 12 times in ChatGPT responses this week."</p>
            </div>
            <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/30">
              <p className="text-slate-400 text-sm mb-2">RivalEdge shows you:</p>
              <p className="text-blue-300 italic">"Your brand was cited 12 times. Competitor X was cited 47 times. Here's why — and here's how to close the gap."</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-8 border border-blue-700/50">
          <h2 className="text-2xl font-bold mb-4">See Your AI Recommendation Share</h2>
          <p className="text-slate-300 mb-6">Discover how often AI recommends your brand vs. competitors — with competitive intelligence Profound can't provide.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/audit" 
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold transition"
            >
              Start Free Audit
            </Link>
            <Link 
              href="/pricing" 
              className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-3 rounded-lg font-semibold transition"
            >
              View Pricing
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
          <p>Last updated: May 2026. Pricing from tryprofound.com.</p>
        </div>
      </div>
    </div>
  );
}
