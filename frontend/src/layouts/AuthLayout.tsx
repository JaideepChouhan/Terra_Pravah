import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-primary flex items-center justify-center font-display antialiased text-navy">
      <Outlet />
    </div>
  )
}
