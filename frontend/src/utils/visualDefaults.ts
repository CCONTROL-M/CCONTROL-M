/**
 * visualDefaults.ts
 * 
 * Este arquivo centraliza todos os tokens visuais padrão utilizados no sistema.
 * Ele serve como fonte única de verdade para cores, espaçamentos, fontes
 * e outros elementos visuais, garantindo consistência em toda a aplicação.
 */

// CORES PRINCIPAIS
export const colors = {
  // Cores primárias
  primary: {
    50: '#e6f0ff',
    100: '#cce0ff',
    200: '#99c0ff',
    300: '#66a0ff',
    400: '#3380ff',
    500: '#0066ff', // Cor principal
    600: '#0052cc',
    700: '#003d99',
    800: '#002966',
    900: '#001433',
  },
  
  // Cores de estado
  success: {
    50: '#e6f7e6',
    100: '#ccefcc',
    200: '#99df99',
    300: '#66cf66',
    400: '#33bf33',
    500: '#00af00', // Cor principal
    600: '#008c00',
    700: '#006900',
    800: '#004600',
    900: '#002300',
  },
  
  danger: {
    50: '#ffe6e6',
    100: '#ffcccc',
    200: '#ff9999',
    300: '#ff6666',
    400: '#ff3333',
    500: '#ff0000', // Cor principal
    600: '#cc0000',
    700: '#990000',
    800: '#660000',
    900: '#330000',
  },
  
  warning: {
    50: '#fff8e6',
    100: '#fff1cc',
    200: '#ffe399',
    300: '#ffd466',
    400: '#ffc633',
    500: '#ffb800', // Cor principal
    600: '#cc9300',
    700: '#996e00',
    800: '#664a00',
    900: '#332500',
  },
  
  info: {
    50: '#e6f6ff',
    100: '#ccedff',
    200: '#99dbff',
    300: '#66c8ff',
    400: '#33b6ff',
    500: '#00a3ff', // Cor principal
    600: '#0082cc',
    700: '#006299',
    800: '#004166',
    900: '#002133',
  },
  
  // Tons de cinza
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  
  // Branco e preto puros
  white: '#ffffff',
  black: '#000000',
};

// TIPOGRAFIA
export const typography = {
  // Família de fontes
  fontFamily: {
    base: 'Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", Oxygen, Ubuntu, Cantarell, "Open Sans", sans-serif',
    mono: 'Roboto Mono, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },
  
  // Tamanhos de fonte
  fontSize: {
    xs: '0.75rem',     // 12px
    sm: '0.875rem',    // 14px
    base: '1rem',      // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },
  
  // Pesos de fonte
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  // Altura de linha
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
  
  // Espaçamento entre letras
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
};

// ESPAÇAMENTOS
export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
};

// TAMANHOS
export const sizes = {
  // Tamanhos de elementos padrão
  elements: {
    button: {
      height: {
        xs: '1.5rem',    // 24px
        sm: '2rem',      // 32px
        md: '2.5rem',    // 40px
        lg: '3rem',      // 48px
        xl: '3.5rem',    // 56px
      },
      minWidth: {
        xs: '4rem',      // 64px
        sm: '6rem',      // 96px
        md: '8rem',      // 128px
        lg: '10rem',     // 160px
        xl: '12rem',     // 192px
      },
    },
    input: {
      height: {
        sm: '2rem',      // 32px
        md: '2.5rem',    // 40px
        lg: '3rem',      // 48px
      },
    },
    modal: {
      width: {
        sm: '20rem',     // 320px
        md: '28rem',     // 448px
        lg: '36rem',     // 576px
        xl: '42rem',     // 672px
        '2xl': '48rem',  // 768px
        full: '100%',
      },
    },
    table: {
      rowHeight: {
        sm: '2rem',      // 32px
        md: '2.5rem',    // 40px
        lg: '3rem',      // 48px
      },
    },
  },
  
  // Breakpoints responsivos
  breakpoints: {
    xs: '20rem',      // 320px
    sm: '36rem',      // 576px
    md: '48rem',      // 768px
    lg: '62rem',      // 992px
    xl: '75rem',      // 1200px
    '2xl': '87.5rem', // 1400px
  },
};

// BORDAS
export const borders = {
  radius: {
    none: '0',
    sm: '0.125rem',    // 2px
    DEFAULT: '0.25rem', // 4px
    md: '0.375rem',    // 6px
    lg: '0.5rem',      // 8px
    xl: '0.75rem',     // 12px
    '2xl': '1rem',     // 16px
    '3xl': '1.5rem',   // 24px
    full: '9999px',
  },
  width: {
    0: '0px',
    1: '1px',
    2: '2px',
    4: '4px',
    8: '8px',
  },
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    none: 'none',
  },
};

// SOMBRAS
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
};

// TRANSIÇÕES E ANIMAÇÕES
export const transitions = {
  timing: {
    DEFAULT: '250ms',
    fast: '150ms',
    slow: '350ms',
  },
  easing: {
    DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)', // ease
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',        // ease-in
    out: 'cubic-bezier(0, 0, 0.2, 1)',       // ease-out
    'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)', // ease-in-out
  },
  properties: {
    all: 'all',
    colors: 'background-color, border-color, color, fill, stroke',
    opacity: 'opacity',
    shadow: 'box-shadow',
    transform: 'transform',
  },
};

// Z-INDEX
export const zIndex = {
  0: '0',
  10: '10',
  20: '20',
  30: '30',
  40: '40',
  50: '50',      // Elementos padrão
  90: '90',      // Dropdown e elementos de menu
  100: '100',    // Headers fixos
  900: '900',    // Modais e drawers
  950: '950',    // Toasts e notificações
  999: '999',    // Máscaras e overlays
  9999: '9999',  // Elementos críticos em fullscreen
};

// Função para acessar tokens aninhados por caminho de string
// Exemplo: getTokenByPath('colors.primary.500') retorna '#0066ff'
export const getTokenByPath = (path: string): any => {
  const parts = path.split('.');
  let result: any = { colors, typography, spacing, sizes, borders, shadows, transitions, zIndex };
  
  for (const part of parts) {
    if (result && result[part] !== undefined) {
      result = result[part];
    } else {
      return undefined;
    }
  }
  
  return result;
};

export default {
  colors,
  typography,
  spacing,
  sizes,
  borders,
  shadows,
  transitions,
  zIndex,
  getTokenByPath,
}; 