// import React, { useState } from 'react';
// import axios from 'axios';
// import { useHistory } from 'react-router-dom';

// const Login = ({ setToken }) => {
//   const [formData, setFormData] = useState({ username: '', password: '' });
//   const [error, setError] = useState('');
//   const history = useHistory();

//   const handleChange = (e) => {
//     setFormData({ ...formData, [e.target.name]: e.target.value });
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const response = await axios.post('http://localhost:8000/token', formData, {
//         headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//       });
//       const token = response.data.access_token;
//       localStorage.setItem('token', token);
//       setToken(token);
//       history.push('/dashboard');
//     } catch (err) {
//       setError(err.response?.data?.detail || 'Login failed');
//     }
//   };

//   return (
//     <div className="form-container">
//       <h2>Login</h2>
//       {error && <p className="error">{error}</p>}
//       <div>
//         <div style={{ marginBottom: '1rem' }}>
//           <label>Username</label>
//           <input
//             type="text"
//             name="username"
//             value={formData.username}
//             onChange={handleChange}
//             required
//           />
//         </div>
//         <div style={{ marginBottom: '1.5rem' }}>
//           <label>Password</label>
//           <input
//             type="password"
//             name="password"
//             value={formData.password}
//             onChange={handleChange}
//             required
//           />
//         </div>
//         <button onClick={handleSubmit}>Login</button>
//       </div>
//     </div>
//   );
// };

// export default Login;

import React, { useState } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { useHistory, Link } from 'react-router-dom';
import axios from 'axios';
import { theme } from '../styles/theme';
import { Button } from './ui_styled/Button';
import { LogIn, Eye, EyeOff, Lock, User } from 'lucide-react';

const PageWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: ${({ theme }) => theme.spacing.md};
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primaryLight} 0%, ${({ theme }) => theme.colors.background} 100%);
  font-family: ${({ theme }) => theme.fonts.main};

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.sm};
  }
`;

const FormContainer = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  padding: ${({ theme }) => theme.spacing.xl};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  box-shadow: ${({ theme }) => theme.boxShadowHover};
  max-width: 420px;
  width: 90%;
  text-align: center;
  animation: fadeIn 0.5s ease;

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
    max-width: 100%;
    margin: 0 ${({ theme }) => theme.spacing.sm};
  }
`;

const Title = styled.h1`
  color: ${({ theme }) => theme.colors.primary};
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  font-size: ${({ theme }) => theme.fontSizes.xxl};
  font-family: ${({ theme }) => theme.fonts.heading};
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xl};
  }
`;

const InputGroup = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  text-align: left;
  position: relative;

  @media (max-width: 480px) {
    margin-bottom: ${({ theme }) => theme.spacing.md};
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${({ theme }) => theme.spacing.xs};
  color: ${({ theme }) => theme.colors.textMedium};
  font-weight: 500;
  font-size: ${({ theme }) => theme.fontSizes.sm};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
  }
`;

const Input = styled.input`
  width: 100%;
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  padding-left: ${({ theme }) => theme.spacing.xl};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius};
  font-size: ${({ theme }) => theme.fontSizes.base};
  box-sizing: border-box;
  transition: all 0.3s ease;
  background-color: ${({ theme }) => theme.colors.surfaceLight};

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    outline: none;
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.primaryLight};
  }

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
    padding-left: ${({ theme }) => theme.spacing.lg};
  }
`;

const InputIcon = styled.div`
  position: absolute;
  left: ${({ theme }) => theme.spacing.md};
  top: 70%;
  transform: translateY(-40%);
  color: ${({ theme }) => theme.colors.textLight};

  @media (max-width: 480px) {
    left: ${({ theme }) => theme.spacing.sm};
  }
`;

const PasswordToggle = styled.button`
  position: absolute;
  right: ${({ theme }) => theme.spacing.md};
  top: 70%;
  transform: translateY(-40%);
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.textLight};
  cursor: pointer;
  padding: ${({ theme }) => theme.spacing.xs};

  @media (max-width: 480px) {
    right: ${({ theme }) => theme.spacing.sm};
  }
`;

const ErrorText = styled.p`
  color: ${({ theme }) => theme.colors.error};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  margin-top: -${({ theme }) => theme.spacing.sm};
  margin-bottom: ${({ theme }) => theme.spacing.md};
  min-height: 1.2em;
  text-align: left;

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
  }
`;

const OptionsText = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  font-size: ${({ theme }) => theme.fontSizes.sm};
  margin-top: ${({ theme }) => theme.spacing.lg};

  a {
    color: ${({ theme }) => theme.colors.primary};
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: ${({ theme }) => theme.spacing.xxs};

    &:hover {
      color: ${({ theme }) => theme.colors.primaryDark};
      text-decoration: underline;
    }
  }

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
  }
`;

const Login = ({ setToken }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const history = useHistory();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      console.log('Logging in:', formData);
      const response = await axios.post('http://192.168.1.111:8000/token', new URLSearchParams(formData), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      console.log('Success:', response.data);
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      localStorage.setItem('userData', JSON.stringify({ username: formData.username }));
      setToken(token);
      setIsLoading(false);
      history.push('/dashboard');
    } catch (err) {
      setIsLoading(false);
      console.error('Login error:', err.response?.data);
      let errorMessage = 'Login failed. Please check your credentials.';
      if (err.response) {
        if (err.response.status === 401) {
          errorMessage = 'Invalid username or password';
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        }
      } else if (err.message === 'Network Error') {
        errorMessage = 'Network error. Please check your connection.';
      }
      setError(errorMessage);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <PageWrapper>
        <FormContainer>
          <Title>
            <Lock size={24} /> Sign In
          </Title>
          <form onSubmit={handleSubmit}>
            <InputGroup>
              <Label htmlFor="username">Username</Label>
              <InputIcon>
                <User size={18} />
              </InputIcon>
              <Input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                autoComplete="username"
                placeholder="Enter your username"
              />
            </InputGroup>
            <InputGroup>
              <Label htmlFor="password">Password</Label>
              <InputIcon>
                <Lock size={18} />
              </InputIcon>
              <Input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                autoComplete="current-password"
                placeholder="Enter your password"
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </PasswordToggle>
            </InputGroup>
            {error && <ErrorText>{error}</ErrorText>}
            <Button
              type="submit"
              size="lg"
              variant="primary"
              style={{ width: '100%' }}
              disabled={isLoading}
            >
              {isLoading ? (
                'Logging in...'
              ) : (
                <>
                  <LogIn size={18} style={{ marginRight: theme.spacing.xs }} />
                  Login
                </>
              )}
            </Button>
          </form>
          <OptionsText>
            Don't have an account? <Link to="/register">Sign Up</Link>
          </OptionsText>
        </FormContainer>
      </PageWrapper>
    </ThemeProvider>
  );
};

export default Login;