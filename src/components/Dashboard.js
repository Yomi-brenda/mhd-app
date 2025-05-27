import React, { useState, useEffect } from 'react';
import styled, { keyframes, css, ThemeProvider } from 'styled-components';
import { useHistory, Link } from 'react-router-dom';
import EmergencyButton from './EmergencyButton';
import { Settings, Sun, Moon, LogOut, Activity, MessageSquare, BookOpen, Users, BriefcaseMedical, Zap, ArrowRight, Clock, CheckCircle, ChevronRight } from 'lucide-react';
import SymptomCheckerPage from './SymptomCheckerPage';
import { theme } from '../styles/theme';
import { Button } from './ui_styled/Button';

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.03); }
  100% { transform: scale(1); }
`;

const PageWrapper = styled.div`
  min-height: 100vh;
  background-color: ${({ theme }) => theme.colors.background};
  font-family: ${({ theme }) => theme.fonts.main};
  display: flex;
  flex-direction: column;
  transition: background-color 0.3s ease;

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.sm};
  }
`;

const WidgetCard = styled.div`
  background-color: ${({ theme, bgColor }) => bgColor || theme.colors.surface};
  color: ${({ theme, textColor }) => textColor || theme.colors.text};
  padding: ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  box-shadow: ${({ theme }) => theme.boxShadow};
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: ${({ theme }) => theme.boxShadowHover};
    &::after { opacity: 0.1; }
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: ${({ theme }) => theme.colors.white};
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  svg {
    margin-bottom: ${({ theme }) => theme.spacing.md};
    height: 32px;
    width: 32px;
    color: ${({ theme, iconColor }) => iconColor || theme.colors.primary};
  }

  h3 {
    font-size: ${({ theme }) => theme.fontSizes.lg};
    font-weight: 600;
    font-family: ${({ theme }) => theme.fonts.heading};
    margin-bottom: ${({ theme }) => theme.spacing.xs};
    color: inherit;
  }

  p {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    color: ${({ theme, textColor }) => textColor ? theme.colors.white + 'CC' : theme.colors.textLight};
    line-height: ${({ theme }) => theme.lineHeights.body};
    flex-grow: 1;
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
    svg { height: 24px; width: 24px; }
    h3 { font-size: ${({ theme }) => theme.fontSizes.md}; }
    p { font-size: ${({ theme }) => theme.fontSizes.xxs}; }
  }
`;

const WidgetProgress = styled.div`
  width: 100%;
  height: 4px;
  background-color: ${({ theme }) => theme.colors.borderLight};
  border-radius: 2px;
  margin-top: ${({ theme }) => theme.spacing.md};
  overflow: hidden;

  &::before {
    content: '';
    display: block;
    height: 100%;
    width: ${({ progress }) => progress}%;
    background-color: ${({ theme, progressColor }) => progressColor || theme.colors.primary};
    border-radius: 2px;
    transition: width 0.5s ease;
  }
`;

const StatusIndicator = styled.span`
  display: inline-flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.xxs} ${({ theme }) => theme.spacing.sm};
  border-radius: ${({ theme }) => theme.borderRadius};
  background-color: ${({ status, theme }) =>
    status === 'High Concern' ? theme.colors.errorLight :
    status === 'Moderate Concern' ? theme.colors.warningLight :
    theme.colors.successLight};
  color: ${({ status, theme }) =>
    status === 'High Concern' ? theme.colors.errorDark :
    status === 'Moderate Concern' ? theme.colors.warningDark :
    theme.colors.successDark};
  font-weight: 600;
  font-size: ${({ theme }) => theme.fontSizes.sm};
  margin-left: ${({ theme }) => theme.spacing.sm};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
    padding: ${({ theme }) => theme.spacing.xxs} ${({ theme }) => theme.spacing.xs};
  }
`;

const RecentActivity = styled.div`
  background-color: ${({ theme }) => theme.colors.surfaceLight};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  padding: ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.boxShadow};

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
  }
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.md} 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.borderLight};

  &:last-child { border-bottom: none; }

  svg {
    margin-right: ${({ theme }) => theme.spacing.md};
    color: ${({ theme }) => theme.colors.primary};
  }

  div {
    flex-grow: 1;
    h4 {
      font-weight: 500;
      color: ${({ theme }) => theme.colors.primary};
      font-size: ${({ theme }) => theme.fontSizes.base};
      margin-bottom: ${({ theme }) => theme.spacing.xxs};
    }
    p {
      font-size: ${({ theme }) => theme.fontSizes.sm};
      color: ${({ theme }) => theme.colors.textLight};
    }
  }

  time {
    font-size: ${({ theme }) => theme.fontSizes.xs};
    color: ${({ theme }) => theme.colors.textLight};
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.sm} 0;
    svg { width: 16px; height: 16px; }
    div h4 { font-size: ${({ theme }) => theme.fontSizes.sm}; }
    div p, time { font-size: ${({ theme }) => theme.fontSizes.xxs}; }
  }
