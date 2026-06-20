interface BadgeProps {
  variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  children: React.ReactNode;
}

const variantStyles = {
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
  neutral: 'bg-gray-100 text-gray-800',
};

export function Badge({ variant, children }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantStyles[variant]}`}
    >
      {children}
    </span>
  );
}

export function DecisionBadge({ decision }: { decision: string }) {
  const variantMap: Record<string, BadgeProps['variant']> = {
    approve: 'success',
    verify: 'info',
    review: 'warning',
    block: 'danger',
  };
  return <Badge variant={variantMap[decision] || 'neutral'}>{decision}</Badge>;
}
