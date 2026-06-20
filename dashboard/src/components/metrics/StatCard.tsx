import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string
  icon: ReactNode
  variant?: 'default' | 'warning' | 'danger'
}

export function StatCard({ title, value, icon, variant = 'default' }: StatCardProps) {
  const borderColor = {
    default: 'border-gray-200',
    warning: 'border-yellow-300',
    danger: 'border-red-300',
  }[variant]

  return (
    <div className={`bg-white p-4 rounded-lg shadow-sm border ${borderColor}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-500">{title}</span>
        {icon}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}
