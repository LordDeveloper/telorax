import styled, { css } from 'styled-components'

const toneStyles = {
  neutral: css`
    background: ${({ theme }) => theme.colors.surfaceOverlay};
    color: ${({ theme }) => theme.colors.muted};
    border-color: ${({ theme }) => theme.colors.border};
  `,
  success: css`
    background: rgba(61, 214, 140, 0.1);
    color: ${({ theme }) => theme.colors.success};
    border-color: rgba(61, 214, 140, 0.3);
  `,
  warning: css`
    background: rgba(245, 165, 36, 0.1);
    color: ${({ theme }) => theme.colors.warning};
    border-color: rgba(245, 165, 36, 0.3);
  `,
  danger: css`
    background: rgba(247, 101, 101, 0.1);
    color: ${({ theme }) => theme.colors.danger};
    border-color: rgba(247, 101, 101, 0.3);
  `,
  accent: css`
    background: rgba(42, 171, 238, 0.1);
    color: ${({ theme }) => theme.colors.accentGlow};
    border-color: rgba(42, 171, 238, 0.3);
  `,
}

export const PageWrap = styled.div`
  animation: fadeIn 0.35s ease-out;
`

export const Badge = styled.span`
  display: inline-flex;
  align-items: center;
  border: 1px solid;
  border-radius: ${({ theme }) => theme.radii.full};
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 500;
  ${({ $tone = 'neutral' }) => toneStyles[$tone]}
`

export const MethodBadge = styled.span`
  display: inline-flex;
  min-width: 3.5rem;
  justify-content: center;
  border: 1px solid;
  border-radius: ${({ theme }) => theme.radii.sm};
  padding: 4px 8px;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 12px;
  font-weight: 600;
  ${({ $tone = 'neutral' }) => toneStyles[$tone]}
`

export function MethodBadgeView({ method }) {
  const tone =
    method === 'GET' ? 'success' : method === 'POST' ? 'accent' : method === 'DELETE' ? 'danger' : 'warning'
  return <MethodBadge $tone={tone}>{method}</MethodBadge>
}

export const Card = styled.div`
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.xl};
  background: rgba(18, 26, 46, 0.8);
  backdrop-filter: blur(8px);
  box-shadow: ${({ $glow, theme }) => ($glow ? theme.shadows.glow : theme.shadows.card)};
  padding: ${({ $padding = '0' }) => $padding};
  transition: border-color 0.2s ease;

  &:hover {
    ${({ $hoverable }) =>
      $hoverable &&
      css`
        border-color: rgba(42, 171, 238, 0.3);
      `}
  }
`

export const CodeBlock = styled.pre`
  overflow-x: auto;
  margin: 0;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 16px;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  line-height: 1.6;
  color: #e2e8f0;
`

export const GhostButton = styled.button`
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.sm};
  background: ${({ theme }) => theme.colors.surfaceOverlay};
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.muted};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(42, 171, 238, 0.4);
    color: ${({ theme }) => theme.colors.white};
  }
`

export function CopyButton({ value, label = 'Copy' }) {
  return (
    <GhostButton type="button" onClick={() => navigator.clipboard.writeText(value)}>
      {label}
    </GhostButton>
  )
}

export const FieldWrap = styled.div`
  margin-bottom: 6px;
`

export const FieldLabelText = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: #e2e8f0;
`

export const FieldHint = styled.p`
  margin: 2px 0 0;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.muted};
`

export const RequiredMark = styled.span`
  margin-left: 4px;
  color: ${({ theme }) => theme.colors.danger};
`

export function FieldLabel({ label, hint, required }) {
  return (
    <FieldWrap>
      <FieldLabelText>
        {label}
        {required ? <RequiredMark>*</RequiredMark> : null}
      </FieldLabelText>
      {hint ? <FieldHint>{hint}</FieldHint> : null}
    </FieldWrap>
  )
}

export const SectionHeadingWrap = styled.div`
  margin-bottom: 32px;
  animation: slideUp 0.4s ease-out;
`

export const Eyebrow = styled.p`
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: ${({ theme }) => theme.colors.accentGlow};
`

export const PageTitle = styled.h1`
  margin: 0;
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 700;
  color: ${({ theme }) => theme.colors.white};
`

export const PageDescription = styled.p`
  margin: 12px 0 0;
  max-width: 42rem;
  font-size: 16px;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.muted};
