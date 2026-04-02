'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, FileText, Loader2, X, Clock } from 'lucide-react';
import { apiRequest } from '@/lib/api';

interface Competitor {
  id: string;
  name: string;
  url: string;
  description?: string;
  last_scraped?: string;
  created_at?: string;
}

interface Snapshot {
  id: string;
  scraped_at: string;
  diff_summary?: string;
  diff?: string;
}

export default function CompetitorDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const [competitor, setCompetitor] = useState<Competitor | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [scrapingNow, setScrapingNow] = useState(false);
  const [generatingCard, setGeneratingCard] = useState(false);
  const [battleCard, setBattleCard] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const token = await getToken();
      const [comp, snaps] = await Promise.all([
        apiRequest<Competitor>(`/api/competitors/${id}`, { token: token || undefined }),
        apiRequest<{snapshots: Snapshot[]} | Snapshot[]>(`/api/competitors/${id}/snapshots`, { token: token || undefined }).catch(() => []),
      ]);
      setCompetitor(comp);
      setSnapshots(Array.isArray(snaps) ? snaps : (snaps as {snapshots: Snapshot[]}).snapshots || []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load competitor');
    } finally {
      setLoading(false);
    }
  }, [getToken, id]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    fetchData();
  }, [fetchData, isLoaded, isSignedIn]);

  const handleScrapeNow = async () => {
    setScrapingNow(true);
    setError(null);
    try {
      const token = await getToken();
      await apiRequest(`/api/jobs/scrape/${id}`, {
        method: 'POST',
        token: token || undefined,
      });
      setSuccessMsg('Scrape job queued! Data will refresh shortly.');
      setTimeout(fetchData, 5000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start scrape');
    } finally {
      setScrapingNow(false);
    }
  };

  const handleGenerateBattleCard = async () => {
    setGeneratingCard(true);
    setError(null);
    setBattleCard(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ content: string; battle_card?: string }>('/api/digest/battle-card', {
        method: 'POST',
        body: JSON.stringify({ competitor_id: id }),
        token: token || undefined,
      });
      setBattleCard(data.content || data.battle_card || 'Battle card generated successfully.');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to generate battle card');
    } finally {
      setGeneratingCard(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
            <span className="text-slate-600">/</span>
            <Link href="/dashboard" className="text-slate-400 text-sm hover:text-white transition-colors">
              Dashboard
            </Link>
            <span className="text-slate-600">/</span>
            <span className="text-slate-300 text-sm truncate max-w-[200px]">
              {competitor?.name || competitor?.url || 'Competitor'}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to dashboard
        </Link>

        {successMsg && (
          <div className="bg-green-900/30 border border-green-700 text-green-300 px-4 py-3 rounded-lg flex items-center justify-between">
            <span className="text-sm">{successMsg}</span>
            <button onClick={() => setSuccessMsg(null)}><X className="w-4 h-4" /></button>
          </div>
        )}
        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg flex items-center justify-between">
            <span className="text-sm">{error}</span>
            <button onClick={() => setError(null)}><X className="w-4 h-4" /></button>
          </div>
        )}

        {/* Competitor profile */}
        {competitor ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold">{competitor.name || competitor.url}</h1>
                <a
                  href={competitor.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 text-sm mt-1 inline-block transition-colors"
                >
                  {competitor.url} ↗
                </a>
                {competitor.description && (
                  <p className="text-slate-400 text-sm mt-3 max-w-lg">{competitor.description}</p>
                )}
                {competitor.last_scraped && (
                  <div className="flex items-center gap-1.5 text-slate-500 text-xs mt-3">
                    <Clock className="w-3.5 h-3.5" />
                    Last scraped: {new Date(competitor.last_scraped).toLocaleString()}
                  </div>
                )}
              </div>
              <div className="flex gap-3 flex-shrink-0">
                <button
                  onClick={handleScrapeNow}
                  disabled={scrapingNow}
                  className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                >
                  {scrapingNow ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                  Scrape now
                </button>
                <button
                  onClick={handleGenerateBattleCard}
                  disabled={generatingCard}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                >
                  {generatingCard ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                  Generate battle card
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-400">
            Competitor not found.
          </div>
        )}

        {/* Battle card output */}
        {battleCard && (
          <div className="bg-slate-900 border border-blue-600/30 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Battle Card
            </h2>
            <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{battleCard}</div>
          </div>
        )}

        {/* Change timeline */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Change timeline</h2>
          {snapshots.length === 0 ? (
            <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-xl">
              <p className="text-slate-500 text-sm mb-2">No snapshots yet</p>
              <p className="text-slate-600 text-xs">Click &quot;Scrape now&quot; to capture the first snapshot</p>
            </div>
          ) : (
            <div className="space-y-4">
              {snapshots.map((snap, idx) => (
                <div key={snap.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2 text-sm text-slate-400">
                      <Clock className="w-4 h-4" />
                      {new Date(snap.scraped_at).toLocaleString()}
                    </div>
                    {idx === 0 && (
                      <span className="text-xs bg-blue-600/20 text-blue-400 border border-blue-600/30 px-2 py-0.5 rounded-full">
                        Latest
                      </span>
                    )}
                  </div>
                  {snap.diff_summary ? (
                    <p className="text-slate-300 text-sm">{snap.diff_summary}</p>
                  ) : snap.diff ? (
                    <pre className="text-slate-400 text-xs bg-slate-950 rounded-lg p-4 overflow-x-auto">
                      {snap.diff}
                    </pre>
                  ) : (
                    <p className="text-slate-500 text-sm">Snapshot captured — no changes detected.</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
