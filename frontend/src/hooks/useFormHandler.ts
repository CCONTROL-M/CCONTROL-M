import { useState, ChangeEvent } from 'react';

/**
 * Hook para gerenciar formulários de forma centralizada
 * 
 * @param initialValues - Valores iniciais do formulário
 * @returns Um objeto com estado do formulário, erros, e funções para manipulação
 */
export function useFormHandler<T extends Record<string, any>>(initialValues: T) {
  const [formData, setFormData] = useState<T>(initialValues);
  const [formErrors, setFormErrors] = useState<Partial<Record<keyof T, string>>>({});

  // Função genérica para lidar com mudanças em campos do formulário
  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    // Converter o valor para o tipo apropriado
    let parsedValue: any = value;
    
    if (type === 'number') {
      parsedValue = value === '' ? '' : Number(value);
    } else if (type === 'checkbox') {
      parsedValue = (e.target as HTMLInputElement).checked;
    }
    
    // Atualizar o estado do formulário
    setFormData(prev => ({
      ...prev,
      [name]: parsedValue
    }));

    // Limpar o erro do campo quando o usuário digita
    if (formErrors[name as keyof T]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  // Função para validar campos específicos
  const validateField = (field: keyof T, rules: { required?: boolean, minLength?: number, maxLength?: number, pattern?: RegExp, custom?: (value: any) => string | undefined }) => {
    const value = formData[field];
    
    // Verificar regra de campo obrigatório
    if (rules.required && (value === undefined || value === null || value === '')) {
      return 'Este campo é obrigatório';
    }
    
    // Verificar tamanho mínimo
    if (rules.minLength && typeof value === 'string' && value.length < rules.minLength) {
      return `Este campo deve ter pelo menos ${rules.minLength} caracteres`;
    }
    
    // Verificar tamanho máximo
    if (rules.maxLength && typeof value === 'string' && value.length > rules.maxLength) {
      return `Este campo deve ter no máximo ${rules.maxLength} caracteres`;
    }
    
    // Verificar padrão (regex)
    if (rules.pattern && typeof value === 'string' && !rules.pattern.test(value)) {
      return 'Formato inválido';
    }
    
    // Verificar regra personalizada
    if (rules.custom) {
      return rules.custom(value);
    }
    
    return undefined;
  };

  // Função para validar o formulário inteiro
  const validate = (validationRules: Record<keyof T, any>) => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;
    
    // Validar cada campo usando as regras fornecidas
    for (const field in validationRules) {
      const error = validateField(field, validationRules[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    }
    
    setFormErrors(newErrors);
    return isValid;
  };

  // Função para resetar o formulário
  const resetForm = () => {
    setFormData(initialValues);
    setFormErrors({});
  };

  return { 
    formData, 
    setFormData, 
    formErrors, 
    setFormErrors, 
    handleInputChange, 
    validate,
    resetForm
  };
}

export default useFormHandler; 