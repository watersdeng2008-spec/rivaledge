import Link from 'next/link';
import { Check, Zap, Bell, Shield, Sparkles, BarChart3, Search, TrendingUp, Play } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/demo" className="text-slate-400 hover:text-white text-sm transition-colors">
              Live Demo
            </Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">
              Pricing
            </Link>
            <Link
              href="/sign-in"
              className="text-slate-400 hover:text-white text-sm transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/sign-up"
              className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors"
            >
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero — Two Products, Side by Side */}
      <section className="max-w-6xl mx-auto px-6 pt-16 pb-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-4">
            Win visibility in your market
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">and in AI.</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto">
            AI-native market intelligence. Track competitors, win AI visibility, and move faster than your market.
          </p>

          {/* Live Demo CTA */}
          <Link
            href="/demo"
            className="inline-flex items-center gap-2 mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg shadow-blue-600/20 hover:shadow-blue-600/40"
          >
            <Play className="w-5 h-5 flex-shrink-0" />
            See the AI in action — interactive demo
          </Link>
        </div>

        {/* Dual product cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {/* CI Card */}
          <div className="bg-slate-900 border border-blue-500/20 rounded-2xl p-7 flex flex-col">
            <div className="inline-flex items-center gap-2 bg-blue-600/10 border border-blue-600/20 text-blue-400 text-xs px-3 py-1 rounded-full self-start mb-4">
              <BarChart3 className="w-3.5 h-3.5" />
              Competitive Intelligence
            </div>
            <h2 className="text-2xl font-bold mb-2">
              Track competitors.<br />
              <span className="text-blue-400">Get weekly briefings.</span>
            </h2>
            <p className="text-slate-400 text-sm mb-5 leading-relaxed">
              Automated monitoring of your rivals&apos; websites, pricing, and product updates.
              AI-powered weekly digests tell you what changed and what to do about it.
            </p>
            <ul className="space-y-2.5 mb-6 flex-1">
              {[
                'Track up to 5 competitors',
                'Weekly AI digest + email alerts',
                'AI battle card generator',
                '5-minute setup — just add URLs',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <div className="text-3xl font-bold mb-1">
              $49<span className="text-base text-slate-400 font-normal">/mo</span>
            </div>
            <p className="text-slate-500 text-xs mb-5">14-day free trial. No credit card required.</p>
            <Link
              href="/sign-up"
              className="block text-center bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-semibold transition-colors"
            >
              Start free trial →
            </Link>
          </div>

          {/* GEO Card */}
          <div className="bg-slate-900 border border-purple-500/20 rounded-2xl p-7 flex flex-col relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-purple-600 text-white text-[10px] px-3 py-0.5 rounded-bl-lg font-semibold tracking-wide">
              NEW
            </div>
            <div className="inline-flex items-center gap-2 bg-purple-600/10 border border-purple-500/20 text-purple-400 text-xs px-3 py-1 rounded-full self-start mb-4">
              <Sparkles className="w-3.5 h-3.5" />
              AI Visibility (GEO)
            </div>
            <h2 className="text-2xl font-bold mb-2">
              Get recommended by AI.<br />
              <span className="text-purple-400">ChatGPT, Claude, Perplexity &amp; more.</span>
            </h2>
            <p className="text-slate-400 text-sm mb-5 leading-relaxed">
              40%+ of B2B buyers now ask AI before they search Google.
              We make sure your brand gets cited, positioned correctly, and recommended over competitors.
            </p>
            <ul className="space-y-2.5 mb-6 flex-1">
              {[
                'Monitor citations across 8 AI platforms',
                'AI-optimized content & structured data',
                'Monthly visibility & positioning reports',
                'Competitive benchmarking in AI answers',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <div className="text-3xl font-bold mb-1">
              $999<span className="text-base text-slate-400 font-normal">/mo</span>
            </div>
            <p className="text-slate-500 text-xs mb-5">+ $3,500 one-time setup. Enterprise-grade AI visibility — available standalone.</p>
            <Link
              href="/geo"
              className="block text-center bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-xl font-semibold transition-colors"
            >
              Get found by AI search →
            </Link>
          </div>
        </div>

        {/* Testimonial */}
        <div className="mt-10 max-w-xl mx-auto text-center">
          <blockquote className="text-lg text-slate-300 italic border-l-4 border-blue-500 pl-4">
            &ldquo;Finally, a tool that pays for itself the first time it prevents surprise.&rdquo;
          </blockquote>
          <p className="text-slate-400 text-sm mt-2">— SaaS Founder</p>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-4">What you get</h2>
        <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
          Competitor monitoring from $49/mo. AI visibility from $999/mo.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Automated scraping</h3>
            <p className="text-slate-400 text-sm">
              We monitor your competitors&apos; websites, pricing pages, and product updates automatically — no manual work.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Bell className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Weekly AI briefings</h3>
            <p className="text-slate-400 text-sm">
              Get a concise digest every week summarizing what changed, what matters, and what to do about it.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Battle cards</h3>
            <p className="text-slate-400 text-sm">
              Generate AI-powered battle cards for any competitor — perfect for sales calls and competitive positioning.
            </p>
          </div>
          <div className="bg-slate-900 border border-purple-500/20 rounded-xl p-6">
            <div className="w-10 h-10 bg-purple-600/10 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI search visibility</h3>
            <p className="text-slate-400 text-sm">
              See how ChatGPT, Claude, and Perplexity describe your brand — and your competitors. Monthly citation tracking.
            </p>
          </div>
        </div>
      </section>

      {/* Why They Work Better Together */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-4">
          One platform. Two angles on the same market.
        </h2>
        <p className="text-slate-400 text-center mb-12 max-w-3xl mx-auto leading-relaxed">
          Most companies track competitors. Very few understand how AI systems are
          reshaping competitive visibility. RivalEdge connects both — so you know
          what your market is doing <em>and</em> how AI is positioning everyone in it.
        </p>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-slate-900 border border-blue-500/15 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <BarChart3 className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-blue-400">Competitive Intelligence</h3>
            </div>
            <p className="text-slate-300 text-sm mb-4 leading-relaxed">
              Know what competitors are doing — pricing changes, feature launches,
              messaging pivots, new market entries — before it impacts your business.
            </p>
            <ul className="space-y-2">
              {[
                'Automated website & pricing monitoring',
                'Weekly AI briefings with actionable insights',
                'Battle cards for every competitor',
                'Slack & email alerts on critical changes',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-400">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-slate-900 border border-purple-500/15 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-600/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-purple-400">Generative Engine Optimization</h3>
            </div>
            <p className="text-slate-300 text-sm mb-4 leading-relaxed">
              Understand how AI systems like ChatGPT, Claude, and Perplexity describe
              and recommend your brand — and your competitors. Monthly visibility and
              citation tracking across every major AI platform.
            </p>
            <ul className="space-y-2">
              {[
                'AI crawler infrastructure for 8 platforms',
                'Monthly citation & visibility reports',
                'Competitor comparison in AI answers',
                'Content pipeline optimization for AI discovery',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-400">
                  <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Synergy payoff */}
        <div className="mt-10 max-w-3xl mx-auto text-center bg-gradient-to-r from-blue-600/5 via-purple-600/10 to-blue-600/5 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-300 text-lg leading-relaxed">
            <span className="text-blue-400 font-semibold">CI</span> tells you what
            competitors are doing.{' '}
            <span className="text-purple-400 font-semibold">AI Visibility</span> tells you
            how AI interprets and recommends them.{' '}
            <span className="text-white font-semibold">
              Together, they give you market movement, narrative positioning, and
              AI discoverability — one platform, one dashboard.
            </span>
          </p>
        </div>
      </section>

      {/* The Discovery Layer Has Changed */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-4">
          The discovery layer has changed
        </h2>
        <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
          How buyers find products has shifted. Google isn&apos;t the only front door anymore.
        </p>
        
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center mb-4">
              <Search className="w-5 h-5 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Traditional Search</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              For years, SERP rankings determined who got discovered. SEO was a one-channel game. 
              Google was the front door to every market.
            </p>
          </div>
          
          <div className="bg-slate-900 border border-purple-500/20 rounded-xl p-6">
            <div className="w-10 h-10 bg-purple-600/10 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI Discovery</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              ChatGPT, Claude, and Perplexity now shape B2B buyer research. 
              AI-generated recommendations are replacing organic search results — 40%+ of discovery starts with AI.
            </p>
          </div>
          
          <div className="bg-slate-900 border border-blue-500/20 rounded-xl p-6">
            <div className="w-10 h-10 bg-blue-600/10 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Competitive Pressure</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Competitors who optimize for AI visibility are capturing mindshare before buyers ever visit a website. 
              If AI doesn&apos;t know you, you don&apos;t exist.
            </p>
          </div>
        </div>
      </section>

      {/* Built For */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <h2 className="text-3xl font-bold text-center mb-4">
          Built for teams that can&apos;t afford to be invisible
        </h2>
        <p className="text-slate-400 text-center mb-10 max-w-2xl mx-auto">
          Whether you&apos;re defending market share or fighting to get noticed — RivalEdge gives you the intel to move faster.
        </p>
        
        <div className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
          {[
            { icon: '🏢', label: 'SaaS & B2B' },
            { icon: '🛒', label: 'eCommerce & Amazon' },
            { icon: '🤝', label: 'Agencies & Consultants' },
            { icon: '🏥', label: 'Healthcare & Professional Services' },
            { icon: '💰', label: 'Fintech & Financial Services' },
            { icon: '📦', label: 'DTC & CPG Brands' },
          ].map((u) => (
            <div key={u.label} className="bg-slate-900 border border-slate-800 rounded-full px-5 py-2.5 flex items-center gap-2 hover:border-slate-600 transition-colors">
              <span className="text-base">{u.icon}</span>
              <span className="text-sm text-slate-300 font-medium">{u.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA — Urgency */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Your competitors are already optimizing for AI.
          </h2>
          <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">
            Every month you wait is market share lost. RivalEdge gives you the full picture — 
            competitor monitoring from $49/mo, AI visibility from $999/mo. Start with one, 
            add the other when you're ready.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/sign-up"
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-semibold transition-colors text-lg"
            >
              Start free trial →
            </Link>
            <Link
              href="/demo"
              className="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white px-8 py-3 rounded-xl font-semibold transition-colors inline-flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              See interactive demo
            </Link>
          </div>
          <p className="text-slate-500 text-sm mt-4">14-day free trial. No credit card required.</p>
        </div>
      </section>

      {/* Testimonial */}
      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-slate-800">
        <div className="max-w-3xl mx-auto text-center">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 md:p-12">
            <p className="text-xl md:text-2xl text-slate-300 italic mb-6">
              &ldquo;Finally, a tool that pays for itself the first time it prevents surprise.&rdquo;
            </p>
            <div className="flex items-center justify-center gap-3">
              <div className="w-10 h-10 bg-blue-600/20 rounded-full flex items-center justify-center">
                <span className="text-blue-400 font-semibold">S</span>
              </div>
              <div className="text-left">
                <p className="text-slate-200 font-medium">Sal Leone</p>
                <p className="text-slate-400 text-sm">Founder, RouzeIQ</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-6xl mx-auto px-6 py-16" id="pricing">
        <h2 className="text-3xl font-bold text-center mb-12">Simple, honest pricing</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-8">
            <h3 className="text-xl font-semibold mb-1">Solo</h3>
            <p className="text-slate-400 text-sm mb-6">For indie founders and small teams</p>
            <div className="text-4xl font-bold mb-6">
              $49<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>
            <ul className="space-y-3 mb-8">
              {['Track up to 5 competitors', 'Weekly AI digest', 'Email alerts', 'Battle card generator'].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href="/sign-up"
              className="block text-center bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Get started
            </Link>
          </div>
          <div className="bg-blue-600/10 border border-blue-500/50 rounded-xl p-8 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-semibold">
              MOST POPULAR
            </div>
            <h3 className="text-xl font-semibold mb-1">Pro</h3>
            <p className="text-slate-400 text-sm mb-6">For growing teams and agencies</p>
            <div className="text-4xl font-bold mb-6">
              $99<span className="text-lg text-slate-400 font-normal">/mo</span>
            </div>
            <ul className="space-y-3 mb-8">
              {[
                'Track up to 10 competitors',
                'Daily AI digest',
                'Slack + email alerts',
                'Battle card generator',
                'API access',
                'Priority support',
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href="/sign-up"
              className="block text-center bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-semibold transition-colors"
            >
              Get started
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-8 mt-16">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-slate-500 text-sm">© 2026 RivalEdge · Aether Holding LLC</span>
          <div className="flex gap-4 mt-2">
            <a href="/privacy" className="text-slate-500 text-sm hover:text-slate-300">Privacy Policy</a>
            <a href="/terms" className="text-slate-500 text-sm hover:text-slate-300">Terms of Service</a>
            <a href="mailto:support@rivaledge.ai" className="text-slate-500 text-sm hover:text-slate-300">Support</a>
          </div>
          <div className="flex gap-6 text-slate-500 text-sm">
            <Link href="/demo" className="hover:text-white transition-colors">Demo</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="/sign-in" className="hover:text-white transition-colors">Sign in</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
