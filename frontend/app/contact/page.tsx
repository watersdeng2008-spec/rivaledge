import Link from 'next/link';
import { ArrowRight, Building2, HelpCircle, Mail } from 'lucide-react';

const salesMailto = 'mailto:ben.d@rivaledge.ai?subject=Sales%20Inquiry';
const supportMailto = 'mailto:ben.d@rivaledge.ai?subject=Support%20Request';

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6">
          <Link href="/" className="flex items-center gap-2">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/" className="text-sm text-slate-400 transition-colors hover:text-white">
              Home
            </Link>
            <Link href="/pricing" className="text-sm text-slate-400 transition-colors hover:text-white">
              Pricing
            </Link>
            <Link href="/demo" className="text-sm text-slate-400 transition-colors hover:text-white">
              Demo
            </Link>
          </div>
        </div>
      </nav>

      <main>
        <section className="mx-auto max-w-4xl px-6 py-20 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-600/10 px-4 py-1.5 text-sm text-blue-300">
            <Mail className="h-4 w-4" />
            Sales and support
          </div>
          <h1 className="mb-5 text-4xl font-bold md:text-5xl">Contact Sales</h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg leading-relaxed text-slate-300">
            Want to talk through Enterprise, AI visibility, or competitive intelligence for your team?
            Send us a note and we will help you find the right setup.
          </p>
          <a
            href={salesMailto}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-500"
          >
            Email ben.d@rivaledge.ai
            <ArrowRight className="h-4 w-4" />
          </a>
          <p className="mt-5 text-sm text-slate-500">We typically respond within 24 hours.</p>
        </section>

        <section className="mx-auto grid max-w-5xl gap-5 px-6 pb-20 md:grid-cols-2">
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-600/5 p-6">
            <Building2 className="mb-4 h-6 w-6 text-emerald-400" />
            <h2 className="mb-2 text-xl font-semibold">Enterprise</h2>
            <p className="mb-5 text-sm leading-relaxed text-slate-400">
              Full-service market intelligence, AI visibility assets, weekly competitor reports,
              custom integrations, and dedicated account support.
            </p>
            <a href={salesMailto} className="text-sm font-semibold text-emerald-300 transition-colors hover:text-emerald-200">
              Talk to sales
            </a>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <HelpCircle className="mb-4 h-6 w-6 text-blue-400" />
            <h2 className="mb-2 text-xl font-semibold">General Questions</h2>
            <p className="mb-5 text-sm leading-relaxed text-slate-400">
              Questions about pricing, setup, AI search visibility, competitor tracking,
              or whether RivalEdge is a fit for your category.
            </p>
            <a href={supportMailto} className="text-sm font-semibold text-blue-300 transition-colors hover:text-blue-200">
              Send a question
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}
