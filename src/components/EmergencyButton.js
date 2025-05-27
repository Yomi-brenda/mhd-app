import React from 'react';
import styled from 'styled-components';

const Button = styled.button`
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: ${({ theme }) => theme.colors.error};
  color: white;
  padding: 10px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
`;

const EmergencyButton = () => (
  <Button>Emergency</Button>
);

export default EmergencyButton;