`;

const AnimatedButton = styled(Button).attrs({
  variant: 'primary',
  size: 'lg'
})`
  ${({ theme }) => css`
    background-color: ${theme.colors.white};
    color: ${theme.colors.primaryDark};
    margin-top: ${theme.spacing.md};
    font-weight: 600;
    box-shadow: ${theme.boxShadow};
    animation: ${pulse} 2s infinite;

    &:hover {
      transform: translateY(-1px);
      box-shadow: ${theme.boxShadowHover};
    }

    svg { margin-left: ${theme.spacing.xs}; }
  `}

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    padding: ${({ theme }) => theme.spacing.sm};
  }
`;

const HeaderBar = styled.header`
  background-color: ${({ theme }) => theme.colors.white};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: ${({ theme }) => theme.spacing.md} 0;

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.sm} 0;
  }
`;

const Container = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 ${({ theme }) => theme.spacing.md};

  @media (max-width: 480px) {
    padding: 0 ${({ theme }) => theme.spacing.sm};
  }
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;

  @media (max-width: 480px) {
    flex-direction: column;
    gap: ${({ theme }) => theme.spacing.sm};
  }
`;

const LogoStyled = styled(Link)`
  font-size: ${({ theme }) => theme.fontSizes.xl};
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: none;
  font-family: ${({ theme }) => theme.fonts.heading};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.lg};
  }
`;

const HeaderActions = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.sm};

  @media (max-width: 480px) {
    gap: ${({ theme }) => theme.spacing.xs};
  }
`;

const ThemeToggleButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.text};
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.backgroundLight};
  }

  svg { width: 20px; height: 20px; }

  @media (max-width: 480px) {
    width: 32px;
    height: 32px;
    svg { width: 16px; height: 16px; }
  }
`;

const Main = styled.main`
  flex: 1;
  padding: ${({ theme }) => theme.spacing.xl} 0;

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md} 0;
  }
`;

const WelcomeBanner = styled.div`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary}, ${({ theme }) => theme.colors.secondary});
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  padding: ${({ theme }) => theme.spacing.xl};
  color: ${({ theme }) => theme.colors.white};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.boxShadow};

  h1 {
    font-size: ${({ theme }) => theme.fontSizes.xxl};
    font-weight: 700;
    margin-bottom: ${({ theme }) => theme.spacing.xs};
    font-family: ${({ theme }) => theme.fonts.heading};
  }

  p {
    font-size: ${({ theme }) => theme.fontSizes.md};
    opacity: 0.9;
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
    h1 { font-size: ${({ theme }) => theme.fontSizes.xl}; }
    p { font-size: ${({ theme }) => theme.fontSizes.sm}; }
  }
`;

const SectionTitle = styled.h2`
  font-size: ${({ theme }) => theme.fontSizes.xl};
  font-weight: 600;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.heading};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.lg};
  }
`;

const WidgetsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.xl};

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: ${({ theme }) => theme.spacing.md};
  }
`;

const RecommendationsCard = styled.div`
  background-color: ${({ theme }) => theme.colors.white};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  box-shadow: ${({ theme }) => theme.boxShadow};
  margin-bottom: ${({ theme }) => theme.spacing.xl};

  h3 {
    font-size: ${({ theme }) => theme.fontSizes.lg};
    font-weight: 600;
    margin-bottom: ${({ theme }) => theme.spacing.md};
    font-family: ${({ theme }) => theme.fonts.heading};
  }

  @media (max-width: 480px) {
    h3 { font-size: ${({ theme }) => theme.fontSizes.md}; }
  }
`;

const RecommendationItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.md} 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.borderLight};
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:last-child { border-bottom: none; }

  &:hover {
    background-color: ${({ theme }) => theme.colors.backgroundLight};
  }

  h4 {
    font-weight: 500;
    margin-bottom: ${({ theme }) => theme.spacing.xxs};
    color: ${({ theme }) => theme.colors.primary};
    font-size: ${({ theme }) => theme.fontSizes.base};
  }

  p {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    color: ${({ theme }) => theme.colors.textLight};
  }

  svg { color: ${({ theme }) => theme.colors.textLight}; }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.sm} 0;
    h4 { font-size: ${({ theme }) => theme.fontSizes.sm}; }
    p { font-size: ${({ theme }) => theme.fontSizes.xxs}; }
    svg { width: 16px; height: 16px; }
  }
`;

