import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
`;

const SymptomCheckerPage = ({ onComplete, isDialogMode }) => {
  const [answers, setAnswers] = useState({});

  const handleComplete = () => {
    onComplete({ answers });
  };

  return (
    <Container>
      <h2>Symptom Checker</h2>
      <button onClick={handleComplete}>Complete</button>
    </Container>
  );
};

export default SymptomCheckerPage;