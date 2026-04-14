'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { BriefcaseIcon, Loader2 } from 'lucide-react'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/lib/auth-store'

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const router = useRouter()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [apiError, setApiError] = useState('')

  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setApiError('')
    try {
      const res = await authApi.register(data.email, data.password, data.full_name)
      setAuth(res.user, res.access_token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail || 'Registration failed.'
      setApiError(message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-surface-50">
      <div className="w-full max-w-sm space-y-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <BriefcaseIcon className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-slate-900">Job Copilot</span>
        </div>

        <div>
          <h1 className="text-2xl font-bold text-slate-900">Create your account</h1>
          <p className="text-sm text-slate-500 mt-1">Start automating your job search today</p>
        </div>

        {apiError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {apiError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label">Full name</label>
            <input {...register('full_name')} type="text" placeholder="Alex Chen" className="input" />
            {errors.full_name && <p className="text-xs text-red-500 mt-1">{errors.full_name.message}</p>}
          </div>

          <div>
            <label className="label">Email address</label>
            <input {...register('email')} type="email" placeholder="you@example.com" className="input" />
            {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="label">Password</label>
            <input {...register('password')} type="password" placeholder="Min. 8 characters" className="input" />
            {errors.password && <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>}
          </div>

          <div>
            <label className="label">Confirm password</label>
            <input {...register('confirmPassword')} type="password" placeholder="Repeat password" className="input" />
            {errors.confirmPassword && <p className="text-xs text-red-500 mt-1">{errors.confirmPassword.message}</p>}
          </div>

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center py-2.5">
            {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
            {isSubmitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="text-sm text-center text-slate-500">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-brand-600 hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
