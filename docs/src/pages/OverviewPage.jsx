import styled from 'styled-components'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Boxes,
  Gauge,
  Globe,
  ListOrdered,
  Server,
  Target,
  Workflow,
} from 'lucide-react'
import {
  ENDPOINTS,
  HTTP_STATUS_CODES,
  OPERATION_RESPONSE_FIELDS,
  OPERATION_TYPES,
} from '../data/apiReference'
import {
  Callout,
  CalloutTitle,
  Card,
  CodeBlock,
  DataTable,
  GridResponsive,
  HighlightTitle,
  IconBox,
  InlineCode,
  MutedText,
  NavTextLink,
  PageWrap,
  SectionBlock,
  SectionHeading,
  StatCell,
  StatGrid,
  StatLabel,
  StatValue,
  StepItem,
  StepList,
  StepNumber,
  SubTitle,
  TableWrap,
  TwoColGrid,
} from '../components/ui'

const highlights = [
  {
    icon: Target,
    title: 'Batch operations',
    text: 'Queue hundreds of Telegram actions — views, joins, reactions, poll votes — with a single API call.',
  },
  {
    icon: ListOrdered,
    title: 'Typed payloads',
    text: 'Each OperationType has a validated extra schema. Invalid fields return HTTP 422 with a clear message.',
  },
  {
    icon: Gauge,
    title: 'Live playground',
    text: 'Send real requests, inspect JSON responses, measure latency, and copy cURL in one click.',
  },
  {
    icon: Boxes,
    title: 'Progress tracking',
    text: 'Poll operation status to monitor completed, remaining, state, and progress_ratio in real time.',
  },
]

const TypeLinkCard = styled(Link)`
  display: block;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.surfaceRaised};
  padding: 12px 16px;
  text-decoration: none;
  transition: all 0.18s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.borderGlow};
    background: ${({ theme }) => theme.colors.surfaceOverlay};
    transform: translateY(-1px);
  }
`

const TypeRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`

const TypeDot = styled.span`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${({ $color }) => $color};
  box-shadow: 0 0 8px ${({ $color }) => $color}88;
`

const TypeCode = styled.span`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 12px;
  color: ${({ theme }) => theme.colors.mutedDim};
`

const TypeLabel = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

const EndpointLinkCard = styled(Link)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.surfaceRaised};
  padding: 14px 18px;
  text-decoration: none;
  transition: all 0.18s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.borderGlow};
  }
`

const EndpointPath = styled.p`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 13px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

const EndpointTitle = styled.p`
  margin: 4px 0 0;
  font-size: 13px;
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

const FlowSteps = styled.div`
  display: grid;
  gap: 12px;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    grid-template-columns: repeat(3, 1fr);
  }
`

const FlowStep = styled.div`
  padding: 16px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  background: ${({ theme }) => theme.colors.surfaceRaised};

  &::before {
    content: '${({ $n }) => $n}';
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    margin-bottom: 10px;
    border-radius: 6px;
    border: 1px solid rgba(42, 171, 238, 0.25);
    font-family: ${({ theme }) => theme.fonts.mono};
    font-size: 11px;
    font-weight: 600;
    color: ${({ theme }) => theme.colors.accentGlow};
  }
`

