'use client';

import { useEffect, useState, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth, useUser, SignOutButton } from '@clerk/nextjs';
import Link from 'next/link';
import { Plus, Zap, RefreshCw, Crown, Loader2, X } from 'lucide-react';
import { apiRequest, ApiError } from '@/lib/api';

interface Competitor {
  id: string;
  name: string;
  url: string;
  last_scraped?: string;
  created_at?: string;
}

interface BillingStatus {
  plan: string;
  competitor_count: number;
  competitor_limit: number;
  status: string;
}

function DashboardContent() {
  const { getToken } = useAuth();
  const { user } = useUser();
  const searchParams = useSearchParams();
  const isCheckoutSuccess = searchParams.get('checkout') === 'success';

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [billing, setBilling] = useState<BillingStatus | null>(null);
  const [loadingCompetitors, setLoadingCompetitors] = useState(true);
  const [loadingBilling, setLoadingBilling] = useState(true);
  const [newUrl, setNewUrl] = useState('');
  const [addingCompetitor, setAddingCompetitor] = useState(false);
  const [generatingDigest, setGeneratingDigest] = useState(false);
  const [scrapingAll, setScrapingAll] = useState(false);
  const [upgradingPlan, setUpgradingPlan] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(
    isCheckoutSuccess ? '🎉 Welcome to RivalEdge! Your plan is now active.' : null
  );

  const fetchCompetitors = useCallback(async () => {
    try {
      const token = await getToken();
      const data = await apiRequest<Competitor[]>('/api/competitors', { token: token || undefined });
      setCompetitors(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load competitors');
    } finally {
      setLoadingCompetitors(false);
    }
  }, [getToken]);

  const fetchBilling = useCallback(async () => {
    try {
      const token = await getToken();
      const data = await apiRequest<BillingStatus>('/api/billing/status', { token: token || undefined });
      setBilling(data);
    } catch {
      // Non-critical — ignore silently
    } finally {
      setLoadingBilling(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchCompetitors();
    fetchBilling();
  }, [fetchCompetitors, fetchBilling]);

  const handleAddCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUrl.trim()) return;
    setAddingCompetitor(true);
    setError(null);
    try {
      const token = await getToken();
      const competitor = await apiRequest<Competitor>('/api/competitors', {
        method: 'POST',
        body: JSON.stringify({ url: newUrl.trim() }),
        token: token || undefined,
      });
      setCompetitors((prev) => [...prev, competitor]);
      setNewUrl('');
      setSuccessMsg('Competitor added successfully!');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add competitor');
    } finally {
      setAddingCompetitor(false);
    }
  };

  const handleGenerateDigest = async () => {
    setGeneratingDigest(true);
    setError(null);
    try {
      const token = await getToken();
      await apiRequest('/api/digest/generate', {
        method: 'POST',
        token: token || undefined,
      });
      setSuccessMsg('Digest generation started! Check your email shortly.');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to generate digest');
    } finally {
      setGeneratingDigest(false);
    }
  };

  const handleScrapeAll = async () => {
    setScrapingAll(true);
    setError(null);
    try {
      const token = await getToken();
      await apiRequest('/api/jobs/scrape-all', {
        method: 'POST',
        token: token || undefined,
      });
      setSuccessMsg('Scrape jobs queued for all competitors!');
      setTimeout(fetchCompetitors, 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start scrape');
    } finally {
      setScrapingAll(false);
    }
  };

  const handleUpgrade = async () => {
    setUpgradingPlan(true);
    setError(null);
    try {
      const token = await getToken();
      const data = await apiRequest<{ checkout_url: string }>('/api/billing/checkout', {
        method: 'POST',
        body: JSON.stringify({ plan: 'pro' }),
        token: token || undefined,
      });
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError('Failed to start checkout');
      }
    } finally {
      setUpgradingPlan(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold text-blue-400">RivalEdge</span>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 text-sm">Dashboard</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-400 text-sm">{user?.primaryEmailAddress?.emailAddress}</span>
            <SignOutButton>
              <button className="text-slate-500 hover:text-white text-sm transition-colors">
                Sign out
              </button>
            </SignOutButton>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Success / Error banners */}
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

        {/* Plan status bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl px-6 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {loadingBilling ? (
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading plan info...
            </div>
          ) : billing ? (
            <div className="flex items-center gap-6">
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Plan</span>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="font-semibold capitalize">{billing.plan}</span>
                  {billing.plan === 'pro' && <Crown className="w-4 h-4 text-yellow-400" />}
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase tracking-wider">Competitors</span>
                <div className="font-semibold mt-0.5">
                  {billing.competitor_count} / {billing.competitor_limit}
                </div>
              </div>
            </div>
          ) : (
            <span className="text-slate-500 text-sm">Plan info unavailable</span>
          )}
          {billing?.plan !== 'pro' && (
            <button
              onClick={handleUpgrade}
              disabled={upgradingPlan}
              className="flex items-center gap-2 bg-yellow-500/10 hover:bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              <Crown className="w-4 h-4" />
              {upgradingPlan ? 'Redirecting...' : 'Upgrade to Pro'}
            </button>
          )}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Competitors — takes 2/3 */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Competitors</h2>
              <span className="text-slate-500 text-sm">{competitors.length} tracked</span>
            </div>

            {/* Add competitor form */}
            <form onSubmit={handleAddCompetitor} className="flex gap-3">
              <input
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://competitor.com"
                required
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
              <button
                type="submit"
                disabled={addingCompetitor}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                {addingCompetitor ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                Add
              </button>
            </form>

            {/* Competitor list */}
            {loadingCompetitors ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
              </div>
            ) : competitors.length === 0 ? (
              <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-xl">
                <p className="text-slate-500 text-sm mb-2">No competitors tracked yet</p>
                <p className="text-slate-600 text-xs">Add a competitor URL above to get started</p>
              </div>
            ) : (
              <div className="space-y-3">
                {competitors.map((c) => (
                  <div
                    key={c.id}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 flex items-center justify-between gap-4"
                  >
                    <div className="min-w-0">
                      <div className="font-medium truncate">{c.name || c.url}</div>
                      <div className="text-slate-500 text-xs truncate mt-0.5">{c.url}</div>
                      {c.last_scraped && (
                        <div className="text-slate-600 text-xs mt-1">
                          Last scraped: {new Date(c.last_scraped).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                    <Link
                      href={`/dashboard/competitors/${c.id}`}
                      className="flex-shrink-0 text-blue-400 hover:text-blue-300 text-sm transition-colors"
                    >
                      View changes →
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick actions sidebar */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Quick actions</h2>

            <button
              onClick={handleGenerateDigest}
              disabled={generatingDigest}
              className="w-full flex items-center gap-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white px-5 py-4 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 text-left"
            >
              {generatingDigest ? (
                <Loader2 className="w-5 h-5 animate-spin text-blue-400 flex-shrink-0" />
              ) : (
                <Zap className="w-5 h-5 text-blue-400 flex-shrink-0" />
              )}
              <div>
                <div className="font-medium">Generate digest</div>
                <div className="text-slate-500 text-xs mt-0.5">AI summary of recent changes</div>
              </div>
            </button>

            <button
              onClick={handleScrapeAll}
              disabled={scrapingAll}
              className="w-full flex items-center gap-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white px-5 py-4 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 text-left"
            >
              {scrapingAll ? (
                <Loader2 className="w-5 h-5 animate-spin text-blue-400 flex-shrink-0" />
              ) : (
                <RefreshCw className="w-5 h-5 text-blue-400 flex-shrink-0" />
              )}
              <div>
                <div className="font-medium">Scrape all</div>
                <div className="text-slate-500 text-xs mt-0.5">Refresh all competitor data</div>
              </div>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
