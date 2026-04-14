import { cn, scoreBg } from '@/lib/utils'

interface ScoreBadgeProps {
  score: number | null
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function ScoreBadge({ score, size = 'md', className }: ScoreBadgeProps) {
  if (score === null || score === undefined) {
    return (
      <span className={cn('badge bg-gray-50 text-gray-400 border-gray-200', className)}>
        —
      </span>
    )
  }

  const sizeClasses = {
    sm: 'w-9 h-9 text-xs',
    md: 'w-11 h-11 text-sm',
    lg: 'w-14 h-14 text-base',
  }

  return (
    <div
      className={cn(
        'score-ring border-2 font-bold',
        scoreBg(score).replace(/^bg-(\S+)\s.*/, 'border-$1'),
        sizeClasses[size],
        scoreBg(score),
        className
      )}
    >
      {Math.round(score)}
    </div>
  )
}

interface ScoreBarProps {
  label: string
  value: number
  max?: number
}

export function ScoreBar({ label, value, max = 100 }: ScoreBarProps) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-600">
        <span>{label}</span>
        <span className="font-medium">{Math.round(value)}</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            value >= 80 ? 'bg-emerald-500' :
            value >= 60 ? 'bg-brand-500' :
            value >= 40 ? 'bg-amber-500' : 'bg-red-400'
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
