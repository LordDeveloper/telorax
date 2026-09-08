import styled from 'styled-components'
import { NavLink } from 'react-router-dom'
import {
  Activity,
  BookOpen,
  Layers3,
  PlayCircle,
  Radio,
  Sparkles,
  Zap,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Overview', icon: Sparkles },
  { to: '/types', label: 'Operation types', icon: Layers3 },
  { to: '/endpoints', label: 'Endpoints', icon: BookOpen },
  { to: '/playground', label: 'Playground', icon: PlayCircle },
]

const Shell = styled.div`
  min-height: 100vh;
  background: ${({ theme }) => theme.colors.surface};
  color: #f1f5f9;
`

const GlowLayer = styled.div`
  pointer-events: none;
  position: fixed;
  inset: 0;
  overflow: hidden;
`

const GlowOrbLeft = styled.div`
  position: absolute;
  top: 0;
  left: -128px;
  width: 384px;
  height: 384px;
  border-radius: 50%;
  background: rgba(42, 171, 238, 0.1);
  filter: blur(80px);
`

const GlowOrbRight = styled.div`
  position: absolute;
  right: 0;
  bottom: 0;
  width: 448px;
  height: 448px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.1);
  filter: blur(80px);
`

const Container = styled.div`
  position: relative;
  display: flex;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
`

const Sidebar = styled.aside`
  display: none;
  position: sticky;
  top: 0;
  flex-direction: column;
  width: 288px;
  height: 100vh;
  flex-shrink: 0;
  padding: 24px;
  border-right: 1px solid rgba(36, 48, 77, 0.8);
  background: rgba(12, 18, 34, 0.7);
  backdrop-filter: blur(16px);

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    display: flex;
  }
`

const BrandRow = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
`

const BrandIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.accent}, ${({ theme }) => theme.colors.indigo});
  box-shadow: ${({ theme }) => theme.shadows.glow};
`

const BrandTitle = styled.p`
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.white};
`

const BrandSub = styled.p`
  margin: 0;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.muted};
`

const SideNav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 4px;
`

const SideNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.muted};
  text-decoration: none;
  transition: all 0.2s ease;

  &.active {
    background: rgba(42, 171, 238, 0.15);
    color: ${({ theme }) => theme.colors.accentGlow};
    box-shadow: ${({ theme }) => theme.shadows.glow};
  }

  &:hover:not(.active) {
    background: ${({ theme }) => theme.colors.surfaceOverlay};
    color: ${({ theme }) => theme.colors.white};
  }
`

const TipCard = styled.div`
  margin-top: auto;
  padding: 16px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  background: ${({ theme }) => theme.colors.surfaceOverlay};
`

const TipTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.white};
`

const TipText = styled.p`
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.muted};

  code {
    font-family: ${({ theme }) => theme.fonts.mono};
    color: ${({ theme }) => theme.colors.accentGlow};
  }
`

const MainColumn = styled.div`
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
`

const MobileHeader = styled.header`
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 16px;
  border-bottom: 1px solid rgba(36, 48, 77, 0.8);
  background: rgba(12, 18, 34, 0.8);
  backdrop-filter: blur(16px);

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    display: none;
  }
`

const MobileBrand = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`

const MobileIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.accent}, ${({ theme }) => theme.colors.indigo});
`

const MobileNav = styled.nav`
  display: flex;
  gap: 8px;
  margin-top: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
`

const MobileNavLink = styled(NavLink)`
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none;
  color: ${({ theme }) => theme.colors.muted};
  background: ${({ theme }) => theme.colors.surfaceOverlay};

  &.active {
    background: rgba(42, 171, 238, 0.2);
    color: ${({ theme }) => theme.colors.accentGlow};
  }
`

const MainContent = styled.main`
  flex: 1;
  padding: 32px 16px;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    padding: 32px;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    padding: 40px;
  }
`

export function Layout({ children }) {
  return (
    <Shell>
      <GlowLayer>
        <GlowOrbLeft />
        <GlowOrbRight />
      </GlowLayer>

      <Container>
        <Sidebar>
          <BrandRow>
            <BrandIcon>
              <Radio size={20} color="white" />
            </BrandIcon>
            <div>
              <BrandTitle>Telorax</BrandTitle>
              <BrandSub>API Reference & Playground</BrandSub>
            </div>
          </BrandRow>

          <SideNav>
            {links.map(({ to, label, icon: Icon }) => (
              <SideNavLink key={to} to={to} end={to === '/'}>
                <Icon size={16} />
                {label}
              </SideNavLink>
            ))}
          </SideNav>

          <TipCard>
            <TipTitle>
              <Zap size={16} color="#5bc0ff" />
              Quick tip
            </TipTitle>
            <TipText>
              Use the playground to send live requests. Dev server proxies <code>/v1</code> to your
              local API on port 8000.
            </TipText>
          </TipCard>
        </Sidebar>

        <MainColumn>
          <MobileHeader>
            <MobileBrand>
              <MobileIcon>
                <Activity size={20} color="white" />
              </MobileIcon>
              <div>
                <BrandTitle style={{ fontSize: '16px' }}>Telorax Docs</BrandTitle>
                <BrandSub>Interactive API reference</BrandSub>
              </div>
            </MobileBrand>
            <MobileNav>
              {links.map(({ to, label }) => (
                <MobileNavLink key={to} to={to} end={to === '/'}>
                  {label}
                </MobileNavLink>
              ))}
            </MobileNav>
          </MobileHeader>

          <MainContent>{children}</MainContent>
        </MainColumn>
      </Container>
    </Shell>
  )
}
