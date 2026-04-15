import { useState } from 'react'
import { Outlet, NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
  HomeIcon,
  FolderIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UsersIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'
import { Menu, Transition } from '@headlessui/react'
import { Fragment } from 'react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Projects', href: '/dashboard/projects', icon: FolderIcon },
  { name: 'Analysis', href: '/dashboard/analysis', icon: ChartBarIcon },
  { name: 'Reports', href: '/dashboard/reports', icon: DocumentTextIcon },
  { name: 'Teams', href: '/dashboard/teams', icon: UsersIcon },
]

const bottomNavigation = [
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
]

export default function DashboardLayout() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-[#F8F6F6] text-text-main font-display">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-surface text-text-inverse border-r border-[#121826] transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-muted">
            <Link to="/dashboard" className="text-xl font-bold text-text-inverse font-heading">
              Terra Pravah
            </Link>
            <button
              className="lg:hidden text-muted hover:text-text-main"
              onClick={() => setSidebarOpen(false)}
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                end={item.href === '/dashboard'}
                className={({ isActive }) =>
                  `sidebar-item ${isActive ? 'sidebar-item-active' : ''}`
                }
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* Bottom navigation */}
          <div className="px-4 py-4 border-t border-muted space-y-1">
            {bottomNavigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `sidebar-item ${isActive ? 'sidebar-item-active' : ''}`
                }
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </NavLink>
            ))}
          </div>

          {/* User section */}
          <div className="p-4 border-t border-muted">
            <div className="flex items-center gap-3 p-3 rounded-none hover:bg-muted/10 transition-colors">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                {user?.firstName?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate text-text-inverse">
                  {user?.firstName} {user?.lastName}
                </p>
                <p className="text-xs text-muted truncate">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-background-light/90 backdrop-blur-lg border-b border-muted">
          <div className="flex items-center justify-between h-16 px-4 lg:px-8">
            {/* Mobile menu button */}
            <button
              className="lg:hidden text-muted hover:text-text-main"
              onClick={() => setSidebarOpen(true)}
            >
              <Bars3Icon className="w-6 h-6" />
            </button>

            {/* Search */}
            <div className="hidden md:flex flex-1 max-w-md mx-4">
              <div className="relative w-full">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
                <input
                  type="text"
                  placeholder="Search projects, reports..."
                  className="w-full pl-10 pr-4 py-2 bg-background-light border border-muted rounded-none text-sm text-text-main placeholder-muted focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
              {/* Notifications */}
              <button className="relative text-muted hover:text-text-main">
                <BellIcon className="w-6 h-6" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-primary rounded-full" />
              </button>

              {/* User menu */}
              <Menu as="div" className="relative">
                <Menu.Button className="flex items-center gap-2 text-text-main hover:text-primary transition-colors">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary text-sm font-bold">
                    {user?.firstName?.charAt(0) || 'U'}
                  </div>
                  <ChevronDownIcon className="w-4 h-4" />
                </Menu.Button>

                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <Menu.Items className="absolute right-0 mt-2 w-56 bg-white border border-muted rounded-none shadow-xl overflow-hidden focus:outline-none z-50">
                    <div className="px-4 py-3 border-b border-muted">
                      <p className="text-sm font-medium text-text-main">
                        {user?.firstName} {user?.lastName}
                      </p>
                      <p className="text-xs text-muted truncate">{user?.email}</p>
                    </div>
                    <div className="py-1">
                      <Menu.Item>
                        {({ active }) => (
                          <Link
                            to="/dashboard/profile"
                            className={`flex items-center gap-2 px-4 py-2 text-sm ${
                              active ? 'bg-background-light text-text-main' : 'text-text-main'
                            }`}
                          >
                            <UserCircleIcon className="w-5 h-5" />
                            Profile
                          </Link>
                        )}
                      </Menu.Item>
                      <Menu.Item>
                        {({ active }) => (
                          <Link
                            to="/dashboard/settings"
                            className={`flex items-center gap-2 px-4 py-2 text-sm ${
                              active ? 'bg-background-light text-text-main' : 'text-text-main'
                            }`}
                          >
                            <Cog6ToothIcon className="w-5 h-5" />
                            Settings
                          </Link>
                        )}
                      </Menu.Item>
                    </div>
                    <div className="border-t border-muted py-1">
                      <Menu.Item>
                        {({ active }) => (
                          <button
                            onClick={handleLogout}
                            className={`flex items-center gap-2 px-4 py-2 text-sm w-full text-left ${
                              active ? 'bg-background-light text-error-dark' : 'text-error-dark'
                            }`}
                          >
                            <ArrowRightOnRectangleIcon className="w-5 h-5" />
                            Sign out
                          </button>
                        )}
                      </Menu.Item>
                    </div>
                  </Menu.Items>
                </Transition>
              </Menu>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8 text-text-main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
