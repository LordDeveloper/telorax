import { ApiPlayground } from '../components/ApiPlayground'
import { PageWrap, SectionHeading } from '../components/ui'

export function PlaygroundPage() {
  return (
    <PageWrap>
      <SectionHeading
        eyebrow="Interactive"
        title="API Playground"
        description="Build and send live requests. Responses show status, timing, and formatted JSON. Base URL is persisted locally."
      />
      <ApiPlayground />
    </PageWrap>
  )
}
