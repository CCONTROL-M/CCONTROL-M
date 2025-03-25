import React, { ReactNode, ButtonHTMLAttributes } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'warning' | 'success';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  className?: string;
}

/**
 * Componente Button padronizado e responsivo
 * Permite aplicar variações de estilo, tamanho e comportamentos de forma consistente
 */
const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  iconPosition = 'left',
  loading = false,
  className = '',
  ...rest
}) => {
  const getButtonClass = () => {
    const classes = [`btn-${variant}`];
    
    if (size !== 'md') {
      classes.push(`btn-${size}`);
    }
    
    if (fullWidth) {
      classes.push('btn-full-width');
    }
    
    if (loading) {
      classes.push('btn-loading');
    }
    
    if (className) {
      classes.push(className);
    }
    
    return classes.join(' ');
  };
  
  const renderIcon = () => {
    if (!icon) return null;
    return <span className="btn-icon">{icon}</span>;
  };
  
  const renderContent = () => {
    if (loading) {
      return (
        <>
          <span className="btn-spinner"></span>
          <span className="btn-loading-text">{children}</span>
        </>
      );
    }
    
    if (!icon) return children;
    
    return (
      <>
        {iconPosition === 'left' && renderIcon()}
        <span>{children}</span>
        {iconPosition === 'right' && renderIcon()}
      </>
    );
  };
  
  return (
    <button 
      className={getButtonClass()} 
      disabled={loading || rest.disabled}
      {...rest}
    >
      {renderContent()}
    </button>
  );
};

export default Button; 