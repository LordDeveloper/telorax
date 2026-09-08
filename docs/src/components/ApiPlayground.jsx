import { useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, Clock3, Loader2, Send } from 'lucide-react'
import { buildCurl, getStoredBaseUrl, sendRequest, storeBaseUrl } from '../lib/apiClient'
import { ENDPOINTS, getOperationType, OPERATION_TYPES } from '../data/apiReference'
import {
  Badge,
  Card,
  CardHeader,
  CodeBlock,
  CopyButton,
  CurlHeader,
  DurationText,
  EmptyState,
  ErrorBox,
  FadeIn,
  FieldLabel,
  FormGrid,
  Grid2,
  InfoPanel,
  Input,
  MethodBadgeView,
  MutedText,
  PanelLabel,
  PanelValue,
  PrimaryButton,
  ResponseHeader,
  Select,
  SpinIcon,
  SectionDivider,
  Stack,
  SubHeading,
  TextArea,
  Row,
  StatusText,
} from './ui'

export function ApiPlayground({ initialEndpointId = 'operations-create' }) {
  const initialEndpoint = ENDPOINTS.find((item) => item.id === initialEndpointId) ?? ENDPOINTS[0]
  const [baseUrl, setBaseUrl] = useState(getStoredBaseUrl())
  const [endpointId, setEndpointId] = useState(initialEndpoint.id)
  const [operationType, setOperationType] = useState(1)
  const [quantity, setQuantity] = useState(500)
  const [target, setTarget] = useState('@yourchannel')
  const [country, setCountry] = useState('')
  const [extraJson, setExtraJson] = useState(
    JSON.stringify(getOperationType(1)?.extraExample ?? {}, null, 2),
  )
  const [operationId, setOperationId] = useState('1')
  const [limit, setLimit] = useState('50')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  const endpoint = ENDPOINTS.find((item) => item.id === endpointId) ?? ENDPOINTS[0]

  const requestBody = useMemo(() => {
    if (endpoint.id !== 'operations-create') return undefined
    let extra = {}
    try {
      extra = JSON.parse(extraJson)
    } catch {
      extra = {}
    }
    const body = { type: operationType, quantity, target, extra }
    if (country.trim()) body.country = country.trim().toUpperCase()
    return body
  }, [country, endpoint.id, extraJson, operationType, quantity, target])

  const resolvedPath = useMemo(() => {
    if (endpoint.id === 'operations-get') return endpoint.path.replace('{id}', operationId)
    return endpoint.path
  }, [endpoint.id, endpoint.path, operationId])

  const query = useMemo(() => {
    if (endpoint.id === 'operations-queued') return { limit }
    return undefined
  }, [endpoint.id, limit])

  const curl = buildCurl(baseUrl, {
    method: endpoint.method,
    path: resolvedPath,
    body: requestBody,
    query,
  })

  async function handleSend() {
    setLoading(true)
    setError(null)
    storeBaseUrl(baseUrl)
    try {
      if (endpoint.id === 'operations-create') JSON.parse(extraJson)
      const result = await sendRequest(baseUrl, {
        method: endpoint.method,
        path: resolvedPath,
        body: requestBody,
        query,
      })
      setResponse(result)
    } catch (caught) {
      setResponse(null)
      setError(caught instanceof Error ? caught.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  function handleTypeChange(code) {
    setOperationType(code)
    const typeDef = getOperationType(code)
    if (typeDef) setExtraJson(JSON.stringify(typeDef.extraExample, null, 2))
  }

  return (
    <Grid2>
      <Card $padding="24px">
        <CardHeader>
          <div>
            <SubHeading>Request builder</SubHeading>
            <MutedText>Configure and send live API calls.</MutedText>
          </div>
          <MethodBadgeView method={endpoint.method} />
        </CardHeader>

        <Stack $gap="16px">
          <div>
            <FieldLabel
              label="Base URL"
              hint="Saved in your browser. Use empty origin in dev to hit the Vite proxy."
            />
            <Input
              $mono
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              placeholder="http://127.0.0.1:8000"
            />
          </div>

          <div>
            <FieldLabel label="Endpoint" />
            <Select value={endpointId} onChange={(event) => setEndpointId(event.target.value)}>
              {ENDPOINTS.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.method} {item.path} — {item.title}
                </option>
              ))}
            </Select>
          </div>

          {endpoint.id === 'operations-get' ? (
            <div>
              <FieldLabel label="Operation ID" required />
              <Input $mono value={operationId} onChange={(event) => setOperationId(event.target.value)} />
            </div>
          ) : null}

          {endpoint.id === 'operations-queued' ? (
            <div>
              <FieldLabel label="limit" hint="1–500" />
              <Input $mono value={limit} onChange={(event) => setLimit(event.target.value)} />
            </div>
          ) : null}

          {endpoint.id === 'operations-create' ? (
            <>
              <FormGrid>
                <div>
                  <FieldLabel label="type" hint="OperationType IntEnum code" required />
                  <Select
                    value={operationType}
                    onChange={(event) => handleTypeChange(Number(event.target.value))}
                  >
                    {OPERATION_TYPES.map((item) => (
                      <option key={item.code} value={item.code}>
                        {item.code} — {item.name}
                      </option>
                    ))}
                  </Select>
                </div>
                <div>
                  <FieldLabel label="quantity" required />
                  <Input
                    $mono
                    type="number"
                    min={1}
                    value={quantity}
                    onChange={(event) => setQuantity(Number(event.target.value))}
                  />
                </div>
              </FormGrid>

              <div>
                <FieldLabel label="target" hint="Channel, group, or bot reference" required />
                <Input $mono value={target} onChange={(event) => setTarget(event.target.value)} />
              </div>

              <div>
                <FieldLabel label="country" hint="Optional 2-letter ISO code for account filter" />
                <Input
                  $mono
                  $uppercase
                  value={country}
                  onChange={(event) => setCountry(event.target.value)}
                  placeholder="IR"
                  maxLength={2}
                />
              </div>

              <div>
                <FieldLabel label="extra" hint="Type-specific JSON payload" required />
                <TextArea rows={8} value={extraJson} onChange={(event) => setExtraJson(event.target.value)} />
              </div>
            </>
          ) : null}

          <SectionDivider />

          <InfoPanel>
            <PanelLabel>Resolved path</PanelLabel>
            <PanelValue>
              {endpoint.method} {resolvedPath}
              {query?.limit ? `?limit=${query.limit}` : ''}
            </PanelValue>
          </InfoPanel>

          <Row>
            <PrimaryButton type="button" onClick={handleSend} disabled={loading}>
              {loading ? (
                <SpinIcon>
                  <Loader2 size={16} />
                </SpinIcon>
              ) : (
                <Send size={16} />
              )}
              Send request
            </PrimaryButton>
            <CopyButton value={curl} label="Copy cURL" />
          </Row>
        </Stack>
      </Card>

      <Stack $gap="24px">
        <Card $padding="24px">
          <ResponseHeader>
            <SubHeading>Response</SubHeading>
            {response ? (
              <Row $gap="8px">
                <Badge $tone={response.ok ? 'success' : 'danger'}>{response.status}</Badge>
                <DurationText>
                  <Clock3 size={14} />
                  {response.durationMs} ms
                </DurationText>
              </Row>
            ) : null}
          </ResponseHeader>

          {error ? (
            <ErrorBox>
              <AlertCircle size={16} style={{ marginTop: 2, flexShrink: 0 }} />
              {error}
            </ErrorBox>
          ) : null}

          {!response && !error ? (
            <EmptyState>Send a request to see the response here.</EmptyState>
          ) : null}

          {response ? (
            <FadeIn>
              <Stack $gap="16px">
                <Row $gap="8px">
                  {response.ok ? (
                    <CheckCircle2 size={16} color="#3dd68c" />
                  ) : (
                    <AlertCircle size={16} color="#f76565" />
                  )}
                  <StatusText $ok={response.ok}>{response.statusText}</StatusText>
                </Row>
                <CodeBlock>{JSON.stringify(response.data, null, 2)}</CodeBlock>
                {response.data ? (
                  <CopyButton value={JSON.stringify(response.data, null, 2)} label="Copy JSON" />
                ) : null}
              </Stack>
            </FadeIn>
          ) : null}
        </Card>

        <Card $padding="24px">
          <CurlHeader>
            <PanelLabel style={{ margin: 0 }}>cURL preview</PanelLabel>
            <CopyButton value={curl} />
          </CurlHeader>
          <CodeBlock>{curl}</CodeBlock>
        </Card>
      </Stack>
    </Grid2>
  )
}
