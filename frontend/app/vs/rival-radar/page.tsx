import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "RivalEdge vs. Rival Radar: AI-Native CI Comparison",
  description: "Compare RivalEdge vs. Rival Radar. RivalEdge adds AI search visibility (GEO) to competitive intelligence — same price, 3x the value.",
};

export default function RivalEdgeVsRivalRadar() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="mb-12">
          <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to RivalEdge
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            RivalEdge vs. Rival Radar
          </h1>
          <p className="text-xl text-slate-400">
            Same price. 3x the value. CI + GEO in one platform.
          </p>
        </div>

        {/* Quick Answer */}
        <div className="bg-slate-800/50 rounded-xl p-6 mb-12 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">The Short Answer</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose Rival Radar if:</strong></p>
              <p className="text-sm text-slate-400">You want the cheapest possible AI battlecards ($49/month) and don't need AI search visibility tracking.</p>
            </div>
            <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose RivalEdge if:</strong></p>
              <p className="text-sm text-slate-400">You want competitive intelligence AND AI search visibility (GEO) in one platform — because knowing what competitors do is only half the battle.</p>
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
                  <th className="pb-3 text-slate-400 font-medium">Rival Radar</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {[
                  ["Starting Price", "$49/month", "$49/month"],
                  ["AI Battlecards", "✅ Yes", "✅ Yes"],
                  ["GEO / AI Search Visibility", "✅ Yes", "❌ No"],
                  ["AI Recommendation Share", "✅ Yes", "❌ No"],
                  ["Competitor Tracking", "✅ Yes — 3-20", "✅ Yes — limited"],
                  ["Weekly CI Reports", "✅ Yes", "⚠️ Basic"],
                  ["AI-Generated Insights", "✅ Yes", "✅ Yes"],
                  ["Slack Integration", "✅ Yes", "❌ No"],
                  ["API Access", "🔄 Coming soon", "❌ No"],
                  ["Free Trial", "✅ Yes", "✅ Yes"],
                ].map(([feature, rival, radar], i) => (
                  <tr key={i} className="border-b border-slate-800">
                    <td className="py-3 text-slate-300">{feature}</td>
                    <td className="py-3 text-blue-400">{rival}</td>
                    <td className="py-3 text-slate-400">{radar}</td>
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
              <h3 className="text-lg font-semibold mb-3 text-blue-400">1. GEO / AI Search Visibility</h3>
              <p className="text-slate-300 mb-2"><strong>Rival Radar:</strong> Competitive intelligence only. Tracks what competitors do on their websites, pricing, positioning.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> CI + GEO. Tracks what competitors do AND how AI systems (ChatGPT, Perplexity, Claude) recommend them over you.</p>
              <p className="text-slate-400 text-sm">Why it matters: 55% of buyers now start their research in AI search. If you only track websites, you're missing where the buying journey actually happens.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">2. Depth of Intelligence</h3>
              <p className="text-slate-300 mb-2"><strong>Rival Radar:</strong> AI battlecards in 60 seconds. Fast, but surface-level.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> AI battlecards + strategic interpretation + AI recommendation share + weekly CI reports. Deeper intelligence, more actionable.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">3. Integration Ecosystem</h3>
              <p className="text-slate-300 mb-2"><strong>Rival Radar:</strong> Standalone tool. No integrations mentioned.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> Slack alerts, email digests, webhook APIs (coming), and soon CRM integrations.</p>
            </div>
          </div>
        </div>

        {/* Who Should Choose */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-4">Who Should Choose Rival Radar?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Solo founders on tight budgets who just need basic battlecards</li>
              <li>• Teams that already have a separate GEO tool</li>
              <li>• Users who want the simplest possible CI experience</li>
            </ul>
          </div>
          <div className="bg-blue-900/30 rounded-xl p-6 border border-blue-700/50">
            <h3 className="text-lg font-semibold mb-4 text-blue-400">Who Should Choose RivalEdge?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Teams that need CI + GEO together (most modern teams do)</li>
              <li>• Companies where AI search visibility affects revenue</li>
              <li>• Founders who want strategic interpretation, not just data</li>
              <li>• Teams planning to scale — need a platform that grows with them</li>
              <li>• Anyone who wants to know not just WHAT competitors do, but HOW AI recommends them</li>
            </ul>
          </div>
        </div>

        {/* Value Proposition */}
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-6 mb-12 border border-blue-700/50">
          <h3 className="text-lg font-semibold mb-4 text-blue-400">Why RivalEdge Costs the Same But Delivers More</h3>
          <p className="text-slate-300 mb-4">Both start at $49/month. But RivalEdge includes:</p>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-slate-400 text-sm mb-2">Everything Rival Radar does:</p>
              <ul className="text-slate-300 text-sm space-y-1">
                <li>✅ AI battlecards</li>
              </ul>
            </div>
            <div>
              <p className="text-blue-400 text-sm mb-2">Plus what Rival Radar doesn't:</p>
              <ul className="text-slate-300 text-sm space-y-1">
                <li>✅ GEO tracking (AI search visibility)</li>
                <li>✅ AI Recommendation Share</li>
                <li>✅ Weekly CI reports</li>
                <li>✅ Slack integration</li>
              </ul>
            </div>
          </div>
          <p className="text-center text-blue-400 font-semibold mt-4">Same price. 3x the value.</p>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-8 border border-blue-700/50">
          <h2 className="text-2xl font-bold mb-4">See Why Teams Choose RivalEdge</h2>
          <p className="text-slate-300 mb-6">Get both competitive intelligence AND AI search visibility — with the metric that matters: AI Recommendation Share.</p>
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
          <p>Last updated: May 2026. Based on publicly available information.</p>
        </div>
      </div>
    </div>
  );
}
