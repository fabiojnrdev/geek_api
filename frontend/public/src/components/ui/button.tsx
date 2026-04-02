// src/components/ui/Button.tsx
import React from 'react';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantClasses: Record<Variant, string> = {
  primary: 'bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-600/20',
  secondary: 'bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700',
  danger: 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/20',
  ghost: 'bg-transparent hover:bg-zinc-800 text-zinc-300 hover:text-white',
  outline: 'bg-transparent border border-violet-500 text-violet-400 hover:bg-violet-500/10',
};

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs rounded-lg',
  md: 'px-4 py-2 text-sm rounded-xl',
  lg: 'px-6 py-3 text-base rounded-xl',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  ...props
}) => (
  <button
    className={`
      inline-flex items-center justify-center gap-2 font-semibold
      transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-500/50
      disabled:opacity-50 disabled:cursor-not-allowed
      ${variantClasses[variant]} ${sizeClasses[size]} ${className}
    `}
    disabled={disabled || isLoading}
    {...props}
  >
    {isLoading ? (
      <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
    ) : leftIcon}
    {children}
    {!isLoading && rightIcon}
  </button>
);

// ─── Badge ───────────────────────────────────────────────────
type BadgeColor = 'violet' | 'green' | 'red' | 'yellow' | 'blue' | 'zinc';

interface BadgeProps { color?: BadgeColor; children: React.ReactNode; className?: string; }

const badgeColors: Record<BadgeColor, string> = {
  violet: 'bg-violet-500/20 text-violet-300 ring-1 ring-violet-500/30',
  green: 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/30',
  red: 'bg-red-500/20 text-red-300 ring-1 ring-red-500/30',
  yellow: 'bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/30',
  blue: 'bg-blue-500/20 text-blue-300 ring-1 ring-blue-500/30',
  zinc: 'bg-zinc-700/50 text-zinc-400 ring-1 ring-zinc-600/50',
};

export const Badge: React.FC<BadgeProps> = ({ color = 'violet', children, className = '' }) => (
  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${badgeColors[color]} ${className}`}>
    {children}
  </span>
);

// ─── Input ───────────────────────────────────────────────────
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({ label, error, leftIcon, className = '', ...props }) => (
  <div className="flex flex-col gap-1.5">
    {label && <label className="text-sm font-medium text-zinc-300">{label}</label>}
    <div className="relative">
      {leftIcon && (
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500">{leftIcon}</span>
      )}
      <input
        className={`
          w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-2.5 text-sm text-zinc-100
          placeholder:text-zinc-600 focus:outline-none focus:border-violet-500 focus:ring-1
          focus:ring-violet-500/30 transition-colors
          ${leftIcon ? 'pl-10' : ''}
          ${error ? 'border-red-500 focus:border-red-500' : ''}
          ${className}
        `}
        {...props}
      />
    </div>
    {error && <span className="text-xs text-red-400">{error}</span>}
  </div>
);

// ─── Card ────────────────────────────────────────────────────
export const Card: React.FC<{ children: React.ReactNode; className?: string; onClick?: () => void }> = ({
  children, className = '', onClick
}) => (
  <div
    onClick={onClick}
    className={`
      bg-zinc-900 border border-zinc-800 rounded-2xl
      ${onClick ? 'cursor-pointer hover:border-violet-500/50 transition-colors' : ''}
      ${className}
    `}
  >
    {children}
  </div>
);

// ─── Spinner ─────────────────────────────────────────────────
export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const s = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={`${s} border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin`} />
  );
};

// ─── Empty State ─────────────────────────────────────────────
export const EmptyState: React.FC<{ icon?: string; title: string; description?: string; action?: React.ReactNode }> = ({
  icon = '📭', title, description, action
}) => (
  <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
    <span className="text-5xl mb-4">{icon}</span>
    <h3 className="text-lg font-semibold text-zinc-200 mb-2">{title}</h3>
    {description && <p className="text-sm text-zinc-500 max-w-sm mb-6">{description}</p>}
    {action}
  </div>
);