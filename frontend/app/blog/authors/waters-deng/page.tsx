import Link from 'next/link';
import { ArrowLeft, ExternalLink } from 'lucide-react';

export const metadata = {
  title: 'Waters Deng, Founder of RivalEdge.ai — RivalEdge',
  description: 'Author page for Waters Deng, founder of RivalEdge.ai and writer on competitive intelligence, AI search, and generative engine optimization.',
};

const PERSON_SCHEMA = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'Waters Deng',
  jobTitle: 'Founder',
  worksFor: {
    '@type': 'Organization',
    name: 'RivalEdge.ai',
    url: 'https://www.rivaledge.ai',
  },
  url: 'https://www.rivaledge.ai/blog/authors/waters-deng',
  sameAs: [
    'https://www.linkedin.com/in/waters-deng',
    'https://twitter.com/waters_deng',
  ],
};

export default function WatersDengAuthorPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(PERSON_SCHEMA) }}
      />

      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-blue-400">
            <img src="/logo.jpg" alt="RivalEdge" className="h-8 w-8 rounded-sm" />
            RivalEdge
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/blog" className="text-slate-400 hover:text-white text-sm transition-colors">Blog</Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">Pricing</Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">Start free trial</Link>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-16">
        <Link href="/blog" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to blog
        </Link>

        <section className="grid gap-8 md:grid-cols-[160px_1fr] md:items-start">
          <img
            src="/logo.jpg"
            alt="RivalEdge founder Waters Deng"
            className="h-40 w-40 rounded-2xl border border-slate-800 object-cover"
          />
          <div>
            <p className="text-blue-400 text-sm font-semibold uppercase tracking-wide mb-3">
              Author
            </p>
            <h1 className="text-4xl font-bold mb-3">Waters Deng</h1>
            <p className="text-lg text-slate-300 mb-5">Founder, RivalEdge.ai</p>
            <p className="text-slate-400 leading-relaxed mb-4">
              Founder of RivalEdge.ai. Building AI-native competitive intelligence and GEO tools for modern brands.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="https://www.linkedin.com/in/waters-deng"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                LinkedIn
              </a>
              <a
                href="https://twitter.com/waters_deng"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                X
              </a>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
