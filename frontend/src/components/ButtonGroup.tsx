import React, { ReactNode } from 'react';

export interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical' | 'responsive';
  spacing?: 'sm' | 'md' | 'lg';
  alignment?: 'start' | 'center' | 'end' | 'stretch';
}

/**
 * Componente ButtonGroup para agrupar botões de forma responsiva
 * Em dispositivos móveis, pode transformar automaticamente botões horizontais em verticais
 */
const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className = '',
  orientation = 'responsive',
  spacing = 'md',
  alignment = 'end'
}) => {
  const getOrientationClass = () => {
    switch (orientation) {
      case 'horizontal':
        return 'btn-group-horizontal';
      case 'vertical':
        return 'btn-group-vertical';
      case 'responsive':
      default:
        return 'btn-group-responsive';
    }
  };

  const getSpacingClass = () => {
    switch (spacing) {
      case 'sm':
        return 'btn-group-spacing-sm';
      case 'lg':
        return 'btn-group-spacing-lg';
      case 'md':
      default:
        return 'btn-group-spacing-md';
    }
  };

  const getAlignmentClass = () => {
    switch (alignment) {
      case 'start':
        return 'btn-group-start';
      case 'center':
        return 'btn-group-center';
      case 'stretch':
        return 'btn-group-stretch';
      case 'end':
      default:
        return 'btn-group-end';
    }
  };

  return (
    <div className={`btn-group ${getOrientationClass()} ${getSpacingClass()} ${getAlignmentClass()} ${className}`}>
      {children}
    </div>
  );
};

export default ButtonGroup; 