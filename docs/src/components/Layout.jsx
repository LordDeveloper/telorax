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
  position: relative;
  min-height: 100vh;
  background: ${({ theme }) => theme.colors.surface};
  color: ${({ theme }) => theme.colors.text};
`

const GridLayer = styled.div`
  pointer-events: none;
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(${({ theme }) => theme.colors.line} 1px, transparent 1px),
    linear-gradient(90deg, ${({ theme }) => theme.colors.line} 1px, transparent 1px);
  background-size: ${({ theme }) => theme.grid.size} ${({ theme }) => theme.grid.size};
  mask-image: radial-gradient(ellipse 80% 70% at 50% 0%, black 20%, transparent 75%);
  opacity: ${({ theme }) => theme.grid.opacity};
`

const GlowLayer = styled.div`
  pointer-events: none;
  position: fixed;
  inset: 0;
  overflow: hidden;
`

const GlowOrbLeft = styled.div`
  position: absolute;
  top: -80px;
  left: -160px;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(42, 171, 238, 0.14) 0%, transparent 70%);
  filter: blur(40px);
`

const GlowOrbRight = styled.div`
  position: absolute;
  right: -120px;
  bottom: -80px;
  width: 480px;
  height: 480px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(129, 140, 248, 0.12) 0%, transparent 70%);
  filter: blur(40px);
`

const TopLine = styled.div`
  pointer-events: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    ${({ theme }) => theme.colors.borderGlow} 30%,
    ${({ theme }) => theme.colors.accent} 50%,
    ${({ theme }) => theme.colors.borderGlow} 70%,
    transparent
  );
  z-index: 30;
`

const Container = styled.div`
  position: relative;
  display: flex;
  min-height: 100vh;
  max-width: 1440px;
  margin: 0 auto;
`

const Sidebar = styled.aside`
  display: none;
  position: sticky;
  top: 0;
  flex-direction: column;
  width: 280px;
  height: 100vh;
  flex-shrink: 0;
  padding: 28px 20px;
  border-right: 1px solid ${({ theme }) => theme.colors.border};
  background: rgba(7, 11, 20, 0.82);
  backdrop-filter: blur(20px);
  box-shadow: inset -1px 0 0 ${({ theme }) => theme.colors.lineStrong};

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    display: flex;
  }
`

const BrandRow = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 36px;
  padding-bottom: 24px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`

const BrandIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  border: 1px solid rgba(42, 171, 238, 0.25);
  background: linear-gradient(145deg, rgba(42, 171, 238, 0.2), rgba(129, 140, 248, 0.15));
  box-shadow: ${({ theme }) => theme.shadows.glow}, ${({ theme }) => theme.shadows.inset};
`

const BrandTitle = styled.p`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: ${({ theme }) => theme.colors.white};
`

const BrandSub = styled.p`
  margin: 2px 0 0;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: ${({ theme }) => theme.colors.mutedDim};
`

const SideNav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 2px;
`

const SideNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: 10px;
  border: 1px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.muted};
  text-decoration: none;
  transition: all 0.18s ease;

  &.active {
    border-color: rgba(42, 171, 238, 0.25);
    background: linear-gradient(135deg, rgba(42, 171, 238, 0.12), rgba(129, 140, 248, 0.06));
    color: ${({ theme }) => theme.colors.accentGlow};
    box-shadow: ${({ theme }) => theme.shadows.inset};
  }

  &:hover:not(.active) {
    border-color: ${({ theme }) => theme.colors.border};
    background: ${({ theme }) => theme.colors.surfaceOverlay};
    color: ${({ theme }) => theme.colors.white};
  }
`

const TipCard = styled.div`
  margin-top: auto;
  padding: 16px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 14px;
  background: ${({ theme }) => theme.colors.surfaceRaised};
  box-shadow: ${({ theme }) => theme.shadows.inset};

  &::before {
    content: '';
    display: block;
    height: 1px;
    margin: -16px -16px 14px;
    background: linear-gradient(90deg, transparent, ${({ theme }) => theme.colors.borderStrong}, transparent);
  }
`

const TipTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: 13px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

const TipText = styled.p`
  margin: 0;
  font-size: 12px;
  line-height: 1.65;
  color: ${({ theme }) => theme.colors.muted};

  code {
    font-family: ${({ theme }) => theme.fonts.mono};
    font-size: 11px;
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
  padding: 14px 16px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  background: rgba(7, 11, 20, 0.9);
  backdrop-filter: blur(20px);

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
  border: 1px solid rgba(42, 171, 238, 0.2);
  background: linear-gradient(145deg, rgba(42, 171, 238, 0.18), rgba(129, 140, 248, 0.12));
`

const MobileNav = styled.nav`
  display: flex;
  gap: 8px;
  margin-top: 14px;
  overflow-x: auto;
  padding-bottom: 4px;
`

const MobileNavLink = styled(NavLink)`
  padding: 6px 14px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none;
  color: ${({ theme }) => theme.colors.muted};
  background: ${({ theme }) => theme.colors.surfaceRaised};

  &.active {
    border-color: rgba(42, 171, 238, 0.35);
    background: rgba(42, 171, 238, 0.1);
    color: ${({ theme }) => theme.colors.accentGlow};
  }
`

const MainContent = styled.main`
  flex: 1;
  padding: 28px 16px 48px;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    padding: 36px 32px 56px;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    padding: 44px 48px 64px;
  }
`

export function Layout({ children }) {
  return (
    <Shell>
      <GridLayer />
      <GlowLayer>
        <GlowOrbLeft />
        <GlowOrbRight />
      </GlowLayer>
      <TopLine />

      <Container>
        <Sidebar>
          <BrandRow>
            <BrandIcon>
              <Radio size={20} color="#6ecfff" />
            </BrandIcon>
            <div>
              <BrandTitle>Telorax</BrandTitle>
              <BrandSub>API Reference</BrandSub>
            </div>
          </BrandRow>

          <SideNav>
            {links.map(({ to, label, icon: Icon }) => (
              <SideNavLink key={to} to={to} end={to === '/'}>
                <Icon size={16} strokeWidth={2} />
                {label}
              </SideNavLink>
            ))}
          </SideNav>

          <TipCard>
            <TipTitle>
              <Zap size={15} color="#6ecfff" />
              Playground
            </TipTitle>
            <TipText>
              Send live requests against your instance. Base URL defaults to the current host — set{' '}
              <code>APP_PORT</code> in production.
            </TipText>
          </TipCard>
        </Sidebar>

        <MainColumn>
          <MobileHeader>
            <MobileBrand>
              <MobileIcon>
                <Activity size={18} color="#6ecfff" />
              </MobileIcon>
              <div>
                <BrandTitle style={{ fontSize: '16px' }}>Telorax Docs</BrandTitle>
                <BrandSub style={{ fontSize: '10px' }}>Interactive API</BrandSub>
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
