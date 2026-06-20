import { CheckCircle, ShieldOff, ArrowUpCircle } from 'lucide-react'

interface AlertActionsProps {
  alertId: string
  decision?: string
  onAction: (alertId: string, action: string, notes?: string) => void
}

export function AlertActions({ alertId, decision, onAction }: AlertActionsProps) {
  return (
    <div className="flex gap-1">
      <div className="relative group">
        <button
          onClick={(e) => { e.stopPropagation(); onAction(alertId, 'approve') }}
          className="p-1.5 text-green-600 hover:bg-green-50 rounded"
        >
          <CheckCircle className="w-4 h-4" />
        </button>
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-0.5 bg-gray-900 text-white text-[10px] rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-75 pointer-events-none">
          Approve
        </span>
      </div>
      {decision !== 'escalate' && (
        <div className="relative group">
          <button
            onClick={(e) => { e.stopPropagation(); onAction(alertId, 'escalate') }}
            className="p-1.5 text-orange-600 hover:bg-orange-50 rounded"
          >
            <ArrowUpCircle className="w-4 h-4" />
          </button>
          <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-0.5 bg-gray-900 text-white text-[10px] rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-75 pointer-events-none">
            Escalate
          </span>
        </div>
      )}
      <div className="relative group">
        <button
          onClick={(e) => { e.stopPropagation(); onAction(alertId, 'block') }}
          className="p-1.5 text-red-600 hover:bg-red-50 rounded"
        >
          <ShieldOff className="w-4 h-4" />
        </button>
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-0.5 bg-gray-900 text-white text-[10px] rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-75 pointer-events-none">
          Block
        </span>
      </div>
    </div>
  )
}
