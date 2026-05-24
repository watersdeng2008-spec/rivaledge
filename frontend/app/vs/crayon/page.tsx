import { Metadata } from "next";
import Link from "next/link";

export const dynamic = 'force-static';

export const metadata: Metadata = {
  title: "RivalEdge vs. Crayon: Competitive Intelligence Comparison",
  description: "Compare RivalEdge vs. Crayon for competitive intelligence. See why teams choose RivalEdge for AI-native CI + GEO at a fraction of the cost.",
};

export default function RivalEdgeVsCrayon() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="mb-12">
          <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to RivalEdge
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            RivalEdge vs. Crayon
          </h1>
          <p className="text-xl text-slate-400">
            AI-native competitive intelligence + AI search visibility at 10x lower cost
          </p>
        </div>

        {/* Quick Answer */}
        <div className="bg-slate-800/50 rounded-xl p-6 mb-12 border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">The Short Answer</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-700/50 rounded-lg p-4">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose Crayon if:</strong></p>
              <p className="text-sm text-slate-400">You're a large enterprise with dedicated RevOps teams, need deep Salesforce integration, and have $20K-$100K/year budget.</p>
            </div>
            <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <p className="text-slate-300 mb-2"><strong className="text-white">Choose RivalEdge if:</strong></p>
              <p className="text-sm text-slate-400">You want AI-native competitive intelligence that combines competitor tracking with AI search visibility — at a fraction of the cost, with setup in minutes not weeks.</p>
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
                  <th className="pb-3 text-slate-400 font-medium">Crayon</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {[
                  ["Starting Price", "$49/month", "$20,000/year"],
                  ["Setup Time", "Minutes", "Weeks"],
                  ["AI-Native Insights", "✅ Yes", "⚠️ Partial"],
                  ["GEO / AI Search Visibility", "✅ Yes", "❌ No"],
                  ["Competitor Tracking", "✅ Yes", "✅ Yes"],
                  ["Battlecards", "✅ AI-generated", "✅ Mature"],
                  ["Salesforce Integration", "🔄 Coming soon", "✅ Deep"],
                  ["Slack Alerts", "✅ Yes", "✅ Yes"],
                  ["AI Recommendation Share", "✅ Yes", "❌ No"],
                  ["Free Trial", "✅ Yes", "❌ Demo only"],
                ].map(([feature, rival, crayon], i) => (
                  <tr key={i} className="border-b border-slate-800">
                    <td className="py-3 text-slate-300">{feature}</td>
                    <td className="py-3 text-blue-400">{rival}</td>
                    <td className="py-3 text-slate-400">{crayon}</td>
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
              <h3 className="text-lg font-semibold mb-3 text-blue-400">1. AI Search Visibility (GEO)</h3>
              <p className="text-slate-300 mb-2"><strong>Crayon tracks:</strong> Website changes, pricing updates, battlecard data</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge tracks:</strong> All of the above PLUS how your brand appears in ChatGPT, Perplexity, Claude, and Google AI Overviews — compared to your competitors.</p>
              <p className="text-slate-400 text-sm">Why it matters: The highest-intent buyers are now searching in AI, not Google. If you only track traditional competitive intelligence, you're missing where the buying journey actually starts.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">2. Speed to Insight</h3>
              <p className="text-slate-300 mb-2"><strong>Crayon:</strong> Enterprise implementation with dedicated onboarding. Powerful, but slow.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> Sign up, add competitors, get insights in under 5 minutes. AI synthesizes the data so you don't need an analyst to interpret it.</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">3. Pricing Transparency</h3>
              <p className="text-slate-300 mb-2"><strong>Crayon:</strong> Custom enterprise pricing. You need a sales call to get a quote.</p>
              <p className="text-slate-300 mb-2"><strong>RivalEdge:</strong> Clear pricing from $49/month. No hidden fees, no annual contracts required.</p>
            </div>
          </div>
        </div>

        {/* Who Should Choose */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-4">Who Should Choose Crayon?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Enterprise companies ($500M+ revenue)</li>
              <li>• Teams with 5+ dedicated CI staff</li>
              <li>• Organizations deep in Salesforce ecosystem</li>
              <li>• Companies needing sophisticated win/loss analysis</li>
            </ul>
          </div>
          <div className="bg-blue-900/30 rounded-xl p-6 border border-blue-700/50">
            <h3 className="text-lg font-semibold mb-4 text-blue-400">Who Should Choose RivalEdge?</h3>
            <ul className="space-y-2 text-slate-400 text-sm">
              <li>• Growth-stage companies ($5M-$100M revenue)</li>
              <li>• Lean teams (1-3 people handling CI)</li>
              <li>• Companies where AI search visibility matters</li>
              <li>• Founders who need insights fast, without enterprise bloat</li>
              <li>• Teams that want CI + GEO in one platform</li>
            </ul>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-8 border border-blue-700/50">
          <h2 className="text-2xl font-bold mb-4">See What Crayon Can't Show You</h2>
          <p className="text-slate-300 mb-6">Get your AI Recommendation Share — the metric that shows how often AI recommends your brand vs. competitors.</p>
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
          <p>Last updated: May 2026. Pricing and features based on publicly available information.</p>
        </div>
      </div>
    </div>
  );
}
