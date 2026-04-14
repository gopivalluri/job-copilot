'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { BriefcaseIcon, EyeIcon, EyeOffIcon, Loader2 } from 'lucide-react'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/lib/auth-store'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password required'),
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const router = useRouter()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [showPassword, setShowPassword] = useState(false)
  const [apiError, setApiError] = useState('')

  const {
    register, handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setApiError('')
    try {
      const res = await authApi.login(data.email, data.password)
      setAuth(res.user, res.access_token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail || 'Login failed. Check your credentials.'
      setApiError(message)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel – branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
            <BriefcaseIcon className="w-5 h-5 text-white" />
          </div>
          <span className="text-white font-semibold text-lg">Job Copilot</span>
        </div>

        <div className="space-y-6">
          <div className="space-y-3">
            {[
              { emoji: '🎯', text: 'Smart scoring across 6 factors' },
              { emoji: '🛂', text: 'H1B sponsorship detection engine' },
              { emoji: '✍️', text: 'AI-tailored resumes & cover letters' },
              { emoji: '📊', text: 'Track up to 50 applications/day' },
            ].map(({ emoji, text }) => (
              <div key={text} className="flex items-center gap-3 text-white/90">
                <span className="text-lg">{emoji}</span>
                <span className="text-sm">{text}</span>
              </div>
            ))}
          </div>
          <p className="text-white/50 text-xs">
            Built for software engineers navigating the modern job market.
          </p>
        </div>
      </div>

      {/* Right panel – form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm space-y-6">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <BriefcaseIcon className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-slate-900">Job Copilot</span>
          </div>

          <div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
            <p className="text-sm text-slate-500 mt-1">Sign in to your account</p>
          </div>

          {apiError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {apiError}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Email address</label>
              <input
                {...register('email')}
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                className="input"
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  className="input pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword
                    ? <EyeOffIcon className="w-4 h-4" />
                    : <EyeIcon className="w-4 h-4" />
                  }
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>
              )}
            </div>

            <button type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center py-2.5">
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="text-sm text-center text-slate-500">
            Don&apos;t have an account?{' '}
            <Link href="/auth/register" className="text-brand-600 hover:underline font-medium">
              Create one
            </Link>
          </div>

          {/* Demo credentials hint */}
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700 space-y-1">
            <p className="font-medium">Demo credentials</p>
            <p>Email: <span className="font-mono">demo@jobcopilot.dev</span></p>
            <p>Password: <span className="font-mono">demo1234</span></p>
          </div>
        </div>
      </div>
    </div>
  )
}
