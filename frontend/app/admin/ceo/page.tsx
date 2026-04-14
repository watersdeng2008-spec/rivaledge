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
