import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ThemeProvider } from 'styled-components';
import { useHistory } from 'react-router-dom';
import EmergencyButton from './EmergencyButton';
import { Search, BookOpen, PlayCircle, Wrench, XCircle } from 'lucide-react';
import { theme } from '../styles/theme';
import { Button } from './ui_styled/Button';
import { Sidebar } from './Sidebar';

// Styled Components
const PageWrapper = styled.div`
  min-height: 100vh;
  background: ${({ theme }) => theme.colors.background};
  font-family: ${({ theme }) => theme.fonts.main};
  margin-left: 280px;
  padding: ${({ theme }) => theme.spacing.lg} 0;
  
  @media (max-width: 1024px) {
    margin-left: 0;
    padding: ${({ theme }) => theme.spacing.md} 0;
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

const HeroSection = styled.div`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary}, ${({ theme }) => theme.colors.secondary});
  color: ${({ theme }) => theme.colors.white};
  padding: ${({ theme }) => theme.spacing.xl};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  text-align: center;
  box-shadow: ${({ theme }) => theme.boxShadow};

  h2 {
    font-size: ${({ theme }) => theme.fontSizes.xxl};
    font-weight: 700;
    font-family: ${({ theme }) => theme.fonts.heading};
    margin-bottom: ${({ theme }) => theme.spacing.sm};
  }
  
  p {
    font-size: ${({ theme }) => theme.fontSizes.md};
    opacity: 0.9;
    max-width: 700px;
    margin: 0 auto;
  }
  
  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
    h2 { font-size: ${({ theme }) => theme.fontSizes.xl}; }
    p { font-size: ${({ theme }) => theme.fontSizes.sm}; }
  }
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.surfaceLight};
  border-radius: ${({ theme }) => theme.borderRadius};
  padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  max-width: 400px;
  
  @media (max-width: 768px) {
    max-width: 100%;
  }
`;

const SearchInput = styled.input`
  border: none;
  background: transparent;
  padding: ${({ theme }) => theme.spacing.xs};
  width: 100%;
  color: ${({ theme }) => theme.colors.textMedium};
  font-family: ${({ theme }) => theme.fonts.main};
  font-size: ${({ theme }) => theme.fontSizes.base};
  
  &:focus {
    outline: none;
  }

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
  }
`;

const TabsWrapper = styled.div`
  width: 100%;
`;

const TabsListStyled = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.xs};
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  background-color: ${({ theme }) => theme.colors.surfaceLight};
  padding: ${({ theme }) => theme.spacing.xs};
  border-radius: ${({ theme }) => theme.borderRadius};
  overflow-x: auto;
  
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: ${({ theme }) => theme.colors.borderLight};
    border-radius: 2px;
  }

  @media (max-width: 480px) {
    gap: ${({ theme }) => theme.spacing.xxs};
    padding: ${({ theme }) => theme.spacing.xxs};
  }
`;

const TabTriggerStyled = styled.button`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  font-size: ${({ theme }) => theme.fontSizes.base};
  font-weight: 500;
  cursor: pointer;
  border: none;
  white-space: nowrap;
  text-align: center;
  background-color: ${({ theme, $isActive }) => $isActive ? theme.colors.primary : 'transparent'};
  color: ${({ theme, $isActive }) => $isActive ? theme.colors.white : theme.colors.primaryDark};
  border-radius: ${({ theme }) => theme.borderRadius};
  transition: background-color 0.2s ease, color 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xs};

  &:hover:not(:disabled) {
    background-color: ${({ theme, $isActive }) => !$isActive && theme.colors.primaryLightest};
    color: ${({ theme, $isActive }) => !$isActive && theme.colors.primaryDark};
  }

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
  }
`;

const TabContentStyled = styled.div`
  padding-top: ${({ theme }) => theme.spacing.md};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${({ theme }) => theme.spacing.lg};
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: ${({ theme }) => theme.spacing.md};
  }
`;

const ResourceCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  box-shadow: ${({ theme }) => theme.boxShadow};
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid ${({ theme }) => theme.colors.borderLight};

  &:hover {
    transform: translateY(-5px);
    box-shadow: ${({ theme }) => theme.boxShadowHover};
  }
`;

const ResourceImageWrapper = styled.div`
  height: 180px;
  position: relative;
  background-color: ${({ theme }) => theme.colors.borderLight};
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  @media (max-width: 480px) {
    height: 140px;
  }
`;

const ResourceCategoryBadge = styled.div`
  position: absolute;
  top: ${({ theme }) => theme.spacing.sm};
  left: ${({ theme }) => theme.spacing.sm};
  background-color: rgba(0,0,0,0.6);
  color: white;
  padding: ${({ theme }) => theme.spacing.xxs} ${({ theme }) => theme.spacing.xs};
  font-size: ${({ theme }) => theme.fontSizes.xs};
  border-radius: ${({ theme }) => theme.borderRadius};
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xxs};
  text-transform: capitalize;

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
  }
