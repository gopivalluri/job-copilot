'use client'

import { useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { SlidersIcon, Loader2, CheckIcon, PlusIcon, XIcon } from 'lucide-react'
import { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { prefsApi } from '@/lib/api'
import { cn } from '@/lib/utils'

const schema = z.object({
  target_roles: z.array(z.string()),
  employment_types: z.array(z.string()),
  work_modes: z.array(z.string()),
  preferred_locations: z.array(z.string()),
  min_salary: z.number().min(0),
  max_salary: z.number().nullable().optional(),
  requires_sponsorship: z.boolean(),
  sponsorship_types: z.array(z.string()),
  experience_levels: z.array(z.string()),
  include_keywords: z.array(z.string()),
  exclude_keywords: z.array(z.string()),
  auto_score_threshold: z.number().min(0).max(100),
  daily_limit: z.number().min(1).max(200),
})
type FormData = z.infer<typeof schema>

function TagInput({
  value, onChange, placeholder,
}: {
  value: string[]; onChange: (v: string[]) => void; placeholder?: string
}) {
  const [input, setInput] = useState('')

  const add = () => {
    const trimmed = input.trim()
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed])
    }
    setInput('')
  }

  const remove = (tag: string) => onChange(value.filter((t) => t !== tag))

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
          placeholder={placeholder}
          className="input flex-1 text-sm"
        />
        <button type="button" onClick={add} className="btn-secondary px-3">
          <PlusIcon className="w-3.5 h-3.5" />
        </button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-brand-50 text-brand-700 text-xs rounded-md border border-brand-200"
          >
            {tag}
            <button type="button" onClick={() => remove(tag)} className="hover:text-brand-900">
              <XIcon className="w-2.5 h-2.5" />
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}

