'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { apiRequest } from '@/lib/api';
import { MessageSquare, X, Send, Loader2 } from 'lucide-react';

const REACTIONS = [
  { emoji: '👍', label: 'Works great', value: 'positive' },
  { emoji: '🤔', label: 'Needs improvement', value: 'neutral' },
  { emoji: '💡', label: 'Feature idea', value: 'feature' },
];

export function FeedbackButton() {
  const { getToken } = useAuth();
  const [open, setOpen] = useState(false);
  const [reaction, setReaction] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!reaction) return;
    setSubmitting(true);
    try {
      const token = await getToken();
      await apiRequest('/api/feedback', {
        method: 'POST',
        token: token || undefined,
        body: JSON.stringify({ reaction, message, page: 'dashboard' }),
      });
      setSubmitted(true);
      setTimeout(() => {
        setOpen(false);
        setSubmitted(false);
        setReaction('');
        setMessage('');
      }, 2000);
    } catch {
      // Fail silently — don't block the user
      setSubmitted(true);
      setTimeout(() => {
        setOpen(false);
        setSubmitted(false);
        setReaction('');
        setMessage('');
      }, 2000);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-500 text-white px-4 py-3 rounded-full shadow-lg flex items-center gap-2 text-sm font-medium transition-colors z-40"
      >
        <MessageSquare className="w-4 h-4" />
        Feedback
      </button>

      {/* Modal */}
      {open && (
        <div className="fixed inset-0 bg-black/60 flex items-end sm:items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Share your feedback</h3>
              <button onClick={() => setOpen(false)} className="text-slate-500 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {submitted ? (
              <div className="text-center py-6">
                <div className="text-4xl mb-3">🙏</div>
                <p className="text-slate-300 font-medium">Thanks! Your feedback helps us improve.</p>
              </div>
            ) : (
              <>
                <p className="text-slate-400 text-sm mb-4">How is RivalEdge working for you?</p>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  {REACTIONS.map((r) => (
                    <button
                      key={r.value}
                      onClick={() => setReaction(r.value)}
                      className={`flex flex-col items-center gap-2 p-3 rounded-xl border text-sm transition-colors ${
                        reaction === r.value
                          ? 'border-blue-500 bg-blue-500/10 text-white'
                          : 'border-slate-700 hover:border-slate-500 text-slate-400'
                      }`}
                    >
                      <span className="text-2xl">{r.emoji}</span>
                      <span className="text-xs">{r.label}</span>
                    </button>
                  ))}
                </div>

                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Tell us more (optional)..."
                  rows={3}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 resize-none focus:outline-none focus:border-blue-500 mb-4"
                />

                <button
                  onClick={handleSubmit}
                  disabled={!reaction || submitting}
                  className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-colors"
                >
                  {submitting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Send feedback
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