`;

const ResourceHeader = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
`;

const ResourceTitle = styled.h3`
  font-size: ${({ theme }) => theme.fontSizes.lg};
  font-weight: 600;
  font-family: ${({ theme }) => theme.fonts.heading};
  color: ${({ theme }) => theme.colors.primaryDark};
  margin-bottom: ${({ theme }) => theme.spacing.xs};
  line-height: ${({ theme }) => theme.lineHeights.heading};

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.md};
  }
`;

const ResourceTags = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  display: flex;
  flex-wrap: wrap;
  gap: ${({ theme }) => theme.spacing.xs};
`;

const Tag = styled.span`
  background-color: ${({ theme }) => theme.colors.primaryLightest};
  color: ${({ theme }) => theme.colors.primaryDark};
  padding: 2px 8px;
  border-radius: ${({ theme }) => theme.borderRadius};
  font-size: ${({ theme }) => theme.fontSizes.xs};
  font-weight: 500;

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.xxs};
  }
`;

const ResourceContent = styled.div`
  padding: 0 ${({ theme }) => theme.spacing.md} ${({ theme }) => theme.spacing.md};
  color: ${({ theme }) => theme.colors.textMedium};
  font-size: ${({ theme }) => theme.fontSizes.base};
  line-height: ${({ theme }) => theme.lineHeights.body};
  flex-grow: 1;
  
  p {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  @media (max-width: 480px) {
    font-size: ${({ theme }) => theme.fontSizes.sm};
  }
`;

const ResourceFooter = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
  margin-top: auto;
  border-top: 1px solid ${({ theme }) => theme.colors.borderLight};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${({ theme }) => theme.spacing.xl};
  background-color: ${({ theme }) => theme.colors.surfaceLight};
  border-radius: ${({ theme }) => theme.borderRadius};
  margin: ${({ theme }) => theme.spacing.xl} 0;
  box-shadow: ${({ theme }) => theme.boxShadow};

  p:first-of-type {
    font-size: ${({ theme }) => theme.fontSizes.lg};
    font-weight: 600;
    color: ${({ theme }) => theme.colors.text};
    margin-bottom: ${({ theme }) => theme.spacing.sm};
  }

  p {
    font-size: ${({ theme }) => theme.fontSizes.base};
    color: ${({ theme }) => theme.colors.textLight};
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.lg};
    p:first-of-type { font-size: ${({ theme }) => theme.fontSizes.md}; }
    p { font-size: ${({ theme }) => theme.fontSizes.sm}; }
  }
`;

const DialogOverlay = styled.div`
  display: ${({ open }) => open ? 'block' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 1000;
`;

const DialogWrapper = styled.div`
  display: ${({ open }) => open ? 'block' : 'none'};
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: ${({ theme }) => theme.colors.white};
  padding: ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadiusLarge};
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  z-index: 1001;

  @media (max-width: 480px) {
    width: 95%;
    padding: ${({ theme }) => theme.spacing.md};
    max-height: 80vh;
  }
`;

const DialogHeader = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing.md};
  border-bottom: 1px solid ${({ theme }) => theme.colors.borderLight};
  margin-bottom: ${({ theme }) => theme.spacing.md};
  
  h2 {
    font-size: ${({ theme }) => theme.fontSizes.xl};
    font-weight: 600;
    color: ${({ theme }) => theme.colors.primaryDark};
    font-family: ${({ theme }) => theme.fonts.heading};
  }
  
  p {
    font-size: ${({ theme }) => theme.fontSizes.sm};
    color: ${({ theme }) => theme.colors.textLight};
    margin-top: ${({ theme }) => theme.spacing.xs};
    display: flex;
    align-items: center;
    gap: ${({ theme }) => theme.spacing.sm};
  }

  @media (max-width: 480px) {
    h2 { font-size: ${({ theme }) => theme.fontSizes.lg}; }
    p { font-size: ${({ theme }) => theme.fontSizes.xxs}; }
  }
`;

const DialogContentArea = styled.div`
  overflow-y: auto;
  flex-grow: 1;
  padding-right: ${({ theme }) => theme.spacing.sm};
  line-height: ${({ theme }) => theme.lineHeights.body};
  color: ${({ theme }) => theme.colors.text};
  
  img {
    max-width: 100%;
    height: auto;
    border-radius: ${({ theme }) => theme.borderRadius};
    margin-bottom: ${({ theme }) => theme.spacing.md};
  }
  
  p {
    margin-bottom: ${({ theme }) => theme.spacing.md};
    font-size: ${({ theme }) => theme.fontSizes.base};
  }

  @media (max-width: 480px) {
    padding-right: ${({ theme }) => theme.spacing.xs};
    p { font-size: ${({ theme }) => theme.fontSizes.sm}; }
  }
