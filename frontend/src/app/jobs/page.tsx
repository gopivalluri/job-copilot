'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { SearchIcon, FilterIcon, RefreshCwIcon, Loader2, PlusIcon } from 'lucide-react'
import { AppLayout } from '@/components/layout/AppLayout'
import { JobCard } from '@/components/jobs/JobCard'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { jobsApi } from '@/lib/api'
import { cn } from '@/lib/utils'

const WORK_MODES = [
  { value: '', label: 'All modes' },
  { value: 'remote', label: '🌐 Remote' },
  { value: 'hybrid', label: '⚡ Hybrid' },
  { value: 'onsite', label: '🏢 On-site' },
]

export default function JobsPage() {
  const auth = useRequireAuth()
  const qc = useQueryClient()

  const [workMode, setWorkMode] = useState('')
  const [sponsorOnly, setSponsorOnly] = useState(false)
  const [minScore, setMinScore] = useState<number | undefined>()
  const [includeFiltered, setIncludeFiltered] = useState(false)
  const [search, setSearch] = useState('')

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs', { workMode, sponsorOnly, minScore, includeFiltered }],
    queryFn: () => jobsApi.list({
      work_mode: workMode || undefined,
      sponsorship_only: sponsorOnly,
      min_score: minScore,
      include_filtered: includeFiltered,
      limit: 100,
    }),
    enabled: auth,
  })

  const ingestMutation = useMutation({
    mutationFn: jobsApi.ingest,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const filtered = jobs?.filter((j) =>
    !search || j.title.toLowerCase().includes(search.toLowerCase()) ||
    j.company.toLowerCase().includes(search.toLowerCase())
  ) ?? []

  if (!auth) return null

  return (
    <AppLayout>
      <div className="p-8 space-y-5 max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Jobs</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {jobs?.length ?? 0} jobs • sorted by match score
            </p>
          </div>
          <button
            onClick={() => ingestMutation.mutate()}
            disabled={ingestMutation.isPending}
            className="btn-primary"
          >
            {ingestMutation.isPending
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <RefreshCwIcon className="w-4 h-4" />}
            Fetch Jobs
          </button>
        </div>

        {/* Filters bar */}
        <div className="card px-4 py-3 flex flex-wrap items-center gap-3">
          <FilterIcon className="w-4 h-4 text-slate-400 shrink-0" />

          {/* Search */}
          <div className="relative flex-1 min-w-[180px]">
            <SearchIcon className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search title or company…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-8 py-1.5 text-xs"
            />
          </div>

          {/* Work mode */}
          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="input py-1.5 text-xs w-36"
          >
            {WORK_MODES.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>

          {/* Min score */}
          <select
            value={minScore ?? ''}
            onChange={(e) => setMinScore(e.target.value ? Number(e.target.value) : undefined)}
            className="input py-1.5 text-xs w-36"
          >
            <option value="">Any score</option>
            <option value="40">Score ≥ 40</option>
            <option value="60">Score ≥ 60</option>
            <option value="75">Score ≥ 75</option>
            <option value="85">Score ≥ 85</option>
          </select>

          {/* Toggle filters */}
          <label className="flex items-center gap-1.5 text-xs text-slate-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={sponsorOnly}
              onChange={(e) => setSponsorOnly(e.target.checked)}
              className="rounded border-slate-300 text-brand-600"
            />
            H1B only
          </label>

          <label className="flex items-center gap-1.5 text-xs text-slate-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={includeFiltered}
              onChange={(e) => setIncludeFiltered(e.target.checked)}
              className="rounded border-slate-300 text-brand-600"
            />
            Show filtered
          </label>
        </div>

        {/* Ingest success */}
        {ingestMutation.isSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700">
            ✓ {ingestMutation.data.new_jobs} new jobs fetched and scored.
          </div>
        )}

        {/* Job list */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-24 skeleton rounded-xl" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="card py-16 text-center text-slate-400">
            <SearchIcon className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm font-medium">No jobs match your filters</p>
            <p className="text-xs mt-1">Try adjusting filters or fetching new jobs</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
