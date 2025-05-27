import React from 'react';
import styled, { keyframes, ThemeProvider } from 'styled-components';
import { Link } from 'react-router-dom';
import { theme } from '../styles/theme';
import { Button } from '../components/ui_styled/Button';
import { Heart, ArrowRight } from 'lucide-react';
import logoImage from '../assets/images/zenlogo.png';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const wave = keyframes`
  0% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0); }
`;

const PageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: ${({ theme }) => theme.spacing.xxl} ${({ theme }) => theme.spacing.md};
  background: linear-gradient(135deg, #e0f2fe 0%, #d1fae5 100%);
  text-align: center;
  font-family: ${({ theme }) => theme.fonts.main};
  color: ${({ theme }) => theme.colors.text};
  position: relative;
  overflow: hidden;

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.lg} ${({ theme }) => theme.spacing.sm};
  }

`;

const HeroSection = styled.section`
  max-width: 800px;
  width: 90%;
  animation: ${fadeIn} 0.8s ease-out;

  @media (max-width: 480px) {
    width: 95%;
  }
`;

const Logo = styled.img`
  width: 500px;
  height: auto;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  animation: ${wave} 2s ease-in-out infinite;

  @media (max-width: 480px) {
    width: 300px;
  }
`;

const Title = styled.h1`
  color: ${({ theme }) => theme.colors.primaryDark};
  font-size: ${({ theme }) => theme.fontSizes.xxxl};
  font-family: ${({ theme }) => theme.fonts.heading};
  font-weight: 700;
  line-height: ${({ theme }) => theme.lineHeights.heading};
  margin-bottom: ${({ theme }) => theme.spacing.md};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (max-width: 768px) {
    font-size: ${({ theme }) => theme.fontSizes.xxl};
  }
  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xl};
  }
`;

const Subtitle = styled.p`
  color: ${({ theme }) => theme.colors.textMedium};
  font-size: ${({ theme }) => theme.fontSizes.lg};
  line-height: ${({ theme }) => theme.lineHeights.body};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  max-width: 600px;

  @media (max-width: 768px) {
    font-size: ${({ theme }) => theme.fontSizes.md};
    max-width: 90%;
  }
  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    max-width: 100%;
    padding: 0 ${({ theme }) => theme.spacing.sm};
  }
`;

const CTAButton = styled(Button)`
  display: inline-flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xs};
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-2px);
  }
  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    padding: ${({ theme }) => theme.spacing.sm};
  }
`;

const BackgroundShape = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%23ffffff' fill-opacity='0.3' d='M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") no-repeat bottom;

  @media (max-width: 480px) {
    height: 100px;
  }
`;

const HomePage = () => {
  return (
    <ThemeProvider theme={theme}>
      <PageWrapper>
        <BackgroundShape />
        <HeroSection>
          <Logo src={logoImage} alt="ZEN Logo" />
          <Title>
            Welcome to ZEN <Heart size={28} color="#dc2626" />
          </Title>
          <Subtitle>
            Your safe space for mental health support. Access resources, connect with peers, and find professional help anytime, anywhere.
          </Subtitle>
          <CTAButton size="lg" variant="primary" as={Link} to="/login">
            Get Started <ArrowRight size={18} />
          </CTAButton>
        </HeroSection>
      </PageWrapper>
    </ThemeProvider>
  );
};

export default HomePage;