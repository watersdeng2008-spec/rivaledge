'use client';

import type { ComponentType } from 'react';
import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Bot, Clock, ExternalLink, Globe2, RefreshCw } from 'lucide-react';

interface CrawlerVisit {
  id: string;
  crawler_name: string;
  crawler_company: string;
  crawler_pattern: string;
  page_url: string;
  ip_address: string | null;
  user_agent: string | null;
  visited_at: string;
}

export default function CrawlerDashboard() {
  const [visits, setVisits] = useState<CrawlerVisit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadVisits() {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/admin/crawlers', { cache: 'no-store' });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Unable to load crawler visits.');
        }

        setVisits(data.visits || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load crawler visits.');
      } finally {
        setLoading(false);
      }
    }

    loadVisits();
  }, []);

  const stats = useMemo(() => {
    const companies = new Set(visits.map((visit) => visit.crawler_company));
    const pages = new Set(visits.map((visit) => visit.page_url));
    const latestVisit = visits[0]?.visited_at;

    return {
      total: visits.length,
      companies: companies.size,
      pages: pages.size,
      latestVisit,
    };
  }, [visits]);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Link href="/admin/ceo" className="text-sm text-slate-400 transition-colors hover:text-white">
            Back to admin
          </Link>
          <span className="text-xl font-bold text-blue-400">AI Crawlers</span>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-400">
              GEO telemetry
            </p>
            <h1 className="text-3xl font-bold">AI Crawler Visits</h1>
            <p className="mt-2 max-w-2xl text-slate-400">
              Track which AI crawlers visit RivalEdge and which pages they inspect most often.
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 transition-colors hover:bg-slate-800"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <StatCard icon={Bot} label="Tracked visits" value={String(stats.total)} />
          <StatCard icon={Globe2} label="AI companies" value={String(stats.companies)} />
          <StatCard icon={ExternalLink} label="Pages visited" value={String(stats.pages)} />
          <StatCard
            icon={Clock}
            label="Latest visit"
            value={stats.latestVisit ? new Date(stats.latestVisit).toLocaleDateString() : 'None yet'}
          />
        </div>

        <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 px-5 py-4">
            <h2 className="font-semibold">Recent crawler activity</h2>
          </div>

          {loading ? (
            <div className="px-5 py-12 text-center text-slate-400">Loading crawler visits...</div>
          ) : error ? (
            <div className="px-5 py-12 text-center text-red-300">{error}</div>
          ) : visits.length === 0 ? (
            <div className="px-5 py-12 text-center text-slate-400">
              No AI crawler visits have been recorded yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-left text-slate-400">
                    <th className="px-5 py-3 font-medium">Crawler</th>
                    <th className="px-5 py-3 font-medium">Company</th>
                    <th className="px-5 py-3 font-medium">Page</th>
                    <th className="px-5 py-3 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {visits.map((visit) => (
                    <tr key={visit.id} className="border-b border-slate-800/70 last:border-0">
                      <td className="px-5 py-3 text-white">{visit.crawler_name}</td>
                      <td className="px-5 py-3 text-slate-300">{visit.crawler_company}</td>
                      <td className="max-w-md truncate px-5 py-3 text-blue-300" title={visit.page_url}>
                        {visit.page_url}
                      </td>
                      <td className="px-5 py-3 text-slate-400">
                        {new Date(visit.visited_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/10">
        <Icon className="h-5 w-5 text-blue-400" />
      </div>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}
