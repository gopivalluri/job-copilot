'use client'

import { useCallback, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { FileTextIcon, UploadCloudIcon, Loader2, CheckCircleIcon, BrainIcon } from 'lucide-react'
import { AppLayout } from '@/components/layout/AppLayout'
import { useRequireAuth } from '@/hooks/useRequireAuth'
import { resumeApi } from '@/lib/api'

export default function ResumePage() {
  const auth = useRequireAuth()
  const qc = useQueryClient()
  const [uploadError, setUploadError] = useState('')

  const { data: resume, isLoading } = useQuery({
    queryKey: ['resume'],
    queryFn: resumeApi.getActive,
    enabled: auth,
    retry: false,
  })

  const uploadMutation = useMutation({
    mutationFn: resumeApi.upload,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['resume'] })
      setUploadError('')
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail || 'Upload failed'
      setUploadError(msg)
    },
  })

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setUploadError('')
      uploadMutation.mutate(accepted[0])
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  })

  if (!auth) return null

  const parsed = resume?.parsed_data

  return (
    <AppLayout>
      <div className="p-8 max-w-3xl mx-auto space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Resume Profile</h1>
          <p className="text-sm text-slate-500 mt-0.5">Upload your resume to power AI tailoring and match scoring</p>
        </div>

        {/* Upload zone */}
        <div
          {...getRootProps()}
          className={`card px-6 py-10 border-2 border-dashed cursor-pointer text-center transition-colors duration-150 ${
            isDragActive ? 'border-brand-400 bg-brand-50' : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50'
          }`}
        >
          <input {...getInputProps()} />
          {uploadMutation.isPending ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
              <p className="text-sm text-slate-600">Parsing resume…</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <UploadCloudIcon className="w-10 h-10 text-slate-400" />
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {isDragActive ? 'Drop it here' : 'Drag & drop or click to upload'}
                </p>
                <p className="text-xs text-slate-400 mt-1">PDF, DOCX, or TXT — max 10MB</p>
              </div>
            </div>
          )}
        </div>

        {uploadError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {uploadError}
          </div>
        )}

        {uploadMutation.isSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700 flex items-center gap-2">
            <CheckCircleIcon className="w-4 h-4 shrink-0" />
            Resume uploaded and parsed successfully!
          </div>
        )}

        {/* Parsed resume display */}
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => <div key={i} className="h-20 skeleton rounded-xl" />)}
          </div>
        ) : resume ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="w-4 h-4 text-emerald-500" />
              <p className="text-sm font-medium text-slate-700">
                Active resume: <span className="text-slate-900">{resume.filename}</span>
              </p>
            </div>

            {parsed && (
              <div className="grid gap-4">
                {/* Summary */}
                {parsed.summary && (
                  <div className="card px-5 py-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Summary</p>
                    <p className="text-sm text-slate-700 leading-relaxed">{parsed.summary}</p>
                  </div>
                )}

                {/* Key info */}
                <div className="card px-5 py-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Parsed Profile</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-xs text-slate-400">Current title</p>
                      <p className="font-medium text-slate-900">{parsed.current_title || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Experience</p>
                      <p className="font-medium text-slate-900">
                        {parsed.experience_years ? `~${parsed.experience_years} years` : '—'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Word count</p>
                      <p className="font-medium text-slate-900">{parsed.word_count || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Education entries</p>
                      <p className="font-medium text-slate-900">{parsed.education?.length || 0}</p>
                    </div>
                  </div>
                </div>

                {/* Skills */}
                {parsed.skills.length > 0 && (
                  <div className="card px-5 py-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3 flex items-center gap-2">
                      <BrainIcon className="w-3.5 h-3.5" />
                      Detected Skills ({parsed.skills.length})
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {parsed.skills.map((skill) => (
                        <span key={skill} className="px-2 py-0.5 bg-brand-50 text-brand-700 text-xs rounded-md border border-brand-200 font-medium">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Experience */}
                {parsed.experience.length > 0 && (
                  <div className="card px-5 py-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Experience Detected</p>
                    <div className="space-y-2">
                      {parsed.experience.map((exp, i) => (
                        <div key={i} className="flex items-start gap-3 text-sm">
                          <span className="text-xs text-slate-400 whitespace-nowrap mt-0.5 font-mono">{exp.period}</span>
                          <span className="text-slate-700">{exp.context || '—'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="card py-10 text-center text-slate-400">
            <FileTextIcon className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No resume uploaded yet</p>
            <p className="text-xs mt-1">Upload your resume above to enable AI features</p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
