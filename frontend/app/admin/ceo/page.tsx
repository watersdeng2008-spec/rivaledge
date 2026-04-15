"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://rivaledge-production.up.railway.app";

interface User {
  id: string;
  email: string;
  company_name?: string;
  plan: string;
  created_at: string;
  onboarding_completed?: boolean;
}

interface SalesAgentRun {
  run_id: string;
  started_at: string;
  companies_processed: number;
  decision_makers_found: number;
  emails_generated: number;
  emails_added_to_instantly: number;
}

interface DashboardData {
  registrations: {
    total_registrations: number;
    completed_signups: number;
    incomplete_signups: number;
    trial_users: number;
    paying_customers: number;
    conversion_rate: number;
    period_days: number;
  };
  recent_signups: User[];
  incomplete_signups: User[];
  revenue_metrics: {
    mrr: number;
    mrr_formatted: string;
    active_subscriptions: number;
    new_subscriptions_period: number;
    new_revenue_period: number;
    new_revenue_formatted: string;
  };
  sales_pipeline: {
    total_leads: number;
    by_status: Record<string, number>;
    recent_emails: number;
  };
  sales_agent?: {
    recent_runs: SalesAgentRun[];
    today_stats: {
      companies: number;
      decision_makers: number;
      emails_sent: number;
    };
  };
  daily_report?: {
    date: string;
    new_signups: number;
    new_leads: number;
    emails_sent: number;
    email_replies: number;
    hot_leads: number;
  };
}

export default function CEODashboard() {
  const { getToken } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const token = await getToken();
        const response = await fetch(`${API_URL}/ceo/dashboard`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 403) {
            setError("Admin access required");
          } else {
            setError(`Failed to load dashboard: ${response.status}`);
          }
          setLoading(false);
          return;
        }

        const dashboardData = await response.json();
        setData(dashboardData);
        setLoading(false);
      } catch (err) {
        setError("Failed to load dashboard data");
        setLoading(false);
      }
    }

    fetchDashboard();
  }, [getToken]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">CEO Dashboard</h1>
          <div className="text-gray-600">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">CEO Dashboard</h1>
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">CEO Dashboard</h1>
          <div className="text-gray-600">No data available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">🎯 CEO Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={data.registrations.total_registrations}
            subtitle={`${data.registrations.period_days} days`}
          />
          <StatCard
            title="Completed Signups"
            value={data.registrations.completed_signups}
            subtitle={`${data.registrations.incomplete_signups} incomplete`}
          />
          <StatCard
            title="Paying Customers"
            value={data.registrations.paying_customers}
            subtitle={`${data.registrations.conversion_rate}% conversion`}
          />
          <StatCard
            title="MRR"
            value={data.revenue_metrics.mrr_formatted}
            subtitle={`${data.revenue_metrics.active_subscriptions} active subs`}
          />
        </div>

        {/* Revenue & Pipeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue Metrics</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Monthly Recurring Revenue</span>
                <span className="font-medium">{data.revenue_metrics.mrr_formatted}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Subscriptions</span>
                <span className="font-medium">{data.revenue_metrics.active_subscriptions}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">New Subscriptions (period)</span>
                <span className="font-medium">{data.revenue_metrics.new_subscriptions_period}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">New Revenue (period)</span>
                <span className="font-medium">{data.revenue_metrics.new_revenue_formatted}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Sales Pipeline</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Leads</span>
                <span className="font-medium">{data.sales_pipeline.total_leads}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Recent Emails</span>
                <span className="font-medium">{data.sales_pipeline.recent_emails}</span>
              </div>
              {Object.entries(data.sales_pipeline.by_status).map(([status, count]) => (
                <div key={status} className="flex justify-between">
                  <span className="text-gray-600 capitalize">{status}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Signups */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Signups</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {data.recent_signups.length === 0 ? (
              <div className="px-6 py-4 text-gray-500">No recent signups</div>
            ) : (
              data.recent_signups.map((user) => (
                <div key={user.id} className="px-6 py-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900">{user.email}</div>
                      <div className="text-sm text-gray-500">
                        {user.company_name || "No company"} • {user.plan}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      {new Date(user.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Sales Agent Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">🤖 Sales Agent</h2>
            <div className="flex gap-2">
              <button
                onClick={downloadLinkedInCSV}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                📥 Download LinkedIn CSV
              </button>
              <button
                onClick={triggerSalesAgent}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
              >
                ▶️ Run Now
              </button>
            </div>
          </div>
          
          {data.sales_agent ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <StatCard
                title="Today's Companies"
                value={data.sales_agent.today_stats.companies}
                subtitle="Processed"
              />
              <StatCard
                title="Decision Makers"
                value={data.sales_agent.today_stats.decision_makers}
                subtitle="Identified"
              />
              <StatCard
                title="Emails Sent"
                value={data.sales_agent.today_stats.emails_sent}
                subtitle="To Instantly"
              />
              <StatCard
                title="Status"
                value="✅ Active"
                subtitle="Daily at 9 AM"
              />
            </div>
          ) : (
            <div className="text-gray-500">Sales agent data loading...</div>
          )}
        </div>

        {/* Daily Report */}
        {data.daily_report && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Yesterday's Report ({data.daily_report.date})</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <StatCard
                title="New Signups"
                value={data.daily_report.new_signups}
                subtitle="Users"
              />
              <StatCard
                title="New Leads"
                value={data.daily_report.new_leads}
                subtitle="Added"
              />
              <StatCard
                title="Emails Sent"
                value={data.daily_report.emails_sent}
                subtitle="Outreach"
              />
              <StatCard
                title="Replies"
                value={data.daily_report.email_replies}
                subtitle="Responses"
              />
              <StatCard
                title="Hot Leads"
                value={data.daily_report.hot_leads}
                subtitle="Priority"
              />
            </div>
          </div>
        )}

        {/* Incomplete Signups */}
        {data.incomplete_signups.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Incomplete Signups</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {data.incomplete_signups.map((user) => (
                <div key={user.id} className="px-6 py-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-gray-900">{user.email}</div>
                      <div className="text-sm text-gray-500">
                        Started {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <span className="px-2 py-1 text-xs font-medium text-yellow-700 bg-yellow-100 rounded">
                      Incomplete
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  async function downloadLinkedInCSV() {
    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/api/admin/sales-agent/linkedin-csv?days=7`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        alert("Failed to download CSV");
        return;
      }

      const data = await response.json();
      
      // Create and download CSV file
      const blob = new Blob([data.csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = data.filename || "linkedin_leads.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading CSV: " + err);
    }
  }

  async function triggerSalesAgent() {
    try {
      const token = await getToken();
      const response = await fetch(`${API_URL}/api/admin/sales-agent/run?target_count=3`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        alert("Failed to trigger sales agent");
        return;
      }

      const data = await response.json();
      alert(`Sales agent triggered! Processed ${data.processed} companies.`);
      
      // Refresh dashboard
      window.location.reload();
    } catch (err) {
      alert("Error triggering sales agent: " + err);
    }
  }
}

function StatCard({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string | number;
  subtitle: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">
        {title}
      </div>
      <div className="mt-2 text-3xl font-bold text-gray-900">{value}</div>
      <div className="mt-1 text-sm text-gray-500">{subtitle}</div>
    </div>
  );
}
