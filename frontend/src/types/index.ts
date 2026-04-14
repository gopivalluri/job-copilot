// ─── Auth ──────────────────────────────────────────────────────────────────
export interface User {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string | null
}

export interface AuthToken {
  access_token: string
  token_type: string
  user: User
}

// ─── Resume ────────────────────────────────────────────────────────────────
export interface ParsedResume {
  skills: string[]
  experience_years: number | null
  current_title: string | null
  education: Array<{ raw: string }>
  experience: Array<{ period: string; context: string }>
  summary: string | null
  word_count: number
}

export interface Resume {
  id: number
  filename: string | null
  parsed_data: ParsedResume | null
  is_active: boolean
  created_at: string | null
}

// ─── Preferences ───────────────────────────────────────────────────────────
export interface Preferences {
  id: number
  user_id: number
  target_roles: string[]
  employment_types: string[]
  work_modes: string[]
  preferred_locations: string[]
  min_salary: number
  max_salary: number | null
  requires_sponsorship: boolean
  sponsorship_types: string[]
  experience_levels: string[]
  include_keywords: string[]
  exclude_keywords: string[]
  auto_score_threshold: number
  daily_limit: number
}

// ─── Jobs ──────────────────────────────────────────────────────────────────
export type EmploymentType = 'full_time' | 'contract' | 'part_time' | 'internship'
export type WorkMode = 'remote' | 'hybrid' | 'onsite'
export type SponsorshipStatus = 'available' | 'not_available' | 'unknown' | 'transfer_ok'
export type ExperienceLevel = 'entry' | 'mid' | 'senior' | 'lead' | 'staff'

export interface Job {
  id: number
  external_id: string | null
  source: string | null
  source_url: string | null
  title: string
  company: string
  location: string | null
  description: string | null
  employment_type: EmploymentType | null
  work_mode: WorkMode | null
  experience_level: ExperienceLevel | null
  skills_required: string[]
  salary_min: number | null
  salary_max: number | null
  sponsorship_status: SponsorshipStatus | null
  posted_at: string | null
  ingested_at: string | null
}

export interface JobWithScore extends Job {
  score: number | null
  score_details: {
    title: number
    skills: number
    sponsorship: number
    employment: number
    location: number
    experience: number
  } | null
  is_filtered_out: boolean
  filter_reason: string | null
}

export interface ScoreDetails {
  job_id: number
  total_score: number
  title_score: number
  skills_score: number
  sponsorship_score: number
  employment_score: number
  location_score: number
  experience_score: number
  is_filtered_out: boolean
  filter_reason: string | null
}

export interface TailorResponse {
  tailored_resume: string
  cover_letter: string | null
  key_matches: string[]
  suggestions: string[]
}

// ─── Applications ──────────────────────────────────────────────────────────
export type ApplicationStatus =
  | 'saved'
  | 'applied'
  | 'interviewing'
  | 'offer'
  | 'rejected'
  | 'withdrawn'

export interface Application {
  id: number
  job_id: number
  status: ApplicationStatus
  tailored_resume: string | null
  cover_letter: string | null
  notes: string | null
  applied_at: string | null
  last_updated: string | null
  follow_up_date: string | null
  offer_details: Record<string, unknown> | null
  job: Job | null
}

// ─── Dashboard ─────────────────────────────────────────────────────────────
export interface DashboardStats {
  total_jobs_ingested: number
  jobs_scored_today: number
  top_matches: JobWithScore[]
  applications_by_status: Record<ApplicationStatus, number>
  total_applications: number
  applied_today: number
  avg_match_score: number
  sponsorship_eligible: number
}
