import Link from 'next/link';
import {
  ArrowRight,
  Bot,
  BriefcaseBusiness,
  Check,
  CircleDollarSign,
  Eye,
  LineChart,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';
import LeadCaptureForm from './components/LeadCaptureForm';

const recentSignals = [
  'Competitor reduced pricing across 43 SKUs',
  'New competitor entered the category',
  'Review sentiment declined 12% after product launch',
  'AI recommendations shifted toward a lower-priced alternative',
];

const marketSignals = [
  {
    signal: 'Competitor Moves',
    why: 'Detect product launches, positioning shifts, and strategic changes',
    icon: Target,
  },
  {
    signal: 'AI Visibility',
    why: 'See which brands AI recommends and why',
    icon: Sparkles,
  },
  {
    signal: 'Customer Sentiment',
    why: 'Identify complaints and unmet needs before competitors do',
    icon: Users,
  },
  {
    signal: 'Pricing Intelligence',
    why: 'Monitor discounting and pricing strategy changes',
    icon: CircleDollarSign,
  },
  {
    signal: 'Hiring Activity',
    why: 'Spot expansion plans and strategic priorities',
    icon: BriefcaseBusiness,
  },
  {
    signal: 'Emerging Competitors',
    why: 'Detect new entrants before they become major threats',
    icon: TrendingUp,
  },
];

const aiVisibilityPoints = [
  'See which brands AI recommends',
  'Compare your visibility against competitors',
  'Identify missing topics and citations',
  'Track visibility changes over time',
  'Discover why competitors are being recommended',
];

const audience = [
  ['Product Marketing', 'Track positioning, messaging, and launch timing'],
  ['Competitive Intelligence', 'Monitor competitor moves and market shifts'],
  ['Strategy & Innovation', 'Spot emerging trends and white space'],
  ['Founders & Executives', 'Get board-ready intelligence without the manual work'],
  ['Revenue Teams', 'Understand why deals are won or lost'],
];

const comparisonRows = [
  ['Competitor monitoring', true, true],
  ['Customer sentiment tracking', true, false],
  ['AI visibility tracking', true, false],
  ['AI recommendation analysis', true, false],
  ['Real-time market signals', true, false],
];

const steps = [
  ['Connect', 'Add your competitors and keywords. We start monitoring in minutes.'],
  ['Monitor', 'Our AI agents scan the web, news, reviews, job boards, and AI search results 24/7.'],
  ['Alert', 'Get notified when something important happens, not noise.'],
  ['Act', 'Spot threats early, find gaps, and move faster than the competition.'],
];

const plans = [
  ['Solo', 'Individual founders, small teams', '$49/mo'],
  ['Pro', 'Growing teams with 5+ competitors', '$99/mo'],
  ['Pro AI', 'Teams who need AI search visibility', '$299/mo'],
  ['Enterprise', 'Full-service market intelligence', 'Custom'],
];

function CheckMark({ active = true }: { active?: boolean }) {
  return active ? (
    <Check className="mx-auto h-5 w-5 text-emerald-400" aria-label="Included" />
  ) : (
    <span className="block text-center text-slate-600" aria-label="Not included">-</span>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6">
          <Link href="/" className="flex items-center gap-2">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/demo" className="hidden text-sm text-slate-400 transition-colors hover:text-white sm:inline">
              Live Demo
            </Link>
            <Link href="/pricing" className="text-sm text-slate-400 transition-colors hover:text-white">
              Pricing
            </Link>
            <Link href="/blog" className="hidden text-sm text-slate-400 transition-colors hover:text-white sm:inline">
              Blog
            </Link>
            <Link href="/sign-in" className="hidden text-sm text-slate-400 transition-colors hover:text-white sm:inline">
              Sign in
            </Link>
            <Link href="/sign-up" className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white transition-colors hover:bg-blue-500">
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      <main>
        <section className="mx-auto max-w-6xl px-6 pb-14 pt-16 md:pt-20">
          <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-600/10 px-3 py-1 text-sm text-blue-300">
                <LineChart className="h-4 w-4" />
                Competitive intelligence for the AI era
              </div>
              <h1 className="mb-5 max-w-4xl text-4xl font-bold leading-tight md:text-6xl">
                Spot market shifts before your competitors do.
              </h1>
              <p className="mb-8 max-w-2xl text-lg leading-relaxed text-slate-300">
                Monitor competitors, customer sentiment, pricing, product launches, hiring activity, and AI visibility from a single intelligence platform.
              </p>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Link href="/sign-up" className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-500">
                  Start Free Trial
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="#how-it-works" className="inline-flex items-center justify-center rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 font-semibold text-white transition-colors hover:bg-slate-800">
                  See How It Works
                </Link>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl shadow-blue-950/20">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Market signal feed</p>
                  <h2 className="text-xl font-semibold">Detected this week</h2>
                </div>
                <Bot className="h-6 w-6 text-blue-400" />
              </div>
              <div className="space-y-3">
                {recentSignals.map((signal) => (
                  <div key={signal} className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                    <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-400" />
                    <span className="text-sm text-slate-200">{signal}</span>
                  </div>
                ))}
              </div>
              <blockquote className="mt-5 border-l-2 border-blue-500 pl-4 text-sm italic leading-relaxed text-slate-300">
                "We spotted three new competitors entering our space two months before our board asked about them."
                <span className="mt-2 block text-slate-500">VP Strategy, category leader</span>
              </blockquote>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-3xl px-6 pb-16">
          <LeadCaptureForm
            source="homepage"
            variant="hero"
            title="See what changed in your market"
            subtitle="Enter any competitor URL and get a free snapshot of their latest moves"
            buttonText="Get my free competitor snapshot"
          />
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-4 text-center text-3xl font-bold">What our AI agents found this week</h2>
            <p className="mx-auto mb-10 max-w-2xl text-center text-slate-400">
              Recent intelligence detected across pricing pages, category narratives, customer feedback, and AI search results.
            </p>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {recentSignals.map((signal) => (
                <div key={signal} className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <Check className="mb-4 h-5 w-5 text-emerald-400" />
                  <p className="text-sm leading-relaxed text-slate-200">{signal}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-10 text-center text-3xl font-bold">Market signals that matter</h2>
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {marketSignals.map(({ signal, why, icon: Icon }) => (
                <div key={signal} className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                  <Icon className="mb-4 h-6 w-6 text-blue-400" />
                  <h3 className="mb-2 text-lg font-semibold">{signal}</h3>
                  <p className="text-sm leading-relaxed text-slate-400">{why}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto grid max-w-6xl items-center gap-10 lg:grid-cols-2">
            <div>
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-600/10 px-3 py-1 text-sm text-purple-300">
                <Sparkles className="h-4 w-4" />
                AI search visibility
              </div>
              <h2 className="mb-4 text-3xl font-bold">AI search is becoming a new competitive channel</h2>
              <p className="mb-6 leading-relaxed text-slate-400">
                When buyers ask ChatGPT, Claude, Gemini, or Perplexity for recommendations, only a handful of brands appear.
              </p>
              <p className="font-semibold text-slate-200">Understand how AI influences buyer decisions:</p>
            </div>
            <div className="rounded-2xl border border-purple-500/20 bg-slate-900 p-6">
              <div className="space-y-3">
                {aiVisibilityPoints.map((point) => (
                  <div key={point} className="flex items-center gap-3">
                    <Eye className="h-4 w-4 flex-shrink-0 text-purple-400" />
                    <span className="text-sm text-slate-300">{point}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-5xl text-center">
            <ShieldCheck className="mx-auto mb-5 h-8 w-8 text-blue-400" />
            <h2 className="mb-4 text-3xl font-bold">Why traditional competitive intelligence is no longer enough</h2>
            <p className="mx-auto mb-8 max-w-2xl text-slate-400">Markets are changing faster than ever.</p>
            <div className="grid gap-4 text-left md:grid-cols-4">
              {[
                'Competitors launch products overnight',
                'Customers leave signals across reviews and communities',
                'AI search engines increasingly influence buying decisions',
                "Manual monitoring can't keep up",
              ].map((item) => (
                <div key={item} className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-sm text-slate-300">
                  {item}
                </div>
              ))}
            </div>
            <p className="mx-auto mt-8 max-w-3xl text-lg font-semibold text-white">
              RivalEdge combines competitive intelligence and AI visibility monitoring into one continuous feedback system.
            </p>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-10 text-center text-3xl font-bold">Built for teams that need to stay ahead</h2>
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-5">
              {audience.map(([role, copy]) => (
                <div key={role} className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <h3 className="mb-2 font-semibold text-blue-300">{role}</h3>
                  <p className="text-sm leading-relaxed text-slate-400">{copy}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-4xl">
            <h2 className="mb-10 text-center text-3xl font-bold">Why RivalEdge</h2>
            <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="px-5 py-4 text-left font-medium text-slate-400">Capability</th>
                    <th className="px-5 py-4 text-center font-medium text-blue-300">RivalEdge</th>
                    <th className="px-5 py-4 text-center font-medium text-slate-400">Traditional CI Tools</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonRows.map(([label, rivaledge, traditional]) => (
                    <tr key={String(label)} className="border-b border-slate-800/60 last:border-0">
                      <td className="px-5 py-4 text-slate-200">{label}</td>
                      <td className="px-5 py-4"><CheckMark active={Boolean(rivaledge)} /></td>
                      <td className="px-5 py-4"><CheckMark active={Boolean(traditional)} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-10 text-center text-3xl font-bold">How it works</h2>
            <div className="grid gap-5 md:grid-cols-4">
              {steps.map(([title, copy], index) => (
                <div key={title} className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                  <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold">
                    {index + 1}
                  </div>
                  <h3 className="mb-2 text-lg font-semibold">{title}</h3>
                  <p className="text-sm leading-relaxed text-slate-400">{copy}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="pricing" className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-3 text-center text-3xl font-bold">Start monitoring your market in minutes.</h2>
            <div className="mt-10 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="px-5 py-4 text-left font-medium text-slate-400">Plan</th>
                    <th className="px-5 py-4 text-left font-medium text-slate-400">Best For</th>
                    <th className="px-5 py-4 text-left font-medium text-slate-400">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {plans.map(([plan, bestFor, price]) => (
                    <tr key={plan} className="border-b border-slate-800/60 last:border-0">
                      <td className="px-5 py-4 font-semibold text-white">{plan}</td>
                      <td className="px-5 py-4 text-slate-300">{bestFor}</td>
                      <td className="px-5 py-4 font-semibold text-blue-300">{price}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 px-6 py-16">
          <div className="mx-auto max-w-3xl text-center">
            <Zap className="mx-auto mb-5 h-8 w-8 text-blue-400" />
            <h2 className="mb-8 text-3xl font-bold">Stop guessing. Start knowing.</h2>
            <div className="flex flex-col justify-center gap-3 sm:flex-row">
              <Link href="/sign-up" className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-500">
                Start Free Trial
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/contact" className="inline-flex items-center justify-center rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 font-semibold text-white transition-colors hover:bg-slate-800">
                Talk to Sales
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 px-6 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 md:flex-row">
          <span className="text-sm text-slate-500">© 2026 RivalEdge · Aether Holding LLC</span>
          <div className="flex gap-4">
            <Link href="/privacy" className="text-sm text-slate-500 hover:text-slate-300">Privacy Policy</Link>
            <Link href="/terms" className="text-sm text-slate-500 hover:text-slate-300">Terms of Service</Link>
            <Link href="/pricing" className="text-sm text-slate-500 hover:text-slate-300">Pricing</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
