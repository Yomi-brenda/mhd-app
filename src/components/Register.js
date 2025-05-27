// import React, { useState } from 'react';
//    import axios from 'axios';
//    import { useHistory } from 'react-router-dom';

//    const Register = () => {
//      const [formData, setFormData] = useState({ username: '', email: '', password: '' });
//      const [error, setError] = useState('');
//      const history = useHistory();

//      const handleChange = (e) => {
//        setFormData({ ...formData, [e.target.name]: e.target.value });
//      };

//      const handleSubmit = async (e) => {
//        e.preventDefault();
//        try {
//          console.log('Registering:', formData);
//          const response = await axios.post('http://localhost:8000/register', formData);
//          console.log('Success:', response.data);
//          history.push('/');
//        } catch (err) {
//          console.error('Registration error:', err.response?.data);
//          setError(err.response?.data?.detail || 'Registration failed');
//        }
//      };

//      return (
//        <div className="form-container">
//          <h2>Register</h2>
//          {error && <p className="error">{error}</p>}
//          <div>
//            <div style={{ marginBottom: '1rem' }}>
//              <label>Username</label>
//              <input
//                type="text"
//                name="username"
//                value={formData.username}
//                onChange={handleChange}
//                required
//              />
//            </div>
//            <div style={{ marginBottom: '1rem' }}>
//              <label>Email</label>
//              <input
//                type="email"
//                name="email"
//                value={formData.email}
//                onChange={handleChange}
//                required
//              />
//            </div>
//            <div style={{ marginBottom: '1.5rem' }}>
//              <label>Password</label>
//              <input
//                type="password"
//                name="password"
//                value={formData.password}
//                onChange={handleChange}
//                required
//              />
//            </div>
//            <button onClick={handleSubmit}>Register</button>
//          </div>
//        </div>
//      );
//    };

//    export default Register;



import React, { useState } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { useHistory, Link } from 'react-router-dom';
import axios from 'axios';
import { theme } from '../styles/theme';
import { Button } from '../components/ui_styled/Button';
import { UserPlus, Eye, EyeOff, Mail, User, Lock } from 'lucide-react';

// Styled Components
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
  width: 100%;
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
  transform: translateY(-50%);
  color: ${({ theme }) => theme.colors.textLight};

  @media (max-width: 480px) {
    left: ${({ theme }) => theme.spacing.sm};
  }
`;

const PasswordToggle = styled.button`
  position: absolute;
  right: ${({ theme }) => theme.spacing.md};
  top: 70%;
  transform: translateY(-50%);
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

const PasswordStrength = styled.div`
  margin-top: ${({ theme }) => theme.spacing.xs};
  height: 4px;
  background-color: ${({ theme }) => theme.colors.borderLight};
  border-radius: 2px;
  overflow: hidden;
`;

const StrengthBar = styled.div`
  height: 100%;
  width: ${({ strength }) => strength}%;
  background-color: ${({ theme, strength }) => 
    strength < 25 ? theme.colors.error :
    strength < 50 ? theme.colors.warning :
    strength < 75 ? theme.colors.primaryLight :
    theme.colors.success};
  transition: width 0.3s ease, background-color 0.3s ease;
`;

const Register = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '', password2: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const history = useHistory();

  const calculatePasswordStrength = (password) => {
    if (!password) return 0;
    let strength = 0;
    strength += Math.min(password.length / 12 * 40, 40);
    const hasLower = /[a-z]/.test(password);
    const hasUpper = /[A-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[^a-zA-Z0-9]/.test(password);
    const varietyCount = [hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length;
    strength += (varietyCount / 4) * 60;
    return Math.min(Math.round(strength), 100);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    const newErrors = {};
    if (formData.password !== formData.password2) {
      newErrors.password2 = "Passwords do not match";
    }
    if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setIsLoading(false);
      return;
    }

    try {
      console.log('Registering:', formData);
      await axios.post('http://localhost:8000/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      console.log('Success: Registration completed');
      setIsLoading(false);
      setTimeout(() => history.push('/'), 500);
    } catch (err) {
      console.error('Registration error:', err.response?.data);
      setIsLoading(false);
      if (err.response?.data?.detail) {
        setErrors({ general: err.response.data.detail });
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    }
  };

  const passwordStrength = calculatePasswordStrength(formData.password);

  return (
    <ThemeProvider theme={theme}>
      <PageWrapper>
        <FormContainer>
          <Title>
            <UserPlus size={24} /> Create Account
          </Title>
          <form onSubmit={handleSubmit}>
            {errors.general && <ErrorText>{errors.general}</ErrorText>}
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
                placeholder="  Enter your username"
                autoFocus
              />
              {errors.username && <ErrorText>{errors.username}</ErrorText>}
            </InputGroup>
            <InputGroup>
              <Label htmlFor=" email">Email Address</Label>
              <InputIcon>
                <Mail size={18} />
              </InputIcon>
              <Input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                autoComplete="email"
                placeholder="   your@email.com"
              />
              {errors.email && <ErrorText>{errors.email}</ErrorText>}
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
                autoComplete="new-password"
                placeholder="   At least 8 characters"
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </PasswordToggle>
              {errors.password && <ErrorText>{errors.password}</ErrorText>}
              <PasswordStrength>
                <StrengthBar strength={passwordStrength} />
              </PasswordStrength>
            </InputGroup>
            <InputGroup>
              <Label htmlFor="password2">Confirm Password</Label>
              <InputIcon>
                <Lock size={18} />
              </InputIcon>
              <Input
                type={showConfirmPassword ? "text" : "password"}
                id="password2"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                required
                autoComplete="new-password"
                placeholder="   Confirm your password"
              />
              <PasswordToggle
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </PasswordToggle>
              {errors.password2 && <ErrorText>{errors.password2}</ErrorText>}
            </InputGroup>
            <Button
              type="submit"
              size="lg"
              variant="primary"
              style={{ width: '100%' }}
              disabled={isLoading}
            >
              {isLoading ? 'Creating account...' : (
                <>
                  <UserPlus size={18} style={{ marginRight: theme.spacing.xs }} />
                  Sign Up
                </>
              )}
            </Button>
          </form>
          <OptionsText>
            Already have an account? <Link to="/">Log In</Link>
          </OptionsText>
        </FormContainer>
      </PageWrapper>
    </ThemeProvider>
  );
};

export default Register;