`;

const DialogFooter = styled.div`
  padding-top: ${({ theme }) => theme.spacing.md};
  margin-top: ${({ theme }) => theme.spacing.md};
  border-top: 1px solid ${({ theme }) => theme.colors.borderLight};
  display: flex;
  justify-content: flex-end;
`;

const AudioPlayerPlaceholder = styled.div`
  background-color: ${({ theme }) => theme.colors.backgroundLight};
  padding: ${({ theme }) => theme.spacing.lg};
  border-radius: ${({ theme }) => theme.borderRadius};
  text-align: center;
  margin-top: ${({ theme }) => theme.spacing.md};
  
  p {
    margin-bottom: ${({ theme }) => theme.spacing.md};
    color: ${({ theme }) => theme.colors.textLight};
    font-size: ${({ theme }) => theme.fontSizes.base};
  }

  @media (max-width: 480px) {
    padding: ${({ theme }) => theme.spacing.md};
    p { font-size: ${({ theme }) => theme.fontSizes.sm}; }
  }
`;

// Mock Data
const initialResources = [
  { 
    id: 1, 
    title: "Mindful Morning Meditation", 
    description: "Start your day with calm and focus. A 10-minute guided session for beginners.", 
    category: 'meditation', 
    tags: ['anxiety', 'morning', 'focus'], 
    audioSrc: "#", 
    imageUrl: 'https://via.placeholder.com/300x180?text=Meditation', 
    duration: "10 min", 
    content: "This guided meditation helps you center yourself and set a positive intention for the day. Find a quiet space, sit comfortably, and allow the gentle guidance to lead you to a state of peaceful awareness. Perfect for reducing morning anxiety and improving focus throughout your day." 
  },
  { 
    id: 2, 
    title: "Understanding Your Emotions", 
    description: "An insightful article on emotional intelligence and self-awareness for better mental health.", 
    category: 'article', 
    tags: ['emotions', 'self-awareness', 'education'], 
    imageUrl: 'https://via.placeholder.com/300x180?text=Article', 
    author: "Dr. Eva Insight", 
    content: "Emotions are powerful signals that guide our thoughts and actions. This article explores how to recognize, understand, and manage your emotions effectively. Developing emotional intelligence can lead to better mental well-being, stronger relationships, and improved decision-making. We delve into practical techniques for self-reflection and emotional regulation." 
  },
  { 
    id: 3, 
    title: "Digital Detox Challenge Tool", 
    description: "A guided tool to help you reduce screen time, improve focus, and reconnect with the present.", 
    category: 'tool', 
    tags: ['digital-wellbeing', 'focus', 'challenge'], 
    toolUrl: "/tools/digital-detox", 
    imageUrl: 'https://via.placeholder.com/300x180?text=Tool', 
    content: "Our Digital Detox Challenge tool provides a structured plan to help you reduce your reliance on digital devices. Improve focus, enhance your connection with the world around you, and discover tips for a healthier digital life. Track your progress and unlock achievements as you build better habits." 
  },
];

const categoryIcons = {
  meditation: <PlayCircle size={18} />,
  article: <BookOpen size={18} />,
  tool: <Wrench size={18} />,
};

const ResourcesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [resources, setResources] = useState(initialResources);
  const [filteredResources, setFilteredResources] = useState(initialResources);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const history = useHistory();

  useEffect(() => {
    let tempFiltered = resources;
    
    // Filter by active tab
    if (activeTab !== 'all') {
      tempFiltered = tempFiltered.filter(r => r.category === activeTab);
    }
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      tempFiltered = tempFiltered.filter(resource => {
        return (
          resource.title.toLowerCase().includes(query) ||
          resource.description.toLowerCase().includes(query) ||
          resource.tags.some(tag => tag.toLowerCase().includes(query))
        );
      });
    }
    
    setFilteredResources(tempFiltered);
  }, [searchQuery, activeTab, resources]);

  const handleResourceOpen = (resource) => {
    setSelectedResource(resource);
    setDialogOpen(true);
  };

  const renderResourceCard = (resource) => (
    <ResourceCard key={resource.id}>
      <ResourceImageWrapper>
        <img src={resource.imageUrl} alt={resource.title} />
        <ResourceCategoryBadge>
          {categoryIcons[resource.category]}
          {resource.category}
        </ResourceCategoryBadge>
      </ResourceImageWrapper>
      <ResourceHeader>
        <ResourceTitle>{resource.title}</ResourceTitle>
        <ResourceTags>
          {resource.tags.slice(0, 3).map((tag) => <Tag key={tag}>{tag}</Tag>)}
        </ResourceTags>
      </ResourceHeader>
      <ResourceContent>
        <p>{resource.description}</p>
      </ResourceContent>
      <ResourceFooter>
        <Button 
          variant="primary" 
          onClick={() => handleResourceOpen(resource)}
          style={{ width: '100%' }}
        >
          {resource.category === 'meditation' ? 'Listen Now' :
           resource.category === 'article' ? 'Read Article' : 'Open Tool'}
        </Button>
      </ResourceFooter>
    </ResourceCard>
  );

  const renderResourceContentInDialog = () => {
    if (!selectedResource) return null;
    return (
      <>
        <DialogHeader>
          <h2>{selectedResource.title}</h2>
          <p>
            {categoryIcons[selectedResource.category]}
            {selectedResource.category}
            {selectedResource.duration && ` • ${selectedResource.duration}`}
            {selectedResource.author && ` • By ${selectedResource.author}`}
          </p>
        </DialogHeader>
        <DialogContentArea>
          <img src={selectedResource.imageUrl} alt={selectedResource.title} />
          <p>{selectedResource.content || "Detailed content will be available here."}</p>
          {selectedResource.category === 'meditation' && (
            <AudioPlayerPlaceholder>
              <p>Audio player will be embedded here.</p>
              <Button variant="secondary">
                <PlayCircle style={{ marginRight: theme.spacing.xs }} /> 
                Play Meditation
              </Button>
            </AudioPlayerPlaceholder>
          )}
          {selectedResource.category === 'tool' && (
            <Button 
              variant="secondary" 
              onClick={() => {
                alert(`Navigating to tool: ${selectedResource.toolUrl}`);
                setDialogOpen(false);
                // history.push(selectedResource.toolUrl); // Uncomment when tool pages exist
              }}
              style={{ width: '100%' }}
            >
              <Wrench style={{ marginRight: theme.spacing.xs }} /> 
              Launch Interactive Tool
            </Button>
          )}
        </DialogContentArea>
      </>
    );
  };

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}>
          <p>Loading resources...</p>
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <PageWrapper>
        <Container>
          <HeroSection>
            <h2>Discover Wellness Resources</h2>
            <p>Explore our collection of meditations, articles, and tools to support your mental health journey.</p>
          </HeroSection>

          <SearchBar>
            <Search size={18} color={theme.colors.textLight} />
            <SearchInput 
              type="text" 
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBar>

          <TabsWrapper>
            <TabsListStyled>
              <TabTriggerStyled 
                $isActive={activeTab === 'all'} 
                onClick={() => setActiveTab('all')}
              >
                All Resources
              </TabTriggerStyled>
              <TabTriggerStyled 
                $isActive={activeTab === 'meditation'} 
                onClick={() => setActiveTab('meditation')}
              >
                <PlayCircle size={16} />
                Meditations
              </TabTriggerStyled>
              <TabTriggerStyled 
                $isActive={activeTab === 'article'} 
                onClick={() => setActiveTab('article')}
              >
                <BookOpen size={16} />
                Articles
              </TabTriggerStyled>
              <TabTriggerStyled 
                $isActive={activeTab === 'tool'} 
                onClick={() => setActiveTab('tool')}
              >
                <Wrench size={16} />
                Tools
              </TabTriggerStyled>
            </TabsListStyled>

            <TabContentStyled>
              {filteredResources.length > 0 ? (
                <Grid>
                  {filteredResources.map(renderResourceCard)}
                </Grid>
              ) : (
                <EmptyState>
                  <Search size={48} style={{ marginBottom: theme.spacing.md, opacity: 0.5 }} />
                  <p>No resources found</p>
                  <p>Try adjusting your search or selected category</p>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSearchQuery('');
                      setActiveTab('all');
                    }}
                    style={{ marginTop: theme.spacing.md }}
                  >
                    Clear Filters
                  </Button>
                </EmptyState>
              )}
            </TabContentStyled>
          </TabsWrapper>
        </Container>

        <DialogOverlay open={dialogOpen} onClick={() => setDialogOpen(false)} />
        <DialogWrapper open={dialogOpen}>
          {renderResourceContentInDialog()}
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setDialogOpen(false)}
            >
              <XCircle style={{ marginRight: theme.spacing.xs }} /> 
              Close
            </Button>
          </DialogFooter>
        </DialogWrapper>
        <EmergencyButton />
      </PageWrapper>
    </ThemeProvider>
  );
};

export default ResourcesPage;