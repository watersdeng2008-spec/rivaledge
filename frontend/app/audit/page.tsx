"use client";

import { useState } from "react";
import Link from "next/link";

export const dynamic = 'force-static';

export default function FreeAuditPage() {
  const [brandName, setBrandName] = useState("");
  const [category, setCategory] = useState("");
  const [competitors, setCompetitors] = useState(["", "", ""]);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleCompetitorChange = (index: number, value: string) => {
    const newCompetitors = [...competitors];
    newCompetitors[index] = value;
    setCompetitors(newCompetitors);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    const validCompetitors = competitors.filter(c => c.trim() !== "");
    
    if (validCompetitors.length === 0) {
      setError("Please enter at least one competitor");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/ars/audit/free", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: brandName,
          category,
          competitors: validCompetitors,
          email: email || undefined,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Audit failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to RivalEdge
          </Link>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Free AI Visibility Audit
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            See how AI recommends your brand vs. your competitors in 60 seconds
          </p>
        </div>

        {/* What You Get */}
        {!result && (
          <div className="grid md:grid-cols-3 gap-4 mb-12">
            {[
              {
                title: "AI Recommendation Share",
                desc: "Your percentage of AI buying conversations vs. competitors",
              },
              {
                title: "Competitor Comparison",
                desc: "Side-by-side AI visibility across ChatGPT, Perplexity, Claude",
              },
              {
                title: "Actionable Insights",
                desc: "Specific recommendations to improve your AI visibility",
              },
            ].map((item, i) => (
              <div key={i} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <h3 className="font-semibold text-blue-400 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400">{item.desc}</p>
              </div>
            ))}
          </div>
        )}

        {/* Form or Results */}
        {!result ? (
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Your Brand Name *
                </label>
                <input
                  type="text"
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  placeholder="e.g., Acme SaaS"
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Product Category *
                </label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="e.g., Project Management Software"
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Competitors (up to 3) *
                </label>
                <div className="space-y-3">
                  {competitors.map((comp, i) => (
                    <input
                      key={i}
                      type="text"
                      value={comp}
                      onChange={(e) => handleCompetitorChange(i, e.target.value)}
                      placeholder={`Competitor ${i + 1}${i === 0 ? " *" : ""}`}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                      required={i === 0}
                    />
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Email (optional — for detailed report)
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {error && (
                <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4 text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 text-white px-8 py-4 rounded-lg font-semibold transition flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing AI responses...
                  </>
                ) : (
                  "Get My Free Audit →"
                )}
              </button>

              <p className="text-center text-slate-500 text-sm">
                Free audit checks 5 prompts across 2 AI models. No credit card required.
              </p>
            </form>
          </div>
        ) : (
          /* Results */
          <div className="space-y-6">
            {/* ARS Score */}
            <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-8 border border-blue-700/50 text-center">
              <h2 className="text-lg text-slate-300 mb-2">Your AI Recommendation Share</h2>
              <div className="text-6xl font-bold text-blue-400 mb-2">
                {result.ars_score}%
              </div>
              <p className="text-slate-400">
                You appear in {result.brand_mentions} out of {result.total_queries} AI buying conversations
              </p>
            </div>

            {/* Ranking */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-4">Category Ranking</h3>
              <div className="space-y-3">
                {result.ranking?.map((item: any) => (
                  <div key={item.rank} className="flex items-center">
                    <div className="w-8 text-slate-500">#{item.rank}</div>
                    <div className="flex-1 mx-4">
                      <div className="bg-slate-700 rounded-full h-4 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            item.brand === result.brand_name
                              ? "bg-blue-500"
                              : "bg-slate-500"
                          }`}
                          style={{ width: `${Math.min(item.ars * 2, 100)}%` }}
                        />
                      </div>
                    </div>
                    <div className="w-24 text-right">
                      <span className={item.brand === result.brand_name ? "text-blue-400 font-semibold" : "text-slate-400"}>
                        {item.ars}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Competitor Scores */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold mb-4">Competitor AI Visibility</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {Object.entries(result.competitor_scores || {}).map(([comp, score]: [string, any]) => (
                  <div key={comp} className="bg-slate-700/50 rounded-lg p-4">
                    <div className="text-slate-400 text-sm">{comp}</div>
                    <div className="text-2xl font-bold text-slate-300">{score}%</div>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-8 border border-blue-700/50 text-center">
              <h3 className="text-xl font-bold mb-4">Want Weekly AI Visibility Tracking?</h3>
              <p className="text-slate-300 mb-6">
                Upgrade to RivalEdge Pro to monitor your AI Recommendation Share weekly, 
                track up to 10 competitors, and get alerts when competitors gain ground.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  href="/pricing" 
                  className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold transition"
                >
                  View Pricing
                </Link>
                <button
                  onClick={() => {setResult(null); setBrandName(""); setCategory(""); setCompetitors(["", "", ""]);}}
                  className="bg-slate-700 hover:bg-slate-600 text-white px-8 py-3 rounded-lg font-semibold transition"
                >
                  Run Another Audit
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Newsletter Signup */}
        {!result && (
          <div className="mt-12 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-8 border border-blue-700/30">
            <div className="text-center">
              <h3 className="text-xl font-bold mb-2">Get Weekly AI Visibility Intel</h3>
              <p className="text-slate-400 mb-6 max-w-xl mx-auto">
                One email every Tuesday. AI search shifts, competitive moves, and GEO tips 
                for B2B founders. No spam, unsubscribe anytime.
              </p>
              <form 
                onSubmit={async (e) => {
                  e.preventDefault();
                  const form = e.target as HTMLFormElement;
                  const email = (form.elements.namedItem('newsletter-email') as HTMLInputElement).value;
                  try {
                    const res = await fetch('/api/leads/newsletter', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ email, source: 'audit_page' }),
                    });
                    if (res.ok) {
                      alert('Thanks! You\'re subscribed to GEO + CI Insights.');
                      form.reset();
                    } else {
                      alert('Something went wrong. Please try again.');
                    }
                  } catch {
                    alert('Something went wrong. Please try again.');
                  }
                }}
                className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
              >
                <input
                  name="newsletter-email"
                  type="email"
                  placeholder="you@company.com"
                  required
                  className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold transition whitespace-nowrap"
                >
                  Subscribe →
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Trust Signals */}
        {!result && (
          <div className="mt-12 grid md:grid-cols-3 gap-6 text-center">
            {[
              { number: "5", label: "AI prompts analyzed" },
              { number: "2", label: "AI models checked" },
              { number: "60", label: "Seconds to results" },
            ].map((stat, i) => (
              <div key={i} className="bg-slate-800/30 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-400">{stat.number}</div>
                <div className="text-sm text-slate-500">{stat.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
