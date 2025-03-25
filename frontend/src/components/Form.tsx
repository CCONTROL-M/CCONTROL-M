import React, { ReactNode } from 'react';

export interface FormProps {
  children: ReactNode;
  onSubmit: (e: React.FormEvent) => void;
  className?: string;
  layout?: 'grid' | 'row' | 'column';
  gap?: 'sm' | 'md' | 'lg';
  actions?: ReactNode;
  actionPosition?: 'start' | 'end' | 'center' | 'stretch';
}

/**
 * Componente Form reutilizável e responsivo
 * Fornece uma estrutura consistente para todos os formulários da aplicação
 */
const Form: React.FC<FormProps> = ({
  children,
  onSubmit,
  className = '',
  layout = 'column',
  gap = 'md',
  actions,
  actionPosition = 'end'
}) => {
  const getLayoutClass = () => {
    switch (layout) {
      case 'grid':
        return 'form-grid';
      case 'row':
        return 'form-row';
      case 'column':
      default:
        return 'form-column';
    }
  };

  const getGapClass = () => {
    switch (gap) {
      case 'sm':
        return 'gap-sm';
      case 'lg':
        return 'gap-lg';
      case 'md':
      default:
        return 'gap-md';
    }
  };

  const getActionPositionClass = () => {
    switch (actionPosition) {
      case 'start':
        return 'justify-start';
      case 'center':
        return 'justify-center';
      case 'stretch':
        return 'justify-stretch';
      case 'end':
      default:
        return 'justify-end';
    }
  };

  return (
    <form
      onSubmit={onSubmit}
      className={`form-container ${getLayoutClass()} ${getGapClass()} ${className}`}
    >
      <div className="form-fields">{children}</div>
      
      {actions && (
        <div className={`form-actions ${getActionPositionClass()}`}>
          {actions}
        </div>
      )}
    </form>
  );
};

export default Form; 