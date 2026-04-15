import { useState, useEffect } from 'react'
import { 
  User, 
  Mail, 
  Building2, 
  Briefcase, 
  Phone, 
  Globe, 
  Camera,
  Loader2,
  Check,
  X,
  AlertTriangle,
  Lock,
  Bell,
  Palette,
  Shield,
  Key
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import api from '../../services/api'

interface UserProfile {
  id: string
  email: string
  first_name?: string
  last_name?: string
  avatar_url?: string
  company?: string
  job_title?: string
  phone?: string
  timezone?: string
  language?: string
  created_at: string
}

interface Preferences {
  theme: 'dark' | 'light' | 'system'
  units: 'metric' | 'imperial'
  notifications: {
    email_analysis_complete: boolean
    email_project_shared: boolean
    email_comment_mention: boolean
    push_enabled: boolean
  }
}

export default function Profile() {
  const { user, setUser } = useAuthStore()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [preferences, setPreferences] = useState<Preferences | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'preferences'>('profile')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Profile form
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [company, setCompany] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [phone, setPhone] = useState('')
  const [timezone, setTimezone] = useState('UTC')

  // Password form
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  useEffect(() => {
    fetchProfile()
    fetchPreferences()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await api.get('/api/users/me')
      const userData = response.data.user
      setProfile(userData)
      setFirstName(userData.first_name || '')
      setLastName(userData.last_name || '')
      setCompany(userData.company || '')
      setJobTitle(userData.job_title || '')
      setPhone(userData.phone || '')
      setTimezone(userData.timezone || 'UTC')
    } catch (err) {
      console.error('Failed to fetch profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/api/users/me/preferences')
      setPreferences(response.data.preferences)
    } catch (err) {
      console.error('Failed to fetch preferences:', err)
    }
  }

  const updateProfile = async () => {
    try {
      setSaving(true)
      setError(null)
      
      const response = await api.put('/api/users/me', {
        first_name: firstName,
        last_name: lastName,
        company,
        job_title: jobTitle,
        phone,
        timezone
      })
      
      setProfile(response.data.user)
      setUser({ ...user, ...response.data.user })
      setSuccess('Profile updated successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const changePassword = async () => {
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    try {
      setSaving(true)
      setError(null)
      
      await api.put('/api/users/me/password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setSuccess('Password changed successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  const updatePreferences = async (updates: Partial<Preferences>) => {
    try {
      const newPrefs = { ...preferences, ...updates }
      await api.put('/api/users/me/preferences', newPrefs)
      setPreferences(newPrefs as Preferences)
      setSuccess('Preferences updated')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update preferences')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-navy flex items-center gap-3">
          <User className="w-7 h-7 text-primary-500" />
          Profile Settings
        </h1>
        <p className="text-navy/60 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-none p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-red-400">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {success && (
        <div className="bg-primary-500/10 border border-primary-500/20 rounded-none p-4 flex items-center gap-3">
          <Check className="w-5 h-5 text-primary-400" />
          <p className="text-primary-400">{success}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-white p-1 rounded-none w-fit">
        {[
          { id: 'profile', label: 'Profile', icon: User },
          { id: 'security', label: 'Security', icon: Shield },
          { id: 'preferences', label: 'Preferences', icon: Palette }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-none transition-all ${
              activeTab === id
                ? 'bg-primary-500 text-navy'
                : 'text-navy/60 hover:text-navy hover:bg-neutral-100'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="glass-card p-6 space-y-6">
          {/* Avatar Section */}
          <div className="flex items-center gap-6 pb-6 border-b border-navy/10">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center">
                {profile?.avatar_url ? (
                  <img 
                    src={profile.avatar_url} 
                    alt="" 
                    className="w-24 h-24 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-3xl font-bold text-navy">
                    {(firstName?.[0] || profile?.email?.[0] || 'U').toUpperCase()}
                  </span>
                )}
              </div>
              <button className="absolute bottom-0 right-0 p-2 bg-neutral-100 rounded-full border border-navy/20 hover:bg-neutral-200 transition-colors">
                <Camera className="w-4 h-4 text-navy" />
              </button>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-navy">
                {firstName && lastName ? `${firstName} ${lastName}` : profile?.email}
              </h3>
              <p className="text-navy/60">{profile?.email}</p>
            </div>
          </div>

          {/* Profile Form */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                First Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="John"
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                Last Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Doe"
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                Company
              </label>
              <div className="relative">
                <Building2 className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Acme Inc."
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                Job Title
              </label>
              <div className="relative">
                <Briefcase className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Civil Engineer"
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                Phone
              </label>
              <div className="relative">
                <Phone className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-navy-muted mb-2">
                Timezone
              </label>
              <div className="relative">
                <Globe className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                >
                  <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                  <option value="Europe/London">Europe/London (GMT)</option>
                  <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-navy/10">
            <button
              onClick={updateProfile}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              Save Changes
            </button>
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          {/* Change Password */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-navy mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-primary-400" />
              Change Password
            </h3>

            <div className="space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Current Password
                </label>
                <div className="relative">
                  <Key className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>

              <button
                onClick={changePassword}
                disabled={saving || !currentPassword || !newPassword || !confirmPassword}
                className="btn-primary flex items-center gap-2"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Lock className="w-4 h-4" />
                )}
                Update Password
              </button>
            </div>
          </div>

          {/* Two-Factor Auth */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-primary-400 mt-0.5" />
                <div>
                  <h3 className="text-lg font-semibold text-navy">Two-Factor Authentication</h3>
                  <p className="text-navy/60 text-sm mt-1">
                    Add an extra layer of security to your account
                  </p>
                </div>
              </div>
              <button className="btn-secondary">
                Enable 2FA
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && preferences && (
        <div className="space-y-6">
          {/* Notifications */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-navy mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary-400" />
              Notification Settings
            </h3>

            <div className="space-y-4">
              {[
                { key: 'email_analysis_complete', label: 'Email when analysis completes' },
                { key: 'email_project_shared', label: 'Email when a project is shared with you' },
                { key: 'email_comment_mention', label: 'Email when mentioned in comments' },
                { key: 'push_enabled', label: 'Enable push notifications' }
              ].map(({ key, label }) => (
                <div key={key} className="flex items-center justify-between py-2">
                  <span className="text-navy-muted">{label}</span>
                  <button
                    onClick={() => updatePreferences({
                      notifications: {
                        ...preferences.notifications,
                        [key]: !preferences.notifications[key as keyof typeof preferences.notifications]
                      }
                    })}
                    className={`w-12 h-6 rounded-full transition-colors relative ${
                      preferences.notifications[key as keyof typeof preferences.notifications]
                        ? 'bg-primary-500'
                        : 'bg-neutral-200'
                    }`}
                  >
                    <span
                      className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                        preferences.notifications[key as keyof typeof preferences.notifications]
                          ? 'translate-x-7'
                          : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Display Settings */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-navy mb-4 flex items-center gap-2">
              <Palette className="w-5 h-5 text-primary-400" />
              Display Settings
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-2">
                  Units
                </label>
                <div className="flex gap-2">
                  {(['metric', 'imperial'] as const).map((unit) => (
                    <button
                      key={unit}
                      onClick={() => updatePreferences({ units: unit })}
                      className={`px-4 py-2 rounded-none border capitalize transition-all ${
                        preferences.units === unit
                          ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                          : 'border-navy/20 bg-neutral-100 text-navy-muted hover:border-dark-500'
                      }`}
                    >
                      {unit}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
