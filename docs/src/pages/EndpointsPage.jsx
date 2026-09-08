import styled from 'styled-components'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ENDPOINTS } from '../data/apiReference'
import {
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
} from '../components/ui'

const EndpointCard = styled(Card)`
  padding: 24px;
`

const EndpointHeader = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`

const EndpointPath = styled.code`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 18px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

const EndpointTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

const EndpointDesc = styled.p`
  margin: 8px 0 0;
  max-width: 48rem;
  font-size: 14px;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.muted};
`

const QueryBlock = styled.div`
  margin-top: 20px;
`

export function EndpointsPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Reference"
        title="API endpoints"
        description="All routes are prefixed with /v1. Use the playground to execute any endpoint interactively."
      />

      <Stack $gap="24px">
        {ENDPOINTS.map((endpoint) => (
          <EndpointCard key={endpoint.id}>
            <EndpointHeader>
              <MethodBadgeView method={endpoint.method} />
              <EndpointPath>{endpoint.path}</EndpointPath>
            </EndpointHeader>
            <EndpointTitle>{endpoint.title}</EndpointTitle>
            <EndpointDesc>{endpoint.description}</EndpointDesc>

            {endpoint.queryParams?.length ? (
              <QueryBlock>
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
              </QueryBlock>
            ) : null}

            {endpoint.bodyExample ? (
              <QueryBlock>
                <UpperLabel>Request body</UpperLabel>
                <CodeBlock>{JSON.stringify(endpoint.bodyExample, null, 2)}</CodeBlock>
              </QueryBlock>
            ) : null}

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
