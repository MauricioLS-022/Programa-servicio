import React, { useState } from 'react';
import { Icon } from './Icon';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, icon, type = 'text', className = '', id, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-semibold uppercase tracking-wider text-text-main dark:text-[#d4c2bf]"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute left-3.5 text-text-muted dark:text-[#d4c2bf] pointer-events-none flex items-center justify-center">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            className={`w-full rounded-lg border bg-white dark:bg-[#150f10] text-text-main dark:text-[#f8f2f0] placeholder:text-text-muted/60 dark:placeholder:text-[#a89f9e] text-sm transition-all duration-200 py-2.5 outline-none focus:ring-2 focus:ring-vino/30 focus:border-vino dark:focus:border-vino-light ${
              icon ? 'pl-10' : 'pl-3.5'
            } ${isPassword ? 'pr-10' : 'pr-3.5'} ${
              error
                ? 'border-red-500 focus:border-red-500 focus:ring-red-200 dark:focus:ring-red-950'
                : 'border-border-subtle dark:border-[#382628]'
            } ${className}`}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 text-text-muted hover:text-text-main dark:text-[#d4c2bf] dark:hover:text-[#f8f2f0] p-0.5 rounded cursor-pointer transition-colors focus:outline-none"
              tabIndex={-1}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
            >
              {showPassword ? <Icon name="visibility_off" size={16} /> : <Icon name="visibility" size={16} />}
            </button>
          )}
        </div>
        {error ? (
          <p className="text-xs text-red-600 dark:text-red-400 font-medium">{error}</p>
        ) : helperText ? (
          <p className="text-xs text-text-muted dark:text-[#d4c2bf]">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
