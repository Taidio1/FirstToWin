import { ReactNode } from 'react';

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-14 text-center">
      {icon && <div className="text-slate-500">{icon}</div>}
      <div>
        <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
        {description && <p className="mt-1 text-xs text-slate-400">{description}</p>}
      </div>
      {action}
    </div>
  );
}
