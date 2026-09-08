const STORAGE_KEY = 'telorax-docs-base-url'

export function getStoredBaseUrl() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem(STORAGE_KEY) ?? window.location.origin
}

export function storeBaseUrl(url) {
  localStorage.setItem(STORAGE_KEY, url.replace(/\/$/, ''))
}

function buildUrl(baseUrl, path, query) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const url = new URL(normalizedPath, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`)
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value) url.searchParams.set(key, value)
    })
  }
  return url.toString()
}

export async function sendRequest(baseUrl, request) {
  const started = performance.now()
  const url = buildUrl(baseUrl, request.path, request.query)
  const headers = { Accept: 'application/json' }
  const init = { method: request.method, headers }

  if (request.body !== undefined && request.method !== 'GET') {
    headers['Content-Type'] = 'application/json'
    init.body = JSON.stringify(request.body)
  }

  const response = await fetch(url, init)
  const durationMs = Math.round(performance.now() - started)
  const responseHeaders = {}
  response.headers.forEach((value, key) => {
    responseHeaders[key] = value
  })

  let data
  const text = await response.text()
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }

  return {
    ok: response.ok,
    status: response.status,
    statusText: response.statusText,
    durationMs,
    data,
    headers: responseHeaders,
  }
}

export function buildCurl(baseUrl, request) {
  const url = buildUrl(baseUrl, request.path, request.query)
  const lines = [`curl -X ${request.method} '${url}'`, "  -H 'Accept: application/json'"]
  if (request.body !== undefined && request.method !== 'GET') {
    lines.push("  -H 'Content-Type: application/json'")
    lines.push(`  -d '${JSON.stringify(request.body)}'`)
  }
  return lines.join(' \\\n')
}
