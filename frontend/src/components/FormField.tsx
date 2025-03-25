import React, { ChangeEvent } from 'react';

export interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  value: string | number;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  placeholder?: string;
  required?: boolean;
  step?: string;
  helperText?: string;
  disabled?: boolean;
  min?: number;
  width?: 'full' | 'half' | 'third' | 'auto';
  className?: string;
}

/**
 * Componente de campo de formulário padronizado
 * Utiliza as variáveis CSS globais para estilização consistente
 */
const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  placeholder = '',
  required = false,
  step,
  helperText,
  disabled = false,
  min,
  width = 'full',
  className = '',
}) => {
  const getWidthClass = () => {
    switch (width) {
      case 'half':
        return 'form-field-half';
      case 'third':
        return 'form-field-third';
      case 'auto':
        return 'form-field-auto';
      case 'full':
      default:
        return 'form-field-full';
    }
  };

  return (
    <div className={`form-field ${getWidthClass()} ${className}`}>
      <label htmlFor={name}>
        {label}
        {required && <span className="required">*</span>}
      </label>
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={error ? 'input-error' : ''}
        step={step}
        disabled={disabled}
        min={min}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${name}-error` : helperText ? `${name}-helper` : undefined}
      />
      {helperText && (
        <div className="helper-text" id={`${name}-helper`}>
          {helperText}
        </div>
      )}
      {error && (
        <div className="form-field-error" id={`${name}-error`}>
          {error}
        </div>
      )}
    </div>
  );
};

export default FormField; 