const FlowTitle = styled.p`
  margin: 0 0 6px;
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

export function OverviewPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Telorax API v1"
        title="Control plane for Telegram account operations"
        description="REST API for queuing, tracking, and scaling Telegram automation workloads. All routes are JSON over HTTP — explore endpoints, learn OperationType codes, and test live from the playground."
      />

      <StatGrid style={{ marginBottom: 32 }}>
        <StatCell>
          <StatLabel>Base path</StatLabel>
          <StatValue>/v1</StatValue>
        </StatCell>
        <StatCell>
          <StatLabel>Format</StatLabel>
          <StatValue>JSON</StatValue>
        </StatCell>
        <StatCell>
          <StatLabel>Operation types</StatLabel>
          <StatValue>{OPERATION_TYPES.length}</StatValue>
        </StatCell>
        <StatCell>
          <StatLabel>Endpoints</StatLabel>
          <StatValue>{ENDPOINTS.length}</StatValue>
        </StatCell>
      </StatGrid>

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
                Install & start: <InlineCode>telorax serve</InlineCode> or enable the systemd unit
              </span>
            </StepItem>
            <StepItem>
              <StepNumber>2</StepNumber>
              <span>
                Open docs at <InlineCode>/docs</InlineCode> on your API host (e.g. port 2082)
              </span>
            </StepItem>
            <StepItem>
              <StepNumber>3</StepNumber>
              <span>Set Base URL in the playground and queue your first operation</span>
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
Content-Type: application/json

{
  "type": 1,
  "quantity": 500,
  "target": "@yourchannel",
  "extra": { "message_ids": [42] },
  "country": "IR"
}`}</CodeBlock>
          <MutedText style={{ marginTop: 16 }}>
            Returns <InlineCode>201 Created</InlineCode> with operation summary including{' '}
            <InlineCode>state: "QUEUED"</InlineCode>.
          </MutedText>
        </Card>
      </TwoColGrid>

      <SectionBlock>
        <SubTitle>
          <Workflow size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
          Request lifecycle
        </SubTitle>
        <FlowSteps>
          <FlowStep $n="01">
            <FlowTitle>Queue</FlowTitle>
            <MutedText>POST creates an operation in QUEUED state with the requested quantity.</MutedText>
          </FlowStep>
          <FlowStep $n="02">
            <FlowTitle>Execute</FlowTitle>
            <MutedText>Workers pick up jobs and transition to RUNNING while fulfilling units.</MutedText>
          </FlowStep>
          <FlowStep $n="03">
            <FlowTitle>Track</FlowTitle>
            <MutedText>GET by ID returns completed, remaining, and progress_ratio until COMPLETED.</MutedText>
          </FlowStep>
        </FlowSteps>
      </SectionBlock>

      <SectionBlock>
        <SubTitle>
          <Server size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
          Operation response fields
        </SubTitle>
        <TableWrap>
          <DataTable>
            <thead>
              <tr>
                <th>Field</th>
                <th>Type</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {OPERATION_RESPONSE_FIELDS.map((field) => (
                <tr key={field.name}>
                  <td>
                    <code>{field.name}</code>
                  </td>
                  <td>{field.type}</td>
                  <td style={{ color: '#94a3b8' }}>{field.description}</td>
                </tr>
              ))}
            </tbody>
          </DataTable>
        </TableWrap>
      </SectionBlock>

      <SectionBlock>
        <SubTitle>
          <Globe size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
          HTTP status codes
        </SubTitle>
        <TableWrap>
          <DataTable>
            <thead>
              <tr>
                <th>Code</th>
                <th>Label</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              {HTTP_STATUS_CODES.map((item) => (
                <tr key={item.code}>
                  <td>
                    <code>{item.code}</code>
                  </td>
                  <td>{item.label}</td>
                  <td style={{ color: '#94a3b8' }}>{item.description}</td>
                </tr>
              ))}
            </tbody>
          </DataTable>
        </TableWrap>
      </SectionBlock>

      <SectionBlock>
        <Callout $accent="#6ecfff">
          <div>
            <CalloutTitle>Configuration</CalloutTitle>
            Telorax reads <InlineCode>/etc/telorax/.env</InlineCode>. Set{' '}
            <InlineCode>APP_HOST</InlineCode> and <InlineCode>APP_PORT</InlineCode> to control where the API
            listens. Use <InlineCode>/v1/health</InlineCode> for liveness and{' '}
            <InlineCode>/v1/status</InlineCode> for full diagnostics.
          </div>
        </Callout>
      </SectionBlock>

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
              <ArrowRight size={16} color="#64748b" />
            </EndpointLinkCard>
          ))}
        </EndpointList>
      </SectionBlock>
    </PageWrap>
  )
}
