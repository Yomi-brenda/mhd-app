import styled from 'styled-components';

   export const Button = styled.button`
     padding: ${({ theme, size }) => {
       switch (size) {
         case 'lg': return theme.spacing.md;
         case 'md': return `${theme.spacing.sm} ${theme.spacing.md}`;
         default: return theme.spacing.sm;
       }
     }};
     font-size: ${({ theme, size }) => {
       switch (size) {
         case 'lg': return theme.fontSizes.base;
         case 'md': return theme.fontSizes.sm;
         default: return theme.fontSizes.sm;
       }
     }};
     background-color: ${({ theme, variant }) => 
       variant === 'primary' ? theme.colors.primary : theme.colors.borderLight};
     color: ${({ theme, variant }) => 
       variant === 'primary' ? '#ffffff' : theme.colors.textMedium};
     border: ${({ theme, variant }) => 
       variant === 'outline' ? `1px solid ${theme.colors.border}` : 'none'};
     border-radius: ${({ theme }) => theme.borderRadius};
     cursor: pointer;
     transition: all 0.2s ease;
     display: inline-flex;
     align-items: center;
     justify-content: center;

     &:hover {
       background-color: ${({ theme, variant }) => 
         variant === 'primary' ? theme.colors.primaryDark : theme.colors.border};
     }

     &:disabled {
       opacity: 0.6;
       cursor: not-allowed;
     }
   `;