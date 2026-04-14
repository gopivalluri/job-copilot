import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatSalary(min?: number | null, max?: number | null): string {
  if (!min && !max) return 'Not disclosed'
  const fmt = (n: number) =>
    n >= 1000 ? `$${(n / 1000).toFixed(0)}k` : `$${n.toLocaleString()}`
  if (min && max) return `${fmt(min)} – ${fmt(max)}`
  if (min) return `${fmt(min)}+`
  if (max) return `Up to ${fmt(max)}`
  return 'Not disclosed'
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    }).format(new Date(dateStr))
  } catch {
    return dateStr
  }
}

export function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diff = Math.floor((now - then) / 1000)
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
  return formatDate(dateStr)
}

export function scoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-brand-600'
  if (score >= 40) return 'text-amber-600'
  return 'text-red-500'
}

export function scoreBg(score: number): string {
  if (score >= 80) return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  if (score >= 60) return 'bg-brand-50 text-brand-700 border-brand-200'
  if (score >= 40) return 'bg-amber-50 text-amber-700 border-amber-200'
  return 'bg-red-50 text-red-700 border-red-200'
}

export function sponsorshipBadge(status: string | null): { label: string; className: string } {
  switch (status) {
    case 'available':
      return { label: '✓ Sponsors H1B', className: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
    case 'transfer_ok':
      return { label: '↔ H1B Transfer', className: 'bg-teal-50 text-teal-700 border-teal-200' }
    case 'not_available':
      return { label: '✗ No Sponsorship', className: 'bg-red-50 text-red-600 border-red-200' }
    default:
      return { label: '? Sponsorship Unknown', className: 'bg-gray-50 text-gray-600 border-gray-200' }
  }
}

export function workModeBadge(mode: string | null): { label: string; className: string } {
  switch (mode) {
    case 'remote':
      return { label: '🌐 Remote', className: 'bg-violet-50 text-violet-700 border-violet-200' }
    case 'hybrid':
      return { label: '⚡ Hybrid', className: 'bg-blue-50 text-blue-700 border-blue-200' }
    case 'onsite':
      return { label: '🏢 On-site', className: 'bg-slate-50 text-slate-700 border-slate-200' }
    default:
      return { label: 'Unknown', className: 'bg-gray-50 text-gray-600 border-gray-200' }
  }
}

export function applicationStatusBadge(status: string): { label: string; className: string } {
  const map: Record<string, { label: string; className: string }> = {
    saved:        { label: 'Saved',        className: 'bg-gray-100 text-gray-700' },
    applied:      { label: 'Applied',      className: 'bg-brand-100 text-brand-700' },
    interviewing: { label: 'Interviewing', className: 'bg-amber-100 text-amber-700' },
    offer:        { label: '🎉 Offer',      className: 'bg-emerald-100 text-emerald-700' },
    rejected:     { label: 'Rejected',     className: 'bg-red-100 text-red-600' },
    withdrawn:    { label: 'Withdrawn',    className: 'bg-slate-100 text-slate-600' },
  }
  return map[status] || { label: status, className: 'bg-gray-100 text-gray-600' }
}
