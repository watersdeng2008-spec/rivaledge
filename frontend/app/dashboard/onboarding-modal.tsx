'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';
import { Loader2, Building2, ChevronRight } from 'lucide-react';

const INDUSTRIES = [
  'E-commerce / Retail',
  'SaaS / Software',
  'Marketing / Agency',
  'Healthcare / Telehealth',
  'Finance / Fintech',
  'Education / EdTech',
  'Real Estate',
  'Food & Beverage',
  'Fashion / Apparel',
  'Manufacturing',
  'Consulting / Services',
  'Other',
];

interface OnboardingModalProps {
  onComplete: () => void;
}

export function OnboardingModal({ onComplete }: OnboardingModalProps) {
  const { getToken } = useAuth();
  const [companyName, setCompanyName] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  const [industry, setIndustry] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!companyName.trim()) return;
    setSaving(true);
    try {
      const token = await getToken();
      await apiRequest('/api/users/onboarding', {
        method: 'POST',
        token: token || undefined,
        body: JSON.stringify({
          company_name: companyName.trim(),
          business_description: businessDescription.trim(),
          industry,
        }),
      });
    } catch {
      // Don't block on failure — onboarding is optional
    } finally {
      setSaving(false);
      onComplete();
    }
  };

  const handleSkip = () => onComplete();

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-8 shadow-2xl">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-blue-600/20 rounded-xl flex items-center justify-center">
            <Building2 className="w-5 h-5 text-blue-400" />
          </div>
          <h2 className="text-xl font-bold">Tell us about your business</h2>
        </div>
        <p className="text-slate-400 text-sm mb-6">
          This helps us personalize your competitive intelligence reports. Takes 30 seconds.
        </p>

        <div className="space-y-5">
          {/* Company name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Company name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Acme Store, Widget Co."
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>

          {/* Business description */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              What does your business do?
            </label>
            <textarea
              value={businessDescription}
              onChange={(e) => setBusinessDescription(e.target.value)}
              placeholder="Tell us about your business — what you sell, who your customers are, what markets you operate in, and what makes you different. The more you share, the more relevant your competitive analysis will be."
              rows={5}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm resize-none"
            />
            <p className="text-slate-600 text-xs mt-1">
              There's no wrong answer — the more context, the sharper your insights.
            </p>
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Industry
            </label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 text-sm"
            >
              <option value="">Select your industry...</option>
              {INDUSTRIES.map((i) => (
                <option key={i} value={i}>{i}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3 mt-7">
          <button
            onClick={handleSubmit}
            disabled={!companyName.trim() || saving}
            className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                Continue to dashboard
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
          <button
            onClick={handleSkip}
            className="text-slate-500 hover:text-slate-300 text-sm px-4 py-3 transition-colors"
          >
            Skip
          </button>
        </div>
      </div>
    </div>
  );
}
