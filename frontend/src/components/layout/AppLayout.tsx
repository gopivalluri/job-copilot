'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  BriefcaseIcon, LayoutDashboardIcon, SearchIcon, FileTextIcon,
  SlidersIcon, ClipboardListIcon, LogOutIcon, UserIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/lib/auth-store'

const NAV_ITEMS = [
  { href: '/dashboard',    icon: LayoutDashboardIcon, label: 'Dashboard' },
  { href: '/jobs',         icon: SearchIcon,           label: 'Jobs' },
  { href: '/tracker',      icon: ClipboardListIcon,    label: 'Tracker' },
  { href: '/resume',       icon: FileTextIcon,         label: 'Resume' },
  { href: '/preferences',  icon: SlidersIcon,          label: 'Preferences' },
]

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, clearAuth } = useAuthStore()

  const handleLogout = () => {
    clearAuth()
    router.push('/auth/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-surface-50">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 flex flex-col bg-white border-r border-slate-200">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-slate-100">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center shrink-0">
            <BriefcaseIcon className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900 leading-tight">Job Copilot</p>
            <p className="text-[10px] text-slate-400 leading-tight">AI-powered search</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
            const active = pathname === href || pathname.startsWith(href + '/')
            return (
              <Link
                key={href}
                href={href}
                className={cn(active ? 'nav-link-active' : 'nav-link')}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{label}</span>
              </Link>
            )
          })}
        </nav>

        {/* User footer */}
        <div className="px-3 py-3 border-t border-slate-100 space-y-0.5">
          <div className="flex items-center gap-2.5 px-3 py-2">
            <div className="w-7 h-7 bg-brand-100 rounded-full flex items-center justify-center shrink-0">
              <UserIcon className="w-3.5 h-3.5 text-brand-700" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-900 truncate">
                {user?.full_name || user?.email?.split('@')[0]}
              </p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
          <button onClick={handleLogout} className="nav-link w-full">
            <LogOutIcon className="w-4 h-4 shrink-0" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
