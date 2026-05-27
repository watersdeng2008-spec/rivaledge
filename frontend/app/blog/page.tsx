import Link from 'next/link';
import { ArrowLeft, Calendar, Clock } from 'lucide-react';

export const metadata = {
  title: 'Blog — RivalEdge',
  description: 'Insights on competitive intelligence, GEO, and AI search optimization.',
};

const posts = [
  {
    slug: 'geo-vs-seo',
    title: 'GEO vs SEO: Why Generative Engine Optimization Is the New Must-Have for 2026',
    excerpt: 'SEO got you found on Google. GEO gets you recommended by AI. Learn the key differences and how to start optimizing for ChatGPT, Claude, and Perplexity.',
    date: 'May 17, 2026',
    readTime: '6 min read',
    category: 'GEO',
    author: 'Waters Deng',
  },
  {
    slug: 'rivaledge-vs-crayon',
    title: 'RivalEdge vs Crayon: A Side-by-Side Comparison',
    excerpt: 'Why pay $20K+/year when you can get 80% of the value for $49/month? A detailed comparison of features, pricing, and setup time.',
    date: 'May 17, 2026',
    readTime: '5 min read',
    category: 'Comparison',
    author: 'Waters Deng',
  },
  {
    slug: 'rivaledge-vs-klue',
    title: 'RivalEdge vs Klue: A Side-by-Side Comparison',
    excerpt: 'Enterprise CI vs startup-friendly AI. See why lean teams are choosing RivalEdge over Klue.',
    date: 'May 17, 2026',
    readTime: '4 min read',
    category: 'Comparison',
    author: 'Waters Deng',
  },
  {
    slug: 'rivaledge-vs-visualping',
    title: 'RivalEdge vs Visualping: A Side-by-Side Comparison',
    excerpt: 'Change detection vs AI-powered intelligence. Why RivalEdge delivers 10x more value for $50 less per month.',
    date: 'May 17, 2026',
    readTime: '3 min read',
    category: 'Comparison',
    author: 'Waters Deng',
  },
  {
    slug: 'rivaledge-vs-spyfu',
    title: 'RivalEdge vs SpyFu: A Side-by-Side Comparison',
    excerpt: 'SEO/PPC tracking vs full competitive intelligence. Why RivalEdge delivers broader coverage at a similar price.',
    date: 'May 17, 2026',
    readTime: '4 min read',
    category: 'Comparison',
    author: 'Waters Deng',
  },
  {
    slug: 'rivaledge-vs-alphasense',
    title: 'RivalEdge vs AlphaSense: A Side-by-Side Comparison',
    excerpt: 'Enterprise market intelligence vs startup-friendly competitive intelligence. See the 100x price difference.',
    date: 'May 17, 2026',
    readTime: '4 min read',
    category: 'Comparison',
    author: 'Waters Deng',
  },
];

export default function BlogPage() {
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
            <Link href="/" className="text-slate-400 hover:text-white text-sm transition-colors">
              Home
            </Link>
            <Link href="/pricing" className="text-slate-400 hover:text-white text-sm transition-colors">
              Pricing
            </Link>
            <Link href="/sign-up" className="bg-blue-600 hover:bg-blue-500 text-white text-sm px-4 py-2 rounded-lg transition-colors">
              Start free trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Header */}
      <section className="max-w-4xl mx-auto px-6 pt-16 pb-8">
        <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to home
        </Link>
        <h1 className="text-4xl font-bold mb-4">RivalEdge Blog</h1>
        <p className="text-lg text-slate-400">
          Insights on competitive intelligence, GEO, and winning in AI search.
        </p>
      </section>

      {/* Posts */}
      <section className="max-w-4xl mx-auto px-6 pb-20">
        <div className="space-y-8">
          {posts.map((post) => (
            <article key={post.slug} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/30 transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <span className="bg-blue-600/10 text-blue-400 text-xs px-2 py-1 rounded-full">
                  {post.category}
                </span>
                <span className="flex items-center gap-1 text-slate-500 text-sm">
                  <Calendar className="w-3.5 h-3.5" />
                  {post.date}
                </span>
                <span className="flex items-center gap-1 text-slate-500 text-sm">
                  <Clock className="w-3.5 h-3.5" />
                  {post.readTime}
                </span>
              </div>
              <h2 className="text-xl font-bold mb-2 hover:text-blue-400 transition-colors">
                <Link href={`/blog/${post.slug}`}>
                  {post.title}
                </Link>
              </h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                {post.excerpt}
              </p>
              <p className="text-slate-500 text-sm mt-3">
                By{' '}
                <Link href="/blog/authors/waters-deng" className="text-slate-300 hover:text-white underline underline-offset-2">
                  {post.author}
                </Link>
              </p>
              <Link 
                href={`/blog/${post.slug}`}
                className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-sm mt-4 transition-colors"
              >
                Read more →
              </Link>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
