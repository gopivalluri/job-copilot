'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeftIcon, BuildingIcon, MapPinIcon, ExternalLinkIcon,
  WandSparklesIcon, BookmarkPlusIcon, Loader2, CheckIcon, CopyIcon,
} from 'lucide-react'
import { AppLayout } from '@/components/layout/AppLayout'
import { ScoreBadge, ScoreBar } from '@/components/ui/ScoreBadge'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { jobsApi, appsApi } from '@/lib/api'
import { cn, formatSalary, sponsorshipBadge, workModeBadge } from '@/lib/utils'

export default function JobDetailPage() {
  const auth = useRequireAuth()
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const qc = useQueryClient()
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.get(Number(id)),
    enabled: auth && !!id,
  })

  const tailorMutation = useMutation({
    mutationFn: () => jobsApi.tailor(Number(id), true),
  })

  const saveMutation = useMutation({
    mutationFn: () => appsApi.create(Number(id)),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })

  const handleCopy = async (text: string, section: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedSection(section)
    setTimeout(() => setCopiedSection(null), 2000)
  }

  if (!auth) return null

  const sponsor = sponsorshipBadge(job?.sponsorship_status ?? null)
  const mode = workModeBadge(job?.work_mode ?? null)

  return (
    <AppLayout>
      <div className="p-8 max-w-4xl mx-auto space-y-6 animate-fade-in">
        {/* Back */}
        <button onClick={() => router.back()} className="btn-secondary text-xs">
          <ArrowLeftIcon className="w-3.5 h-3.5" /> Back to jobs
        </button>

        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => <div key={i} className="h-20 skeleton rounded-xl" />)}
          </div>
        ) : job ? (
          <>
            {/* Header card */}
            <div className="card px-6 py-5 space-y-4">
              <div className="flex items-start gap-4">
                <ScoreBadge score={job.score} size="lg" />
                <div className="flex-1 min-w-0 space-y-2">
                  <div>
                    <h1 className="text-xl font-bold text-slate-900">{job.title}</h1>
                    <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                      <span className="flex items-center gap-1.5"><BuildingIcon className="w-3.5 h-3.5" />{job.company}</span>
                      {job.location && <span className="flex items-center gap-1.5"><MapPinIcon className="w-3.5 h-3.5" />{job.location}</span>}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <span className={cn('badge', sponsor.className)}>{sponsor.label}</span>
                    <span className={cn('badge', mode.className)}>{mode.label}</span>
                    {job.employment_type && (
                      <span className="badge bg-slate-50 text-slate-600 border-slate-200">
                        {job.employment_type.replace('_', '-')}
                      </span>
                    )}
                    {(job.salary_min || job.salary_max) && (
                      <span className="badge bg-green-50 text-green-700 border-green-200">
                        💰 {formatSalary(job.salary_min, job.salary_max)}
                      </span>
                    )}
                    {job.experience_level && (
                      <span className="badge bg-purple-50 text-purple-700 border-purple-200">
                        {job.experience_level}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Score breakdown */}
              {job.score_details && (
                <div className="border-t border-slate-100 pt-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Match Score Breakdown</p>
                  <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                    <ScoreBar label="Title relevance" value={job.score_details.title} />
                    <ScoreBar label="Skills match" value={job.score_details.skills} />
                    <ScoreBar label="Sponsorship" value={job.score_details.sponsorship} />
                    <ScoreBar label="Employment type" value={job.score_details.employment} />
                    <ScoreBar label="Location fit" value={job.score_details.location} />
                    <ScoreBar label="Experience level" value={job.score_details.experience} />
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-1 border-t border-slate-100">
                <button
                  onClick={() => saveMutation.mutate()}
                  disabled={saveMutation.isPending || saveMutation.isSuccess}
                  className="btn-secondary text-xs"
                >
                  {saveMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> :
                   saveMutation.isSuccess ? <CheckIcon className="w-3.5 h-3.5 text-emerald-600" /> :
                   <BookmarkPlusIcon className="w-3.5 h-3.5" />}
                  {saveMutation.isSuccess ? 'Saved!' : 'Save Application'}
                </button>

                <button
                  onClick={() => tailorMutation.mutate()}
                  disabled={tailorMutation.isPending}
                  className="btn-primary text-xs"
                >
                  {tailorMutation.isPending
                    ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    : <WandSparklesIcon className="w-3.5 h-3.5" />}
                  {tailorMutation.isPending ? 'Generating…' : 'AI Tailor Resume'}
                </button>

                {job.source_url && (
                  <a
                    href={job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-xs ml-auto"
                  >
                    <ExternalLinkIcon className="w-3.5 h-3.5" />
                    View original
                  </a>
                )}
              </div>

              {saveMutation.isError && (
                <p className="text-xs text-amber-600">
                  {(saveMutation.error as { response?: { data?: { detail?: string } } })
                    ?.response?.data?.detail || 'Could not save application.'}
                </p>
              )}
            </div>

            {/* AI Results */}
            {tailorMutation.isSuccess && (
              <div className="space-y-4 animate-slide-up">
                {/* Key matches */}
                {tailorMutation.data.key_matches.length > 0 && (
                  <div className="card px-5 py-4">
                    <p className="text-sm font-semibold text-slate-700 mb-2">✓ Key Skill Matches</p>
                    <div className="flex flex-wrap gap-1.5">
                      {tailorMutation.data.key_matches.map((skill) => (
                        <span key={skill} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-xs rounded-md border border-emerald-200 font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {tailorMutation.data.suggestions.length > 0 && (
                  <div className="card px-5 py-4">
                    <p className="text-sm font-semibold text-slate-700 mb-2">💡 Suggestions</p>
                    <ul className="space-y-1">
                      {tailorMutation.data.suggestions.map((s, i) => (
                        <li key={i} className="text-xs text-slate-600 flex items-start gap-2">
                          <span className="text-brand-500 mt-0.5 shrink-0">→</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tailored resume */}
                <div className="card px-5 py-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-semibold text-slate-700">📄 Tailored Resume Content</p>
                    <button
                      onClick={() => handleCopy(tailorMutation.data.tailored_resume, 'resume')}
                      className="btn-secondary text-xs py-1"
                    >
                      {copiedSection === 'resume' ? <CheckIcon className="w-3 h-3 text-emerald-600" /> : <CopyIcon className="w-3 h-3" />}
                      {copiedSection === 'resume' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <pre className="text-xs text-slate-700 whitespace-pre-wrap bg-slate-50 rounded-lg p-4 max-h-72 overflow-y-auto font-mono leading-relaxed">
                    {tailorMutation.data.tailored_resume}
                  </pre>
                </div>

                {/* Cover letter */}
                {tailorMutation.data.cover_letter && (
                  <div className="card px-5 py-4">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm font-semibold text-slate-700">✉️ Cover Letter</p>
                      <button
                        onClick={() => handleCopy(tailorMutation.data.cover_letter!, 'cover')}
                        className="btn-secondary text-xs py-1"
                      >
                        {copiedSection === 'cover' ? <CheckIcon className="w-3 h-3 text-emerald-600" /> : <CopyIcon className="w-3 h-3" />}
                        {copiedSection === 'cover' ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <pre className="text-xs text-slate-700 whitespace-pre-wrap bg-slate-50 rounded-lg p-4 max-h-72 overflow-y-auto leading-relaxed">
                      {tailorMutation.data.cover_letter}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Job description */}
            <div className="card px-5 py-4">
              <p className="text-sm font-semibold text-slate-700 mb-3">Job Description</p>
              {job.skills_required.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {job.skills_required.map((skill) => (
                    <span key={skill} className="px-1.5 py-0.5 bg-brand-50 text-brand-700 text-[10px] rounded font-medium">
                      {skill}
                    </span>
                  ))}
                </div>
              )}
              <div className="prose prose-sm max-w-none text-slate-600 text-sm whitespace-pre-wrap leading-relaxed">
                {job.description}
              </div>
            </div>
          </>
        ) : (
          <div className="card py-12 text-center text-slate-400">
            <p>Job not found.</p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
