import { useState } from 'react'
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Save,
  Loader2,
  CheckCircle,
  Key,
  Mail,
  Building2,
  Globe
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

interface UserProfile {
  name: string
  email: string
  company?: string
  role?: string
}

interface Preferences {
  defaultAlgorithm: 'd8' | 'dinf'
  defaultStormYears: number
  defaultRunoffCoeff: number
  emailNotifications: boolean
  units: 'metric' | 'imperial'
}

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'notifications' | 'security'>('profile')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  
  const [profile, setProfile] = useState<UserProfile>({
    name: `${user?.firstName || ''} ${user?.lastName || ''}`.trim(),
    email: user?.email || '',
    company: user?.company || '',
    role: user?.role || 'Engineer'
  })
  
  const [preferences, setPreferences] = useState<Preferences>({
    defaultAlgorithm: 'd8',
    defaultStormYears: 10,
    defaultRunoffCoeff: 0.5,
    emailNotifications: true,
    units: 'metric'
  })

  const handleSave = async () => {
    setSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'preferences', label: 'Preferences', icon: Palette },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <SettingsIcon className="w-7 h-7 text-primary-500" />
          Settings
        </h1>
        <p className="text-dark-400 mt-2">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64 flex-shrink-0">
          <div className="glass-card p-2">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === id
                    ? 'bg-primary-500/20 text-primary-400'
                    : 'text-dark-300 hover:bg-dark-700/50 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="glass-card p-6">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-white">Profile Information</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      <User className="w-4 h-4 inline mr-2" />
                      Full Name
                    </label>
                    <input
                      type="text"
                      value={profile.name}
                      onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                      className="input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      <Mail className="w-4 h-4 inline mr-2" />
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                      className="input w-full"
                      disabled
                    />
                    <p className="text-xs text-dark-500 mt-1">Email cannot be changed</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      <Building2 className="w-4 h-4 inline mr-2" />
                      Company/Organization
                    </label>
                    <input
                      type="text"
                      value={profile.company}
                      onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                      className="input w-full"
                      placeholder="Enter company name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      Role
                    </label>
                    <select
                      value={profile.role}
                      onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                      className="input w-full"
                    >
                      <option value="Engineer">Engineer</option>
                      <option value="Designer">Designer</option>
                      <option value="Manager">Manager</option>
                      <option value="Consultant">Consultant</option>
                      <option value="Student">Student</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-white">Analysis Preferences</h2>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      Default Flow Algorithm
                    </label>
                    <select
                      value={preferences.defaultAlgorithm}
                      onChange={(e) => setPreferences({ ...preferences, defaultAlgorithm: e.target.value as any })}
                      className="input w-full"
                    >
                      <option value="d8">D8 - Fast & Recommended</option>
                      <option value="dinf">D-Infinity - More Accurate</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      Default Design Storm (years)
                    </label>
                    <select
                      value={preferences.defaultStormYears}
                      onChange={(e) => setPreferences({ ...preferences, defaultStormYears: Number(e.target.value) })}
                      className="input w-full"
                    >
                      <option value={2}>2-Year</option>
                      <option value={5}>5-Year</option>
                      <option value={10}>10-Year</option>
                      <option value={25}>25-Year</option>
                      <option value={50}>50-Year</option>
                      <option value={100}>100-Year</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      Default Runoff Coefficient
                    </label>
                    <input
                      type="number"
                      min="0.1"
                      max="1.0"
                      step="0.05"
                      value={preferences.defaultRunoffCoeff}
                      onChange={(e) => setPreferences({ ...preferences, defaultRunoffCoeff: Number(e.target.value) })}
                      className="input w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      <Globe className="w-4 h-4 inline mr-2" />
                      Units System
                    </label>
                    <select
                      value={preferences.units}
                      onChange={(e) => setPreferences({ ...preferences, units: e.target.value as any })}
                      className="input w-full"
                    >
                      <option value="metric">Metric (meters)</option>
                      <option value="imperial">Imperial (feet)</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-white">Notification Settings</h2>
                
                <div className="space-y-4">
                  <label className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg cursor-pointer">
                    <div>
                      <p className="text-white font-medium">Email Notifications</p>
                      <p className="text-sm text-dark-400">Receive updates about analysis completion</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.emailNotifications}
                      onChange={(e) => setPreferences({ ...preferences, emailNotifications: e.target.checked })}
                      className="w-5 h-5 text-primary-500 rounded"
                    />
                  </label>
                  
                  <label className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg cursor-pointer">
                    <div>
                      <p className="text-white font-medium">Project Updates</p>
                      <p className="text-sm text-dark-400">Get notified when collaborators make changes</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5 text-primary-500 rounded" />
                  </label>
                  
                  <label className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg cursor-pointer">
                    <div>
                      <p className="text-white font-medium">Weekly Summary</p>
                      <p className="text-sm text-dark-400">Receive weekly digest of project activity</p>
                    </div>
                    <input type="checkbox" className="w-5 h-5 text-primary-500 rounded" />
                  </label>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-white">Security Settings</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      <Key className="w-4 h-4 inline mr-2" />
                      Current Password
                    </label>
                    <input type="password" className="input w-full max-w-md" placeholder="Enter current password" />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      New Password
                    </label>
                    <input type="password" className="input w-full max-w-md" placeholder="Enter new password" />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-200 mb-2">
                      Confirm New Password
                    </label>
                    <input type="password" className="input w-full max-w-md" placeholder="Confirm new password" />
                  </div>
                  
                  <button className="btn-secondary">Update Password</button>
                </div>
                
                <hr className="border-dark-700" />
                
                <div>
                  <h3 className="text-white font-medium mb-2">Active Sessions</h3>
                  <p className="text-sm text-dark-400 mb-4">Manage your active login sessions</p>
                  
                  <div className="p-4 bg-dark-800/50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white">Current Session</p>
                        <p className="text-xs text-dark-400">Linux • Chrome • Last active now</p>
                      </div>
                      <span className="text-xs text-primary-400 bg-primary-500/20 px-2 py-1 rounded">Active</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="mt-8 pt-6 border-t border-dark-700 flex items-center justify-between">
              <div>
                {saved && (
                  <span className="text-primary-400 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Settings saved successfully
                  </span>
                )}
              </div>
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary flex items-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}