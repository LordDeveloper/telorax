import styled from 'styled-components'
import { OPERATION_STATES, OPERATION_TYPES } from '../data/apiReference'
import {
  Badge,
  Card,
  CodeBlock,
  FieldCard,
  FieldName,
  FieldType,
  GridResponsive,
  MutedText,
  PageWrap,
  SectionBlock,
  SectionDivider,
  SectionHeading,
  Stack,
  UpperLabel,
} from '../components/ui'

const TypeCard = styled(Card)`
  overflow: hidden;
`

const TypeHeader = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  padding: 22px 26px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  background: linear-gradient(180deg, ${({ theme }) => theme.colors.surfaceOverlay}, transparent);
`

const TypeCodeBadge = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.radii.md};
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  font-weight: 700;
  background: ${({ $bg }) => $bg};
  color: ${({ $color }) => $color};
`

const TypeTitleRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`

const TypeTitle = styled.h2`
  margin: 0;
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: ${({ theme }) => theme.colors.white};
`

const TypeBody = styled.div`
  display: grid;
  gap: 24px;
  padding: 24px;

  @media (min-width: ${({ theme }) => theme.breakpoints.lg}) {
    grid-template-columns: 1fr 1fr;
  }
`

const StateCard = styled(Card)`
  padding: 16px;
`

const StateRow = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`

const StateCode = styled.span`
  font-family: ${({ theme }) => theme.fonts.mono};
  font-size: 14px;
  color: ${({ theme }) => theme.colors.accentGlow};
`

const StateName = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.white};
`

const TypesStack = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`

const StatesSection = styled(SectionBlock)`
  margin-top: 56px;
`

export function TypesPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Reference"
        title="Operation types"
        description="OperationType is an IntEnum. Pass the numeric code as type in API requests. Each type accepts a typed extra object."
      />

      <TypesStack>
        {OPERATION_TYPES.map((item) => (
          <TypeCard key={item.code}>
            <TypeHeader>
              <TypeCodeBadge $bg={`${item.color}22`} $color={item.color}>
                {item.code}
              </TypeCodeBadge>
              <div>
                <TypeTitleRow>
                  <TypeTitle>{item.label}</TypeTitle>
                  <Badge $tone="neutral">{item.name}</Badge>
                </TypeTitleRow>
                <MutedText style={{ marginTop: 4 }}>{item.description}</MutedText>
              </div>
            </TypeHeader>

            <TypeBody>
              <div>
                <UpperLabel>extra fields</UpperLabel>
                {item.extraFields.length === 0 ? (
                  <MutedText>No extra fields required.</MutedText>
                ) : (
                  <Stack $gap="12px">
                    {item.extraFields.map((field) => (
                      <FieldCard key={field.name}>
                        <div>
                          <FieldName>{field.name}</FieldName>
                          <FieldType>{field.type}</FieldType>
                          {field.required ? <Badge $tone="danger">required</Badge> : null}
                        </div>
                        <MutedText style={{ marginTop: 4 }}>{field.description}</MutedText>
                      </FieldCard>
                    ))}
                  </Stack>
                )}
              </div>
              <div>
                <UpperLabel>Example request</UpperLabel>
                <CodeBlock>
                  {JSON.stringify(
                    {
                      type: item.code,
                      quantity: 100,
                      target: '@yourchannel',
                      extra: item.extraExample,
                    },
                    null,
                    2,
                  )}
                </CodeBlock>
              </div>
            </TypeBody>
          </TypeCard>
        ))}
      </TypesStack>

      <StatesSection>
        <SectionDivider />
        <SectionHeading
          eyebrow="Lifecycle"
          title="Operation states"
          description="State is returned as an uppercase string in operation summaries. Workers transition operations through these values."
        />
        <GridResponsive>
          {OPERATION_STATES.map((state) => (
            <StateCard key={state.code}>
              <StateRow>
                <StateCode>{state.code}</StateCode>
                <StateName>{state.name}</StateName>
              </StateRow>
              <MutedText style={{ marginTop: 8 }}>{state.description}</MutedText>
            </StateCard>
          ))}
        </GridResponsive>
      </StatesSection>
    </PageWrap>
  )
}