`

export function SectionHeading({ eyebrow, title, description }) {
  return (
    <SectionHeadingWrap>
      {eyebrow ? <Eyebrow>{eyebrow}</Eyebrow> : null}
      <PageTitle>{title}</PageTitle>
      {description ? <PageDescription>{description}</PageDescription> : null}
    </SectionHeadingWrap>
  )
}

export const Input = styled.input`
  width: 100%;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 12px 16px;
  font-family: ${({ $mono, theme }) => ($mono ? theme.fonts.mono : theme.fonts.sans)};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.white};
  outline: none;

  &:focus {
    border-color: rgba(42, 171, 238, 0.5);
    box-shadow: 0 0 0 3px rgba(42, 171, 238, 0.15);
  }

  text-transform: ${({ $uppercase }) => ($uppercase ? 'uppercase' : 'none')};
`

export const Select = styled.select`
  width: 100%;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 12px 16px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.white};
  outline: none;

  &:focus {
    border-color: rgba(42, 171, 238, 0.5);
    box-shadow: 0 0 0 3px rgba(42, 171, 238, 0.15);
  }
`

export const TextArea = styled.textarea`
  width: 100%;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 12px 16px;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.white};
  outline: none;
  resize: vertical;

  &:focus {
    border-color: rgba(42, 171, 238, 0.5);
    box-shadow: 0 0 0 3px rgba(42, 171, 238, 0.15);
  }
`

export const PrimaryButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: none;
  border-radius: ${({ theme }) => theme.radii.md};
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.accent}, ${({ theme }) => theme.colors.indigo});
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
  box-shadow: ${({ theme }) => theme.shadows.glow};
  cursor: pointer;

  &:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

export const SpinIcon = styled.span`
  display: inline-flex;
  animation: spin 1s linear infinite;
`

export const Grid2 = styled.div`
  display: grid;
  gap: 24px;

  @media (min-width: ${({ theme }) => theme.breakpoints.xl}) {
    grid-template-columns: 1fr 1fr;
  }
`

export const GridResponsive = styled.div`
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
`

export const Stack = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ $gap = '16px' }) => $gap};
`

export const Row = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
`

export const InlineCode = styled.code`
  font-family: ${({ theme }) => theme.fonts.mono};
  color: ${({ theme }) => theme.colors.white};
`

export const MutedText = styled.p`
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.muted};
`

export const SubTitle = styled.h2`
  margin: 0 0 16px;
  font-size: 20px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

export const SubHeading = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

export const ErrorBox = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border: 1px solid rgba(247, 101, 101, 0.3);
  border-radius: ${({ theme }) => theme.radii.md};
  background: rgba(247, 101, 101, 0.1);
  padding: 16px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.danger};
`

export const EmptyState = styled.div`
  border: 1px dashed ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  padding: 48px 24px;
  text-align: center;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.muted};
`

export const InfoPanel = styled.div`
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 12px 16px;
`

export const PanelLabel = styled.p`
  margin: 0 0 4px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: ${({ theme }) => theme.colors.muted};
`

export const PanelValue = styled.p`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

export const IconBox = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-bottom: 16px;
  border-radius: ${({ theme }) => theme.radii.md};
  background: rgba(42, 171, 238, 0.1);
  color: ${({ theme }) => theme.colors.accentGlow};
`

export const StepNumber = styled.span`
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(42, 171, 238, 0.15);
  font-size: 12px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.accentGlow};
`

export const StepList = styled.ol`
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
`

export const StepItem = styled.li`
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.muted};
`

export const StatusText = styled.span`
  font-size: 14px;
  color: ${({ $ok, theme }) => ($ok ? theme.colors.success : theme.colors.danger)};
`

export const DurationText = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.muted};
`

export const SectionBlock = styled.section`
  margin-top: 40px;
`

export const TwoColGrid = styled.div`
  display: grid;
  gap: 24px;

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    grid-template-columns: 1fr 1fr;
  }
`

export const FormGrid = styled.div`
  display: grid;
  gap: 16px;

  @media (min-width: ${({ theme }) => theme.breakpoints.sm}) {
    grid-template-columns: 1fr 1fr;
  }
`

export const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
`

export const UpperLabel = styled.h3`
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: ${({ theme }) => theme.colors.muted};
`

export const FieldCard = styled.div`
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.codeBg};
  padding: 12px 16px;
`

export const FieldName = styled.code`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

export const FieldType = styled.span`
  margin-left: 8px;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.muted};
`

export const HighlightTitle = styled.h3`
  margin: 0 0 8px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

export const NavTextLink = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.accentGlow};
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: ${({ theme }) => theme.colors.white};
  }
`

export const FadeIn = styled.div`
  animation: fadeIn 0.35s ease-out;
`

export const ResponseHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`

export const CurlHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`
