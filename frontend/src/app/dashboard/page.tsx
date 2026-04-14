'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  BriefcaseIcon, SearchIcon, TrendingUpIcon, ShieldCheckIcon,
  RefreshCwIcon, ClipboardListIcon, BarChart2Icon, Loader2,
} from 'lucide-react'
import { AppLayout } from '@/components/layout/AppLayout'
import { StatCard } from '@/components/dashboard/StatCard'
import { JobCard } from '@/components/jobs/JobCard'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { dashboardApi, jobsApi } from '@/lib/api'
import { cn } from '@/lib/utils'

export default function DashboardPage() {
  const auth = useRequireAuth()
  const qc = useQueryClient()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
    enabled: auth,
    refetchInterval: 60_000,
  })

  const ingestMutation = useMutation({
    mutationFn: jobsApi.ingest,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  if (!auth) return null

  const appsByStatus = stats?.applications_by_status ?? {}

  return (
    <AppLayout>
      <div className="p-8 space-y-6 max-w-6xl mx-auto animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-500 mt-0.5">Your job search at a glance</p>
          </div>
          <button
            onClick={() => ingestMutation.mutate()}
            disabled={ingestMutation.isPending}
            className="btn-primary"
          >
            {ingestMutation.isPending
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <RefreshCwIcon className="w-4 h-4" />}
            {ingestMutation.isPending ? 'Fetching jobs…' : 'Fetch New Jobs'}
          </button>
        </div>

        {/* Ingest result toast */}
        {ingestMutation.isSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 animate-fade-in">
            ✓ {ingestMutation.data.message} — {ingestMutation.data.new_jobs} new jobs,{' '}
            {ingestMutation.data.scored} scored.
          </div>
        )}

        {/* Stat cards */}
        {isLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="card px-5 py-4 h-24 skeleton" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Jobs Ingested"
              value={stats?.total_jobs_ingested ?? 0}
              subtitle={`${stats?.jobs_scored_today ?? 0} scored today`}
              icon={BriefcaseIcon}
            />
            <StatCard
              title="Top Match Score"
              value={`${stats?.top_matches[0]?.score?.toFixed(0) ?? '—'}`}
              subtitle="Best match today"
              icon={TrendingUpIcon}
              iconColor="text-emerald-600"
              iconBg="bg-emerald-50"
            />
            <StatCard
              title="Avg Match Score"
              value={`${stats?.avg_match_score ?? 0}`}
              subtitle="Across all scored jobs"
              icon={BarChart2Icon}
              iconColor="text-amber-600"
              iconBg="bg-amber-50"
            />
            <StatCard
              title="Sponsor-Eligible"
              value={stats?.sponsorship_eligible ?? 0}
              subtitle="H1B / transfer available"
              icon={ShieldCheckIcon}
              iconColor="text-teal-600"
              iconBg="bg-teal-50"
            />
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Top matches */}
          <div className="lg:col-span-2 space-y-3">
            <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <SearchIcon className="w-4 h-4 text-brand-500" />
              Top Matches
            </h2>
            {isLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-20 skeleton rounded-xl" />
                ))}
              </div>
            ) : stats?.top_matches.length === 0 ? (
              <div className="card px-5 py-8 text-center text-slate-400">
                <BriefcaseIcon className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p className="text-sm">No jobs scored yet.</p>
                <p className="text-xs mt-1">Click &quot;Fetch New Jobs&quot; to get started.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {stats?.top_matches.map((job) => (
                  <JobCard key={job.id} job={job} compact />
                ))}
              </div>
            )}
          </div>

          {/* Application pipeline */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <ClipboardListIcon className="w-4 h-4 text-brand-500" />
              Application Pipeline
            </h2>
            <div className="card px-5 py-4 space-y-3">
              {[
                { key: 'saved',        label: 'Saved',        color: 'bg-slate-400' },
                { key: 'applied',      label: 'Applied',      color: 'bg-brand-500' },
                { key: 'interviewing', label: 'Interviewing', color: 'bg-amber-500' },
                { key: 'offer',        label: 'Offer',        color: 'bg-emerald-500' },
                { key: 'rejected',     label: 'Rejected',     color: 'bg-red-400' },
              ].map(({ key, label, color }) => {
                const count = (appsByStatus as Record<string, number>)[key] ?? 0
                const total = stats?.total_applications || 1
                const pct = (count / total) * 100
                return (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-600">{label}</span>
                      <span className="font-medium text-slate-900">{count}</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={cn('h-full rounded-full transition-all duration-500', color)}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
              <div className="pt-2 border-t border-slate-100 flex justify-between text-xs">
                <span className="text-slate-500">Total</span>
                <span className="font-semibold text-slate-900">{stats?.total_applications ?? 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