const DialogOverlay = styled.div`
  display: ${({ open }) => open ? 'block' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;

  @media (max-width: 480px) {
    background-color: rgba(0, 0, 0, 0.7);
  }
`;

const DialogWrapper = styled.div`
  display: ${({ open }) => open ? 'block' : 'none'};
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  z-index: 101;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);

  @media (max-width: 480px) {
    width: 95%;
    padding: ${({ theme }) => theme.spacing.md};
    max-height: 85vh;
  }
`;

const DialogScrollableContent = styled.div`
  max-height: 75vh;
  overflow-y: auto;
  padding: ${({ theme }) => theme.spacing.md};

  @media (max-width: 480px) {
    max-height: 70vh;
    padding: ${({ theme }) => theme.spacing.sm};
  }
`;

const getTimeBasedGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
};

const DashboardPage = () => {
  const [showSymptomCheckerDialog, setShowSymptomCheckerDialog] = useState(false);
  const [mentalState, setMentalState] = useState(localStorage.getItem('lastMentalState') || undefined);
  const [username, setUsername] = useState("Patricia");
  const [currentTheme, setCurrentTheme] = useState('light');
  const history = useHistory();

  const [recentActivity, setRecentActivity] = useState([
    {
      id: 1,
      title: "Completed Wellness Check-in",
      description: "You reported feeling Moderate Concern",
      icon: <CheckCircle />,
      time: "2 hours ago"
    },
    {
      id: 2,
      title: "Read article on mindfulness",
      description: "5-minute meditation techniques",
      icon: <BookOpen />,
      time: "Yesterday"
    }
  ]);

  const [widgetProgress] = useState({
    checkIn: 75,
    resources: 30,
    community: 10
  });

  useEffect(() => {
    const storedUserData = localStorage.getItem('userData');
    if (storedUserData) {
      try {
        const user = JSON.parse(storedUserData);
        setUsername(user.first_name || user.username || "User");
      } catch (e) { console.error("Error parsing user data for dashboard:", e); }
    }

    const lastState = localStorage.getItem('lastMentalState');
    if (lastState) {
      setMentalState(lastState);
    }

    const savedTheme = localStorage.getItem('theme') || 'light';
    setCurrentTheme(savedTheme);
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark-theme-active');
    }
  }, []);

  const handleSymptomCheckerComplete = (result) => {
    const { label } = analyzeAnswersForDashboard(result.answers);
    setMentalState(label);
    localStorage.setItem('lastMentalState', label);

    setRecentActivity(prev => [
      {
        id: Date.now(),
        title: "Completed Wellness Check-in",
        description: `You reported feeling ${label}`,
        icon: <CheckCircle />,
        time: "Just now"
      },
      ...prev.slice(0, 4)
    ]);

    setShowSymptomCheckerDialog(false);
  };

  const analyzeAnswersForDashboard = (answers) => {
    if (!answers || Object.keys(answers).length === 0) return { label: "Awaiting Check-in" };
    let score = 0;
    Object.values(answers).forEach(answer => {
      if (typeof answer === 'string') {
        if (answer.includes('Terrible') || answer.includes('Nearly every day') || answer.includes('Almost constantly') || answer.includes('Almost completely') || answer.includes('Severe difficulty')) score += 2;
        else if (answer.includes('Not great') || answer.includes('More than half the days') || answer.includes('Frequently') || answer.includes('Considerably') || answer.includes('Moderate difficulty')) score += 1;
      }
    });
    if (score >= 4) return { label: "High Concern" };
    if (score >= 2) return { label: "Moderate Concern" };
    return { label: "Feeling Okay" };
  };

  const toggleTheme = () => {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setCurrentTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark-theme-active');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    localStorage.removeItem('lastMentalState');
    history.push("/login");
  };

  const widgetsData = [
    {
      title: "Symptom Check-in",
      description: mentalState ? `Last check-in: ${mentalState}` : "How are you feeling today?",
      icon: <Activity />,
      action: () => setShowSymptomCheckerDialog(true),
      bgColor: theme.colors.secondaryLight,
      textColor: theme.colors.secondaryDark,
      iconColor: theme.colors.secondaryDark,
      progress: widgetProgress.checkIn,
      progressColor: theme.colors.secondary
    },
    {
      title: "AI Chat Support",
      description: "Talk to our supportive AI assistant.",
      icon: <MessageSquare />,
      path: "/chatbot",
      bgColor: theme.colors.primaryLight,
      textColor: theme.colors.primaryDark,
      iconColor: theme.colors.primaryDark
    },
    {
      title: "Wellness Resources",
      description: "Articles, meditations, and tools.",
      icon: <BookOpen />,
      path: "/resources",
      bgColor: theme.colors.accentLight,
      textColor: theme.colors.accentDark,
      iconColor: theme.colors.accentDark,
      progress: widgetProgress.resources,
      progressColor: theme.colors.accent
    },
    {
      title: "Community Hub",
      description: "Connect with peers and find support.",
      icon: <Users />,
      path: "/community",
      bgColor: '#E9D5FF',
      textColor: '#6B46C1',
      iconColor: '#6B46C1',
      progress: widgetProgress.community,
      progressColor: '#6B46C1'
    },
    {
      title: "Find a Professional",
      description: "Book a session with a psychologist.",
      icon: <BriefcaseMedical />,
      path: "/psychologists",
      bgColor: '#FED7D7',
      textColor: '#9B2C2C',
      iconColor: '#9B2C2C'
    },
  ];

  return (
    <ThemeProvider theme={theme}>
      <PageWrapper>
        <HeaderBar>
          <Container>
            <HeaderContent>
              <LogoStyled to="/dashboard">MindWell</LogoStyled>
              <HeaderActions>
                <ThemeToggleButton onClick={toggleTheme}>
                  {currentTheme === 'light' ? <Moon /> : <Sun />}
                </ThemeToggleButton>
                <Button variant="ghost" size="icon" onClick={() => history.push("/settings")} title="Settings">
                  <Settings />
                </Button>
                <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                  <LogOut />
                </Button>
              </HeaderActions>
            </HeaderContent>
          </Container>
        </HeaderBar>

        <Main>
          <Container>
            <WelcomeBanner>
              <h1>{getTimeBasedGreeting()}, {username}!</h1>
              {mentalState ? (
                <p>
                  Your current status:
                  <StatusIndicator status={mentalState}>
                    {mentalState}
                  </StatusIndicator>
                </p>
              ) : (
                <p>Welcome to your mental wellness space. How are you feeling today?</p>
              )}
              <AnimatedButton
                onClick={() => setShowSymptomCheckerDialog(true)}
              >
                Start Wellness Check-in <Zap />
              </AnimatedButton>
            </WelcomeBanner>

            <SectionTitle>Quick Access</SectionTitle>
            <WidgetsGrid>
              {widgetsData.map((widget) => (
                <WidgetCard
                  key={widget.title}
                  onClick={widget.action ? widget.action : () => history.push(widget.path)}
                  bgColor={widget.bgColor}
                  textColor={widget.textColor}
                  iconColor={widget.iconColor}
                >
                  {React.cloneElement(widget.icon, { color: widget.iconColor || theme.colors.primary })}
                  <h3>{widget.title}</h3>
                  <p>{widget.description}</p>
                  {widget.progress && (
                    <WidgetProgress
                      progress={widget.progress}
                      progressColor={widget.progressColor}
                    />
                  )}
                </WidgetCard>
              ))}
            </WidgetsGrid>

            <RecentActivity>
              <h3 style={{ marginBottom: theme.spacing.lg }}>Recent Activity</h3>
              {recentActivity.map(activity => (
                <ActivityItem key={activity.id}>
                  {activity.icon}
                  <div>
                    <h4>{activity.title}</h4>
                    <p>{activity.description}</p>
                  </div>
                  <time>{activity.time}</time>
                </ActivityItem>
              ))}
            </RecentActivity>

            <RecommendationsCard as="section">
              <h3 style={{padding: `${theme.spacing.md} ${theme.spacing.lg} 0` }}>Recommended For You</h3>
              <div style={{padding: `0 ${theme.spacing.lg} ${theme.spacing.md}` }}>
                <RecommendationItem onClick={() => history.push('/resources')}>
                  <div><h4>Article: Managing Daily Stress</h4><p>Tips for a calmer day.</p></div>
                  <ChevronRight />
                </RecommendationItem>
                <RecommendationItem onClick={() => history.push('/resources')}>
                  <div><h4>Meditation: 5-Minute Mindful Break</h4><p>Quick reset for your mind.</p></div>
                  <ChevronRight />
                </RecommendationItem>
              </div>
            </RecommendationsCard>
          </Container>
        </Main>

        <EmergencyButton />

        <DialogOverlay open={showSymptomCheckerDialog} onClick={() => setShowSymptomCheckerDialog(false)} />
        <DialogWrapper open={showSymptomCheckerDialog}>
          <DialogScrollableContent>
            {showSymptomCheckerDialog && <SymptomCheckerPage onComplete={handleSymptomCheckerComplete} isDialogMode={true} />}
          </DialogScrollableContent>
        </DialogWrapper>
      </PageWrapper>
    </ThemeProvider>
  );
};

export default DashboardPage;