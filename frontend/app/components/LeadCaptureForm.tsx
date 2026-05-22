'use client';

import { useState } from 'react';
import { ArrowRight, Check, Loader2 } from 'lucide-react';

interface LeadCaptureFormProps {
  source: 'homepage' | 'pricing' | 'exit_intent' | 'demo';
  variant?: 'hero' | 'inline' | 'compact';
  title?: string;
  subtitle?: string;
  buttonText?: string;
  onSuccess?: () => void;
}

export default function LeadCaptureForm({
  source,
  variant = 'inline',
  title,
  subtitle,
  buttonText = 'See what they\'re doing →',
  onSuccess,
}: LeadCaptureFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    companyName: '',
    companyUrl: '',
    competitorUrl: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://rivaledge-production.up.railway.app/api/leads/capture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          company_name: formData.companyName || null,
          company_url: formData.companyUrl || null,
          competitor_url: formData.competitorUrl || null,
          capture_source: source,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || data.message || 'Something went wrong');
      }

      setSuccess(true);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 text-center">
        <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check className="w-6 h-6 text-green-400" />
        </div>
        <h3 className="text-lg font-semibold text-green-400 mb-2">You&apos;re in!</h3>
        <p className="text-slate-300 text-sm">
          Check your email for a personalized competitor snapshot.
        </p>
      </div>
    );
  }

  const inputClasses =
    'w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-sm';

  if (variant === 'hero') {
    return (
      <div className="w-full max-w-lg mx-auto">
        {title && <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>}
        {subtitle && <p className="text-slate-400 text-sm mb-6">{subtitle}</p>}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Your name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={inputClasses}
            />
            <input
              type="email"
              placeholder="Work email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className={inputClasses}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Company name"
              value={formData.companyName}
              onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
              className={inputClasses}
            />
            <input
              type="url"
              placeholder="Your website (optional)"
              value={formData.companyUrl}
              onChange={(e) => setFormData({ ...formData, companyUrl: e.target.value })}
              className={inputClasses}
            />
          </div>

          <div className="relative">
            <input
              type="url"
              placeholder="Competitor URL to track (e.g., https://competitor.com)"
              required
              value={formData.competitorUrl}
              onChange={(e) => setFormData({ ...formData, competitorUrl: e.target.value })}
              className={inputClasses}
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white py-3.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-600/20 hover:shadow-blue-600/40 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                {buttonText}
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          <p className="text-slate-500 text-xs text-center">
            No spam. Unsubscribe anytime. We never share your data.
          </p>
        </form>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
        <input
          type="email"
          placeholder="Work email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg font-semibold transition-colors disabled:opacity-50 text-sm whitespace-nowrap"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : buttonText}
        </button>
      </form>
    );
  }

  // Inline variant (default)
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
      {title && <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>}
      {subtitle && <p className="text-slate-400 text-sm mb-4">{subtitle}</p>}

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input
            type="text"
            placeholder="Your name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className={inputClasses}
          />
          <input
            type="email"
            placeholder="Work email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className={inputClasses}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input
            type="text"
            placeholder="Company name"
            value={formData.companyName}
            onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
            className={inputClasses}
          />
          <input
            type="url"
            placeholder="Your website (optional)"
            value={formData.companyUrl}
            onChange={(e) => setFormData({ ...formData, companyUrl: e.target.value })}
            className={inputClasses}
          />
        </div>

        <input
          type="url"
          placeholder="Competitor URL to track (e.g., https://competitor.com)"
          required
          value={formData.competitorUrl}
          onChange={(e) => setFormData({ ...formData, competitorUrl: e.target.value })}
          className={inputClasses}
        />

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              {buttonText}
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
