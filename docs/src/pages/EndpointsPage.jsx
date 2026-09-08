import styled from 'styled-components'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ENDPOINTS, HTTP_STATUS_CODES } from '../data/apiReference'
import {
  Badge,
  Card,
  CodeBlock,
  MethodBadgeView,
  MutedText,
  NavTextLink,
  PageWrap,
  SectionHeading,
  Stack,
  SubTitle,
  UpperLabel,
  FieldCard,
  FieldName,
  FieldType,
  TwoColGrid,
} from '../components/ui'

const EndpointCard = styled(Card)`
  padding: 28px;
`

const EndpointHeader = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`

const EndpointPath = styled.code`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 17px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.accentGlow};
`

const EndpointTitle = styled.h2`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: ${({ theme }) => theme.colors.white};
`

const EndpointDesc = styled.p`
  margin: 0;
  max-width: 52rem;
  font-size: 15px;
  line-height: 1.65;
  color: ${({ theme }) => theme.colors.muted};
`

const Block = styled.div`
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
`

const StatusRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
`

function statusTone(code) {
  if (code >= 500) return 'danger'
  if (code >= 400) return 'warning'
  if (code >= 200 && code < 300) return 'success'
  return 'neutral'
}

export function EndpointsPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Reference"
        title="API endpoints"
        description="All routes are prefixed with /v1 and accept or return application/json. Click through to the playground to send live requests."
      />

      <Stack $gap="28px">
        {ENDPOINTS.map((endpoint) => (
          <EndpointCard key={endpoint.id}>
            <EndpointHeader>
              <MethodBadgeView method={endpoint.method} />
              <EndpointPath>{endpoint.path}</EndpointPath>
            </EndpointHeader>
            <EndpointTitle>{endpoint.title}</EndpointTitle>
            <EndpointDesc>{endpoint.description}</EndpointDesc>

            {endpoint.statusCodes?.length ? (
              <Block>
                <UpperLabel>Status codes</UpperLabel>
                <StatusRow>
                  {endpoint.statusCodes.map((code) => {
                    const meta = HTTP_STATUS_CODES.find((item) => item.code === code)
                    return (
                      <Badge key={code} $tone={statusTone(code)}>
                        {code} {meta ? meta.label : ''}
                      </Badge>
                    )
                  })}
                </StatusRow>
              </Block>
            ) : null}

            {endpoint.queryParams?.length ? (
              <Block>
                <UpperLabel>Query parameters</UpperLabel>
                <Stack $gap="8px">
                  {endpoint.queryParams.map((param) => (
                    <FieldCard key={param.name}>
                      <FieldName>{param.name}</FieldName>
                      <FieldType>{param.type}</FieldType>
                      {param.default ? (
                        <FieldType> · default: {param.default}</FieldType>
                      ) : null}
                      <MutedText style={{ marginTop: 4 }}>{param.description}</MutedText>
                    </FieldCard>
                  ))}
                </Stack>
              </Block>
            ) : null}

            {(endpoint.bodyExample || endpoint.responseExample) && (
              <TwoColGrid style={{ marginTop: 24 }}>
                {endpoint.bodyExample ? (
                  <Block style={{ marginTop: 0, paddingTop: 0, borderTop: 'none' }}>
                    <UpperLabel>Request body</UpperLabel>
                    <CodeBlock>{JSON.stringify(endpoint.bodyExample, null, 2)}</CodeBlock>
                  </Block>
                ) : null}
                {endpoint.responseExample ? (
                  <Block style={{ marginTop: 0, paddingTop: 0, borderTop: 'none' }}>
                    <UpperLabel>Response example</UpperLabel>
                    <CodeBlock>{JSON.stringify(endpoint.responseExample, null, 2)}</CodeBlock>
                  </Block>
                ) : null}
              </TwoColGrid>
            )}

            <Link to="/playground" style={{ textDecoration: 'none' }}>
              <NavTextLink>
                Try in playground
                <ArrowRight size={16} />
              </NavTextLink>
            </Link>
          </EndpointCard>
        ))}
      </Stack>
    </PageWrap>
  )
}
