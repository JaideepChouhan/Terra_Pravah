import { useState, useEffect } from 'react'
import { 
  Users, 
  Plus, 
  Search, 
  MoreVertical, 
  Mail, 
  UserPlus, 
  Crown, 
  Shield, 
  Eye,
  Loader2,
  Trash2,
  X,
  Check,
  AlertTriangle
} from 'lucide-react'
import { teamsApi } from '../../services/api'

interface Team {
  id: string
  name: string
  slug: string
  description?: string
  logo_url?: string
  owner_id: string
  member_count?: number
  created_at: string
}

interface TeamMember {
  user: {
    id: string
    email: string
    first_name?: string
    last_name?: string
    avatar_url?: string
  }
  role: 'owner' | 'admin' | 'member' | 'viewer'
}

export default function Teams() {
  const [teams, setTeams] = useState<Team[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [members, setMembers] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [membersLoading, setMembersLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Form states
  const [newTeamName, setNewTeamName] = useState('')
  const [newTeamDescription, setNewTeamDescription] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'admin' | 'member' | 'viewer'>('member')
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    fetchTeams()
  }, [])

  const fetchTeams = async () => {
    try {
      setLoading(true)
      const response = await teamsApi.list()
      setTeams(response.data.teams || [])
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load teams')
    } finally {
      setLoading(false)
    }
  }

  const fetchMembers = async (teamId: string) => {
    try {
      setMembersLoading(true)
      const response = await teamsApi.get(teamId)
      setMembers(response.data.members || [])
    } catch (err) {
      console.error('Failed to fetch members:', err)
    } finally {
      setMembersLoading(false)
    }
  }

  const handleSelectTeam = (team: Team) => {
    setSelectedTeam(team)
    fetchMembers(team.id)
  }

  const createTeam = async () => {
    if (!newTeamName.trim()) return

    try {
      setFormLoading(true)
      const response = await teamsApi.create({
        name: newTeamName,
        description: newTeamDescription
      })
      setTeams([...teams, response.data.team])
      setShowCreateModal(false)
      setNewTeamName('')
      setNewTeamDescription('')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create team')
    } finally {
      setFormLoading(false)
    }
  }

  const inviteMember = async () => {
    if (!inviteEmail.trim() || !selectedTeam) return

    try {
      setFormLoading(true)
      await teamsApi.addMember(selectedTeam.id, {
        email: inviteEmail,
        role: inviteRole
      })
      fetchMembers(selectedTeam.id)
      setShowInviteModal(false)
      setInviteEmail('')
      setInviteRole('member')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to invite member')
    } finally {
      setFormLoading(false)
    }
  }

  const removeMember = async (userId: string) => {
    if (!selectedTeam) return

    try {
      await teamsApi.removeMember(selectedTeam.id, userId)
      setMembers(members.filter(m => m.user.id !== userId))
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to remove member')
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner': return <Crown className="w-4 h-4 text-amber-400" />
      case 'admin': return <Shield className="w-4 h-4 text-primary-400" />
      case 'member': return <Users className="w-4 h-4 text-blue-400" />
      default: return <Eye className="w-4 h-4 text-navy/60" />
    }
  }

  const filteredTeams = teams.filter(team =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-navy flex items-center gap-3">
            <Users className="w-7 h-7 text-primary-500" />
            Teams
          </h1>
          <p className="text-navy/60 mt-1">
            Collaborate with your team on drainage projects
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Team
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-none p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <div className="flex-1">
            <p className="text-red-400">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Teams List */}
        <div className="lg:col-span-1 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search teams..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border border-navy/10 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {/* Teams */}
          <div className="space-y-2">
            {filteredTeams.length === 0 ? (
              <div className="glass-card p-8 text-center">
                <Users className="w-12 h-12 text-dark-500 mx-auto mb-3" />
                <p className="text-navy/60">No teams yet</p>
                <p className="text-dark-500 text-sm mt-1">
                  Create a team to start collaborating
                </p>
              </div>
            ) : (
              filteredTeams.map((team) => (
                <button
                  key={team.id}
                  onClick={() => handleSelectTeam(team)}
                  className={`w-full p-4 rounded-none border text-left transition-all ${
                    selectedTeam?.id === team.id
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-navy/10 bg-white/50 hover:border-navy/20'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-none bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center text-navy font-bold">
                      {team.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-navy truncate">{team.name}</h3>
                      <p className="text-sm text-navy/60">
                        {team.member_count || 1} member{(team.member_count || 1) !== 1 ? 's' : ''}
                      </p>
                    </div>
                    <MoreVertical className="w-4 h-4 text-dark-500" />
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Team Details */}
        <div className="lg:col-span-2">
          {selectedTeam ? (
            <div className="glass-card p-6 space-y-6">
              {/* Team Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-none bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center text-navy text-2xl font-bold">
                    {selectedTeam.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-navy">{selectedTeam.name}</h2>
                    <p className="text-navy/60">{selectedTeam.description || 'No description'}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowInviteModal(true)}
                  className="btn-primary flex items-center gap-2"
                >
                  <UserPlus className="w-4 h-4" />
                  Invite
                </button>
              </div>

              {/* Members List */}
              <div>
                <h3 className="text-lg font-semibold text-navy mb-4">
                  Team Members ({members.length})
                </h3>
                
                {membersLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
                  </div>
                ) : (
                  <div className="space-y-2">
                    {members.map((member) => (
                      <div
                        key={member.user.id}
                        className="flex items-center justify-between p-3 bg-neutral-100/50 rounded-none"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-neutral-200 flex items-center justify-center">
                            {member.user.avatar_url ? (
                              <img 
                                src={member.user.avatar_url} 
                                alt="" 
                                className="w-10 h-10 rounded-full object-cover"
                              />
                            ) : (
                              <span className="text-navy font-medium">
                                {(member.user.first_name?.[0] || member.user.email[0]).toUpperCase()}
                              </span>
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-navy font-medium">
                                {member.user.first_name && member.user.last_name
                                  ? `${member.user.first_name} ${member.user.last_name}`
                                  : member.user.email}
                              </span>
                              {getRoleIcon(member.role)}
                            </div>
                            <span className="text-sm text-navy/60">{member.user.email}</span>
                          </div>
                        </div>
                        {member.role !== 'owner' && (
                          <button
                            onClick={() => removeMember(member.user.id)}
                            className="p-2 text-navy/60 hover:text-red-400 hover:bg-red-500/10 rounded-none transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="glass-card p-12 text-center">
              <Users className="w-16 h-16 text-dark-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-navy mb-2">Select a Team</h3>
              <p className="text-navy/60">
                Choose a team from the list to view members and manage settings
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-none p-6 max-w-md w-full border border-navy/10">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-navy">Create Team</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 text-navy/60 hover:text-navy"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-1">
                  Team Name *
                </label>
                <input
                  type="text"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="e.g., Engineering Team"
                  className="w-full px-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-navy-muted mb-1">
                  Description
                </label>
                <textarea
                  value={newTeamDescription}
                  onChange={(e) => setNewTeamDescription(e.target.value)}
                  placeholder="What does this team work on?"
                  rows={3}
                  className="w-full px-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={createTeam}
                disabled={!newTeamName.trim() || formLoading}
                className="btn-primary flex items-center gap-2"
              >
                {formLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Check className="w-4 h-4" />
                )}
                Create Team
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-none p-6 max-w-md w-full border border-navy/10">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-navy">Invite Member</h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="p-1 text-navy/60 hover:text-navy"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-muted mb-1">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-navy/60 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="colleague@example.com"
                    className="w-full pl-10 pr-4 py-2 bg-neutral-100 border border-navy/20 rounded-none text-navy placeholder-dark-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-navy-muted mb-1">
                  Role
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['admin', 'member', 'viewer'] as const).map((role) => (
                    <button
                      key={role}
                      onClick={() => setInviteRole(role)}
                      className={`p-2 rounded-none border text-center capitalize transition-all ${
                        inviteRole === role
                          ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                          : 'border-navy/20 bg-neutral-100 text-navy-muted hover:border-dark-500'
                      }`}
                    >
                      {role}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={inviteMember}
                disabled={!inviteEmail.trim() || formLoading}
                className="btn-primary flex items-center gap-2"
              >
                {formLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <UserPlus className="w-4 h-4" />
                )}
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