function CheckboxGroup({
  options, value, onChange,
}: {
  options: { value: string; label: string }[]
  value: string[]
  onChange: (v: string[]) => void
}) {
  const toggle = (v: string) => {
    if (value.includes(v)) onChange(value.filter((x) => x !== v))
    else onChange([...value, v])
  }
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => toggle(opt.value)}
          className={cn(
            'px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors',
            value.includes(opt.value)
              ? 'bg-brand-600 text-white border-brand-600'
              : 'bg-white text-slate-700 border-slate-200 hover:border-brand-300'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

export default function PreferencesPage() {
  const auth = useRequireAuth()
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: prefs, isLoading } = useQuery({
    queryKey: ['preferences'],
    queryFn: prefsApi.get,
    enabled: auth,
    retry: false,
  })

  const { register, handleSubmit, control, reset, watch, formState: { isSubmitting } } =
    useForm<FormData>({
      resolver: zodResolver(schema),
      defaultValues: {
        target_roles: [], employment_types: [], work_modes: [],
        preferred_locations: [], min_salary: 90000, max_salary: null,
        requires_sponsorship: false, sponsorship_types: [],
        experience_levels: [], include_keywords: [], exclude_keywords: [],
        auto_score_threshold: 75, daily_limit: 50,
      },
    })

  useEffect(() => {
    if (prefs) reset(prefs)
  }, [prefs, reset])

  const saveMutation = useMutation({
    mutationFn: prefsApi.upsert,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['preferences'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const onSubmit = (data: FormData) => saveMutation.mutate(data)

  if (!auth) return null

  return (
    <AppLayout>
      <div className="p-8 max-w-3xl mx-auto animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Preferences</h1>
            <p className="text-sm text-slate-500 mt-0.5">Configure your job search filters and scoring criteria</p>
          </div>
          <button
            type="button"
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting || saveMutation.isPending}
            className="btn-primary"
          >
            {(isSubmitting || saveMutation.isPending)
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : saved ? <CheckIcon className="w-4 h-4" />
              : <SlidersIcon className="w-4 h-4" />}
            {saved ? 'Saved!' : 'Save Preferences'}
          </button>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-28 skeleton rounded-xl" />)}
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">

            {/* Target roles */}
            <div className="card px-5 py-4 space-y-3">
              <p className="text-sm font-semibold text-slate-700">🎯 Target Roles</p>
              <Controller
                name="target_roles"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="e.g. Senior Backend Engineer"
                  />
                )}
              />
            </div>

            {/* Employment & Work mode */}
            <div className="card px-5 py-4 space-y-4">
              <p className="text-sm font-semibold text-slate-700">💼 Employment Type</p>
              <Controller
                name="employment_types"
                control={control}
                render={({ field }) => (
                  <CheckboxGroup
                    options={[
                      { value: 'full_time', label: 'Full-time' },
                      { value: 'contract', label: 'Contract' },
                      { value: 'part_time', label: 'Part-time' },
                      { value: 'internship', label: 'Internship' },
                    ]}
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />

              <p className="text-sm font-semibold text-slate-700 pt-2">🌐 Work Mode</p>
              <Controller
                name="work_modes"
                control={control}
                render={({ field }) => (
                  <CheckboxGroup
                    options={[
                      { value: 'remote', label: '🌐 Remote' },
                      { value: 'hybrid', label: '⚡ Hybrid' },
                      { value: 'onsite', label: '🏢 On-site' },
                    ]}
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />
            </div>

            {/* Locations */}
            <div className="card px-5 py-4 space-y-3">
              <p className="text-sm font-semibold text-slate-700">📍 Preferred Locations</p>
              <Controller
                name="preferred_locations"
                control={control}
                render={({ field }) => (
                  <TagInput
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="e.g. Texas, California, Remote"
                  />
                )}
              />
            </div>

            {/* Salary */}
            <div className="card px-5 py-4 space-y-4">
              <p className="text-sm font-semibold text-slate-700">💰 Salary Range</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label text-xs">Minimum ($)</label>
                  <input
                    type="number"
                    {...register('min_salary', { valueAsNumber: true })}
                    className="input"
                    placeholder="90000"
                  />
                </div>
                <div>
                  <label className="label text-xs">Maximum ($) — optional</label>
                  <input
                    type="number"
                    {...register('max_salary', { valueAsNumber: true })}
                    className="input"
                    placeholder="No limit"
                  />
                </div>
              </div>
            </div>

            {/* Sponsorship */}
            <div className="card px-5 py-4 space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-700">🛂 Visa Sponsorship</p>
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    {...register('requires_sponsorship')}
                    className="rounded border-slate-300 text-brand-600 w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">I need sponsorship</span>
                </label>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-2">Sponsorship types</p>
                <Controller
                  name="sponsorship_types"
                  control={control}
                  render={({ field }) => (
                    <CheckboxGroup
                      options={[
                        { value: 'H1B', label: 'H-1B' },
                        { value: 'H1B_transfer', label: 'H-1B Transfer' },
                        { value: 'OPT', label: 'OPT' },
                        { value: 'TN', label: 'TN Visa' },
                      ]}
                      value={field.value}
                      onChange={field.onChange}
                    />
                  )}
                />
              </div>
            </div>

            {/* Experience level */}
            <div className="card px-5 py-4 space-y-3">
              <p className="text-sm font-semibold text-slate-700">📈 Experience Level</p>
              <Controller
                name="experience_levels"
                control={control}
                render={({ field }) => (
                  <CheckboxGroup
                    options={[
                      { value: 'entry', label: 'Entry' },
                      { value: 'mid', label: 'Mid' },
                      { value: 'senior', label: 'Senior' },
                      { value: 'lead', label: 'Lead' },
                      { value: 'staff', label: 'Staff' },
                    ]}
                    value={field.value}
                    onChange={field.onChange}
                  />
                )}
              />
            </div>

            {/* Keywords */}
            <div className="card px-5 py-4 space-y-4">
              <p className="text-sm font-semibold text-slate-700">🔍 Keyword Filters</p>
              <div>
                <label className="label text-xs text-emerald-700">✓ Include / Boost keywords</label>
                <Controller
                  name="include_keywords"
                  control={control}
                  render={({ field }) => (
                    <TagInput
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="e.g. python, fastapi"
                    />
                  )}
                />
              </div>
              <div>
                <label className="label text-xs text-red-600">✗ Exclude keywords</label>
                <Controller
                  name="exclude_keywords"
                  control={control}
                  render={({ field }) => (
                    <TagInput
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="e.g. no sponsorship, clearance required"
                    />
                  )}
                />
              </div>
            </div>

            {/* Thresholds */}
            <div className="card px-5 py-4 space-y-4">
              <p className="text-sm font-semibold text-slate-700">⚙️ Automation Settings</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label text-xs">Auto-apply score threshold</label>
                  <input
                    type="number"
                    {...register('auto_score_threshold', { valueAsNumber: true })}
                    min={0} max={100}
                    className="input"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">Jobs scoring above this will be highlighted</p>
                </div>
                <div>
                  <label className="label text-xs">Daily application limit</label>
                  <input
                    type="number"
                    {...register('daily_limit', { valueAsNumber: true })}
                    min={1} max={200}
                    className="input"
                  />
                </div>
              </div>
            </div>

          </form>
        )}
      </div>
    </AppLayout>
  )
}
