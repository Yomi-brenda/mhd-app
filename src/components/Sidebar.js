import React from 'react';
import styled from 'styled-components';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Users, 
  Calendar, 
  MessageSquare, 
  LifeBuoy, 
  Settings, 
  LogOut,
  Bot,
  BookOpen,
  HeartHandshake
} from 'lucide-react';
import { useHistory } from 'react-router-dom';

const SidebarContainer = styled.aside`
  width: 280px;
  min-height: 100vh;
  background-color: ${({ theme }) => theme.colors.surface};
  border-right: 1px solid ${({ theme }) => theme.colors.borderLight};
  position: fixed;
  top: 0;
  left: 0;
  padding: ${({ theme }) => theme.spacing.lg} 0;
  display: flex;
  flex-direction: column;
  z-index: 90;
  transition: transform 0.3s ease;
  
  @media (max-width: 1024px) {
    transform: ${({ isOpen }) => isOpen ? 'translateX(0)' : 'translateX(-100%)'};
    box-shadow: ${({ theme }) => theme.boxShadowHover};
  }
`;

const SidebarHeader = styled.div`
  padding: 0 ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`;

const Logo = styled.h2`
  font-size: ${({ theme }) => theme.fontSizes.xl};
  font-weight: 700;
  color: ${({ theme }) => theme.colors.primary};
  font-family: ${({ theme }) => theme.fonts.heading};
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  
  svg {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const NavList = styled.ul`
  flex-grow: 1;
  padding: 0 ${({ theme }) => theme.spacing.sm};
`;

const NavItem = styled.li`
  margin-bottom: ${({ theme }) => theme.spacing.xs};
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  border-radius: ${({ theme }) => theme.borderRadius};
  color: ${({ theme, $isActive }) => $isActive ? theme.colors.primary : theme.colors.textMedium};
  font-weight: ${({ $isActive }) => $isActive ? '500' : '400'};
  background-color: ${({ theme, $isActive }) => $isActive ? theme.colors.primaryLightest : 'transparent'};
  transition: ${({ theme }) => theme.transition};
  
  &:hover {
    background-color: ${({ theme, $isActive }) => !$isActive && theme.colors.primaryLightest};
    color: ${({ theme }) => theme.colors.primary};
  }
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const SidebarFooter = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
  border-top: 1px solid ${({ theme }) => theme.colors.borderLight};
`;

const MobileToggle = styled.button`
  position: fixed;
  bottom: ${({ theme }) => theme.spacing.lg};
  left: ${({ theme }) => theme.spacing.lg};
  background-color: ${({ theme }) => theme.colors.primary};
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  box-shadow: ${({ theme }) => theme.boxShadow};
  border: none;
  cursor: pointer;
  
  @media (min-width: 1025px) {
    display: none;
  }
`;

export const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();
  const history = useHistory();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    localStorage.removeItem('lastMentalState');
    history.push('/login');
    setIsOpen(false);
  };

  const navItems = [
    { path: '/dashboard', icon: <Home size={20} />, label: 'Dashboard' },
    { path: '/community', icon: <Users size={20} />, label: 'Community' },
    { path: '/chatbot', icon: <Bot size={20} />, label: 'Mental Health Chat' },
    { path: '/resources', icon: <BookOpen size={20} />, label: 'Resources' },
    { path: '/therapy', icon: <HeartHandshake size={20} />, label: 'Therapy Sessions' },
    { path: '/events', icon: <Calendar size={20} />, label: 'My Events' },
    { path: '/support', icon: <LifeBuoy size={20} />, label: 'Support' },
  ];

  const bottomItems = [
    { path: '/settings', icon: <Settings size={20} />, label: 'Settings' },
    { path: '/logout', icon: <LogOut size={20} />, label: 'Logout', onClick: handleLogout },
  ];

  return (
    <>
      <SidebarContainer isOpen={isOpen}>
        <SidebarHeader>
          <Logo>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            MindWell
          </Logo>
        </SidebarHeader>
        
        <NavList>
          {navItems.map((item) => (
            <NavItem key={item.path}>
              <NavLink 
                to={item.path} 
                $isActive={location.pathname === item.path}
                onClick={() => setIsOpen(false)}
              >
                {item.icon}
                {item.label}
              </NavLink>
            </NavItem>
          ))}
        </NavList>
        
        <SidebarFooter>
          {bottomItems.map((item) => (
            <NavItem key={item.path}>
              <NavLink 
                to={item.path} 
                $isActive={location.pathname === item.path}
                onClick={(e) => {
                  if (item.onClick) {
                    e.preventDefault();
                    item.onClick();
                  } else {
                    setIsOpen(false);
                  }
                }}
              >
                {item.icon}
                {item.label}
              </NavLink>
            </NavItem>
          ))}
        </SidebarFooter>
      </SidebarContainer>
      
      <MobileToggle onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        )}
      </MobileToggle>
    </>
  );
};