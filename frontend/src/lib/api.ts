import apiClient from './api-client'
import type {
  AuthToken, User, Resume, Preferences,
  Job, JobWithScore, TailorResponse,
  Application, DashboardStats
} from '@/types'

// ─── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  register: (email: string, password: string, full_name?: string) =>
    apiClient.post<AuthToken>('/auth/register', { email, password, full_name }).then(r => r.data),

  login: (email: string, password: string) =>
    apiClient.post<AuthToken>('/auth/login', { email, password }).then(r => r.data),

  me: () =>
    apiClient.get<User>('/auth/me').then(r => r.data),
}

// ─── Resume ────────────────────────────────────────────────────────────────
export const resumeApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post<Resume>('/resume/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  getActive: () =>
    apiClient.get<Resume>('/resume').then(r => r.data),

  listAll: () =>
    apiClient.get<Resume[]>('/resume/all').then(r => r.data),

  delete: (id: number) =>
    apiClient.delete(`/resume/${id}`),
}

// ─── Preferences ───────────────────────────────────────────────────────────
export const prefsApi = {
  get: () =>
    apiClient.get<Preferences>('/preferences').then(r => r.data),

  upsert: (data: Partial<Preferences>) =>
    apiClient.post<Preferences>('/preferences', data).then(r => r.data),
}

// ─── Jobs ──────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (params?: {
    skip?: number
    limit?: number
    min_score?: number
    include_filtered?: boolean
    work_mode?: string
    sponsorship_only?: boolean
  }) =>
    apiClient.get<JobWithScore[]>('/jobs', { params }).then(r => r.data),

  get: (id: number) =>
    apiClient.get<JobWithScore>(`/jobs/${id}`).then(r => r.data),

  ingest: () =>
    apiClient.post<{ message: string; new_jobs: number; total_fetched: number; scored: number }>(
      '/jobs/ingest'
    ).then(r => r.data),

  ingestManual: (data: {
    title: string; company: string; description: string;
    location?: string; source_url?: string
  }) =>
    apiClient.post<JobWithScore>('/jobs/ingest/manual', data).then(r => r.data),

  score: (id: number) =>
    apiClient.post<{ total_score: number }>(`/jobs/${id}/score`).then(r => r.data),

  tailor: (jobId: number, generateCoverLetter = true) =>
    apiClient.post<TailorResponse>(`/jobs/${jobId}/tailor`, {
      job_id: jobId,
      generate_cover_letter: generateCoverLetter,
    }).then(r => r.data),
}

// ─── Applications ──────────────────────────────────────────────────────────
export const appsApi = {
  list: (status?: string) =>
    apiClient.get<Application[]>('/applications', { params: status ? { status } : {} }).then(r => r.data),

  create: (job_id: number, notes?: string) =>
    apiClient.post<Application>('/applications', { job_id, notes }).then(r => r.data),

  get: (id: number) =>
    apiClient.get<Application>(`/applications/${id}`).then(r => r.data),

  update: (id: number, data: {
    status?: string
    notes?: string
    follow_up_date?: string
    offer_details?: Record<string, unknown>
  }) =>
    apiClient.patch<Application>(`/applications/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    apiClient.delete(`/applications/${id}`),
}

// ─── Dashboard ─────────────────────────────────────────────────────────────
export const dashboardApi = {
  get: () =>
    apiClient.get<DashboardStats>('/dashboard').then(r => r.data),
}
