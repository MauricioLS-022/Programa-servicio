import React from 'react';
import { Icon } from './Icon';

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  helperText?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, error, helperText, className = '', id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={selectId}
            className="text-xs font-semibold uppercase tracking-wider text-text-main dark:text-[#d4c2bf]"
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center w-full">
          <select
            ref={ref}
            id={selectId}
            className={`w-full appearance-none rounded-lg border bg-white dark:bg-[#150f10] text-text-main dark:text-[#f8f2f0] text-sm transition-all duration-200 py-2.5 pl-3.5 pr-10 outline-none focus:ring-2 focus:ring-vino/30 focus:border-vino dark:focus:border-vino-light cursor-pointer ${
              error
                ? 'border-red-500 focus:border-red-500 focus:ring-red-200 dark:focus:ring-red-950'
                : 'border-border-subtle dark:border-[#382628]'
            } ${className}`}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <span
            className="pointer-events-none absolute right-3 flex items-center justify-center text-text-muted dark:text-[#d4c2bf]"
            aria-hidden="true"
          >
            <Icon name="expand_more" size={20} />
          </span>
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

Select.displayName = 'Select';
