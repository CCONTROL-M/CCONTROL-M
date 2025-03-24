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
}

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
}) => {
  return (
    <div className="form-field">
      <label htmlFor={name}>{label}{required && <span className="required">*</span>}</label>
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
      />
      {helperText && <div className="helper-text">{helperText}</div>}
      {error && <div className="form-field-error">{error}</div>}
    </div>
  );
};

export default FormField; 