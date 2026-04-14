'use client'

import Link from 'next/link'
import { BuildingIcon, MapPinIcon, CalendarIcon } from 'lucide-react'
import type { JobWithScore } from '@/types'
import { cn, formatSalary, sponsorshipBadge, workModeBadge, timeAgo } from '@/lib/utils'
import { ScoreBadge } from '@/components/ui/ScoreBadge'

interface JobCardProps {
  job: JobWithScore
  compact?: boolean
}

export function JobCard({ job, compact = false }: JobCardProps) {
  const sponsor = sponsorshipBadge(job.sponsorship_status)
  const mode = workModeBadge(job.work_mode)

  if (job.is_filtered_out) {
    return (
      <div className="card px-4 py-3 opacity-50 border-dashed">
        <div className="flex items-start gap-3">
          <ScoreBadge score={null} size="sm" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-slate-500 line-through truncate">{job.title}</p>
            <p className="text-xs text-slate-400">{job.company}</p>
            {job.filter_reason && (
              <p className="text-xs text-red-400 mt-1">Filtered: {job.filter_reason}</p>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <Link href={`/jobs/${job.id}`} className="block">
      <div className={cn(
        'card px-4 hover:shadow-card-hover transition-shadow duration-150 cursor-pointer',
        compact ? 'py-3' : 'py-4'
      )}>
        <div className="flex items-start gap-3">
          {/* Score ring */}
          <ScoreBadge score={job.score} size={compact ? 'sm' : 'md'} />

          {/* Job info */}
          <div className="min-w-0 flex-1 space-y-1.5">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <h3 className={cn(
                  'font-semibold text-slate-900 truncate',
                  compact ? 'text-sm' : 'text-base'
                )}>
                  {job.title}
                </h3>
                <div className="flex items-center gap-3 text-xs text-slate-500 mt-0.5">
                  <span className="flex items-center gap-1">
                    <BuildingIcon className="w-3 h-3" /> {job.company}
                  </span>
                  {job.location && (
                    <span className="flex items-center gap-1">
                      <MapPinIcon className="w-3 h-3" /> {job.location}
                    </span>
                  )}
                </div>
              </div>
              <div className="text-xs text-slate-400 whitespace-nowrap flex items-center gap-1">
                <CalendarIcon className="w-3 h-3" />
                {timeAgo(job.ingested_at)}
              </div>
            </div>

            {/* Badges */}
            {!compact && (
              <div className="flex flex-wrap gap-1.5">
                <span className={cn('badge', sponsor.className)}>{sponsor.label}</span>
                <span className={cn('badge', mode.className)}>{mode.label}</span>
                {job.employment_type && (
                  <span className="badge bg-slate-50 text-slate-600 border-slate-200">
                    {job.employment_type.replace('_', '-')}
                  </span>
                )}
                {(job.salary_min || job.salary_max) && (
                  <span className="badge bg-slate-50 text-slate-600 border-slate-200">
                    {formatSalary(job.salary_min, job.salary_max)}
                  </span>
                )}
              </div>
            )}

            {/* Skills preview */}
            {!compact && job.skills_required.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {job.skills_required.slice(0, 5).map((skill) => (
                  <span key={skill} className="px-1.5 py-0.5 bg-brand-50 text-brand-700 text-[10px] rounded font-medium">
                    {skill}
                  </span>
                ))}
                {job.skills_required.length > 5 && (
                  <span className="px-1.5 py-0.5 text-slate-400 text-[10px]">
                    +{job.skills_required.length - 5} more
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
