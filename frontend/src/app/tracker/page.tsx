'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ClipboardListIcon, TrashIcon, Loader2, ChevronDownIcon } from 'lucide-react'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { appsApi } from '@/lib/api'
import { cn, applicationStatusBadge, sponsorshipBadge, timeAgo } from '@/lib/utils'
import type { ApplicationStatus } from '@/types'

const STATUS_OPTIONS: ApplicationStatus[] = [
  'saved', 'applied', 'interviewing', 'offer', 'rejected', 'withdrawn',
]

const TAB_FILTERS: { value: string; label: string }[] = [
  { value: '', label: 'All' },
  { value: 'saved', label: 'Saved' },
  { value: 'applied', label: 'Applied' },
  { value: 'interviewing', label: 'Interviewing' },
  { value: 'offer', label: 'Offers' },
  { value: 'rejected', label: 'Rejected' },
]

export default function TrackerPage() {
  const auth = useRequireAuth()
  const qc = useQueryClient()
  const [activeTab, setActiveTab] = useState('')

  const { data: apps, isLoading } = useQuery({
    queryKey: ['applications', activeTab],
    queryFn: () => appsApi.list(activeTab || undefined),
    enabled: auth,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      appsApi.update(id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => appsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })

  if (!auth) return null

  return (
    <AppLayout>
      <div className="p-8 max-w-5xl mx-auto space-y-5 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Application Tracker</h1>
          <p className="text-sm text-slate-500 mt-0.5">{apps?.length ?? 0} applications tracked</p>
        </div>

        {/* Status tabs */}
        <div className="flex gap-1 bg-white border border-slate-200 rounded-lg p-1 w-fit">
          {TAB_FILTERS.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setActiveTab(value)}
              className={cn(
                'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
                activeTab === value
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              )}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-14 skeleton rounded-xl" />
            ))}
          </div>
        ) : apps?.length === 0 ? (
          <div className="card py-16 text-center text-slate-400">
            <ClipboardListIcon className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm font-medium">No applications yet</p>
            <p className="text-xs mt-1">Save jobs from the <Link href="/jobs" className="text-brand-600 hover:underline">Jobs page</Link></p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Job</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Sponsorship</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Updated</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {apps?.map((app) => {
                  const badge = applicationStatusBadge(app.status)
                  const sponsor = sponsorshipBadge(app.job?.sponsorship_status ?? null)
                  return (
                    <tr key={app.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-4 py-3">
                        <Link href={`/jobs/${app.job_id}`} className="hover:text-brand-600 transition-colors">
                          <p className="font-medium text-slate-900 truncate max-w-[240px]">
                            {app.job?.title || `Job #${app.job_id}`}
                          </p>
                          <p className="text-xs text-slate-500">{app.job?.company}</p>
                        </Link>
                      </td>
                      <td className="px-4 py-3">
                        <span className={cn('badge text-[10px]', sponsor.className)}>{sponsor.label}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="relative inline-block">
                          <select
                            value={app.status}
                            onChange={(e) => updateMutation.mutate({ id: app.id, status: e.target.value })}
                            className={cn(
                              'appearance-none text-xs font-medium px-2 py-1 pr-6 rounded-md border cursor-pointer',
                              badge.className
                            )}
                          >
                            {STATUS_OPTIONS.map((s) => (
                              <option key={s} value={s}>{applicationStatusBadge(s).label}</option>
                            ))}
                          </select>
                          <ChevronDownIcon className="absolute right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 pointer-events-none opacity-60" />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400">
                        {timeAgo(app.last_updated)}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => deleteMutation.mutate(app.id)}
                          disabled={deleteMutation.isPending}
                          className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                        >
                          {deleteMutation.isPending
                            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            : <TrashIcon className="w-3.5 h-3.5" />}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
