import styled from 'styled-components'
import { Link } from 'react-router-dom'
import { ArrowRight, Boxes, Gauge, ListOrdered, Target } from 'lucide-react'
import { ENDPOINTS, OPERATION_TYPES } from '../data/apiReference'
import {
  Card,
  GridResponsive,
  IconBox,
  HighlightTitle,
  InlineCode,
  MutedText,
  NavTextLink,
  PageWrap,
  SectionBlock,
  SectionHeading,
  StepItem,
  StepList,
  StepNumber,
  SubTitle,
  TwoColGrid,
  CodeBlock,
} from '../components/ui'

const highlights = [
  {
    icon: Target,
    title: 'Batch operations',
    text: 'Queue hundreds of Telegram actions with type, quantity, target, and extra params.',
  },
  {
    icon: ListOrdered,
    title: 'Typed payloads',
    text: 'Each OperationType has its own extra schema — View, Subscribe, PollVote, and more.',
  },
  {
    icon: Gauge,
    title: 'Live playground',
    text: 'Send real requests, inspect JSON responses, and copy cURL in one click.',
  },
  {
    icon: Boxes,
    title: 'Progress tracking',
    text: 'Monitor quantity, completed, remaining, and state for every operation.',
  },
]

const TypeLinkCard = styled(Link)`
  display: block;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: rgba(18, 26, 46, 0.6);
  padding: 12px 16px;
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(42, 171, 238, 0.3);
    background: ${({ theme }) => theme.colors.surfaceOverlay};
  }
`

const TypeRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`

const TypeDot = styled.span`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${({ $color }) => $color};
`

const TypeCode = styled.span`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 12px;
  color: ${({ theme }) => theme.colors.muted};
`

const TypeLabel = styled.span`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.white};
`

const EndpointLinkCard = styled(Link)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: rgba(18, 26, 46, 0.4);
  padding: 12px 16px;
  text-decoration: none;
  transition: border-color 0.2s ease;

  &:hover {
    border-color: rgba(42, 171, 238, 0.3);
  }
`

const EndpointPath = styled.p`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

const EndpointTitle = styled.p`
  margin: 4px 0 0;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.muted};
`

const EndpointList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const HighlightGrid = styled.div`
  display: grid;
  gap: 16px;
  margin-bottom: 40px;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    grid-template-columns: 1fr 1fr;
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.xl}) {
    grid-template-columns: repeat(4, 1fr);
  }
`

export function OverviewPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Telorax API"
        title="Control plane for Telegram account operations"
        description="Interactive documentation and API playground. Explore endpoints, learn OperationType codes, and test requests against your running Telorax instance."
      />

      <HighlightGrid>
        {highlights.map(({ icon: Icon, title, text }) => (
          <Card key={title} $padding="20px" $hoverable>
            <IconBox>
              <Icon size={20} />
            </IconBox>
            <HighlightTitle>{title}</HighlightTitle>
            <MutedText>{text}</MutedText>
          </Card>
        ))}
      </HighlightGrid>

      <TwoColGrid>
        <Card $padding="24px">
          <SubTitle>Quick start</SubTitle>
          <StepList>
            <StepItem>
              <StepNumber>1</StepNumber>
              <span>
                Start Telorax: <InlineCode>telorax serve</InlineCode>
              </span>
            </StepItem>
            <StepItem>
              <StepNumber>2</StepNumber>
              <span>
                Run docs: <InlineCode>cd docs && npm run dev</InlineCode>
              </span>
            </StepItem>
            <StepItem>
              <StepNumber>3</StepNumber>
              <span>Open playground and send your first operation</span>
            </StepItem>
          </StepList>
          <Link to="/playground" style={{ textDecoration: 'none' }}>
            <NavTextLink>
              Open playground
              <ArrowRight size={16} />
            </NavTextLink>
          </Link>
        </Card>

        <Card $padding="24px">
          <SubTitle>Create operation</SubTitle>
          <CodeBlock>{`POST /v1/operations
{
  "type": 1,
  "quantity": 500,
  "target": "@yourchannel",
  "extra": { "message_ids": [42] },
  "country": "IR"
}`}</CodeBlock>
          <MutedText style={{ marginTop: 16 }}>
            Response includes <InlineCode>completed</InlineCode>, <InlineCode>remaining</InlineCode>, and{' '}
            <InlineCode>progress_ratio</InlineCode>.
          </MutedText>
        </Card>
      </TwoColGrid>

      <SectionBlock>
        <SubTitle>{OPERATION_TYPES.length} operation types</SubTitle>
        <GridResponsive>
          {OPERATION_TYPES.map((item) => (
            <TypeLinkCard key={item.code} to="/types">
              <TypeRow>
                <TypeDot $color={item.color} />
                <TypeCode>{item.code}</TypeCode>
                <TypeLabel>{item.label}</TypeLabel>
              </TypeRow>
            </TypeLinkCard>
          ))}
        </GridResponsive>
      </SectionBlock>

      <SectionBlock>
        <SubTitle>{ENDPOINTS.length} endpoints</SubTitle>
        <EndpointList>
          {ENDPOINTS.map((item) => (
            <EndpointLinkCard key={item.id} to="/playground">
              <div>
                <EndpointPath>
                  {item.method} {item.path}
                </EndpointPath>
                <EndpointTitle>{item.title}</EndpointTitle>
              </div>
              <ArrowRight size={16} color="#8b9bb4" />
            </EndpointLinkCard>
          ))}
        </EndpointList>
      </SectionBlock>
    </PageWrap>
  )
}
