export const HTTP_STATUS_CODES = [
  { code: 200, label: 'OK', description: 'Request succeeded.' },
  { code: 201, label: 'Created', description: 'Operation queued successfully.' },
  { code: 404, label: 'Not Found', description: 'Operation ID does not exist.' },
  { code: 422, label: 'Unprocessable', description: 'Validation failed — check type, extra, or quantity.' },
  { code: 500, label: 'Server Error', description: 'Unexpected failure — check Telorax logs.' },
]

export const OPERATION_RESPONSE_FIELDS = [
  { name: 'id', type: 'integer', description: 'Unique operation identifier.' },
  { name: 'type', type: 'string', description: 'OperationType name, e.g. VIEW.' },
  { name: 'quantity', type: 'integer', description: 'Total units requested.' },
  { name: 'completed', type: 'integer', description: 'Units fulfilled so far.' },
  { name: 'remaining', type: 'integer', description: 'Units still pending.' },
  { name: 'state', type: 'string', description: 'Lifecycle state — QUEUED, RUNNING, COMPLETED, …' },
  { name: 'progress_ratio', type: 'float', description: 'completed / quantity (0.0 – 1.0).' },
  { name: 'target', type: 'string', description: 'Channel, group, or bot reference.' },
]

export const OPERATION_SUMMARY_EXAMPLE = {
  id: 42,
  type: 'VIEW',
  quantity: 500,
  completed: 120,
  remaining: 380,
  state: 'RUNNING',
  progress_ratio: 0.24,
  target: '@yourchannel',
}

export const HEALTH_RESPONSE = { status: 'ok' }

export const STATUS_RESPONSE = {
  version: '0.1.13',
  status: 'healthy',
  components: [
    { name: 'config', status: 'ok', detail: '/etc/telorax/.env' },
    { name: 'database', status: 'ok', detail: null },
    { name: 'redis', status: 'ok', detail: null },
    { name: 'api', status: 'ok', detail: '127.0.0.1:2082' },
  ],
}

export const OPERATION_TYPES = [
  {
    code: 1,
    name: 'VIEW',
    label: 'View',
    description: 'Increment view count on channel posts or stories.',
    color: '#2aabee',
    extraFields: [
      { name: 'message_ids', type: 'int[]', description: 'Specific message IDs to view.' },
      { name: 'story_ids', type: 'int[]', description: 'Story IDs when targeting stories.' },
      { name: 'members_only', type: 'boolean', description: 'Restrict to members-only content.' },
    ],
    extraExample: { message_ids: [42] },
  },
  {
    code: 2,
    name: 'SUBSCRIBE',
    label: 'Subscribe',
    description: 'Join a channel or group with optional auto-unsubscribe.',
    color: '#3dd68c',
    extraFields: [
      { name: 'auto_unsubscribe_days', type: 'integer', description: 'Leave after N days.', example: 30 },
      { name: 'read_history_on_join', type: 'boolean', description: 'Mark history read on join.' },
      { name: 'search_query', type: 'string', description: 'Discovery search term before join.' },
    ],
    extraExample: { auto_unsubscribe_days: 30 },
  },
  {
    code: 3,
    name: 'POLL_VOTE',
    label: 'Poll vote',
    description: 'Vote on a poll attached to a message.',
    color: '#a78bfa',
    extraFields: [
      { name: 'option', type: 'integer', required: true, description: 'Zero-based poll option index.' },
    ],
    extraExample: { option: 0 },
  },
  {
    code: 4,
    name: 'REACTION',
    label: 'Reaction',
    description: 'React to messages or stories with an emoji.',
    color: '#f5a524',
    extraFields: [
      { name: 'message_ids', type: 'int[]', description: 'Messages to react to.' },
      { name: 'story_ids', type: 'int[]', description: 'Stories to react to.' },
      { name: 'emoji', type: 'string', description: 'Reaction emoji.', example: '👍' },
      { name: 'preflight_view', type: 'boolean', description: 'View message before reacting.' },
    ],
    extraExample: { message_ids: [42], emoji: '👍' },
  },
  {
    code: 5,
    name: 'SPONSORED',
    label: 'Sponsored',
    description: 'Handle sponsored message interactions.',
    color: '#f76565',
    extraFields: [
      { name: 'click_probability', type: 'float', description: 'Probability of clicking the ad.' },
      { name: 'skip_usernames', type: 'string[]', description: 'Usernames to skip.' },
      { name: 'report_spam', type: 'boolean', description: 'Report as spam instead of engaging.' },
    ],
    extraExample: { click_probability: 0.2 },
  },
  {
    code: 6,
    name: 'SEARCH_VIEW',
    label: 'Search view',
    description: 'Open content discovered via global search.',
    color: '#38bdf8',
    extraFields: [
      { name: 'search_query', type: 'string', description: 'Query used to find the target.' },
      { name: 'message_ids', type: 'int[]', description: 'Messages to open from search results.' },
    ],
    extraExample: { search_query: 'crypto news' },
  },
  {
    code: 7,
    name: 'BUTTON_CLICK',
    label: 'Button click',
    description: 'Click inline keyboard buttons on a message.',
    color: '#fb923c',
    extraFields: [
      { name: 'message_ids', type: 'int[]', description: 'Messages containing buttons.' },
      { name: 'button_index', type: 'integer', description: 'Button index to click.', example: 0 },
    ],
    extraExample: { message_ids: [42], button_index: 0 },
  },
  {
    code: 8,
    name: 'BOT_START',
    label: 'Bot start',
    description: 'Send /start to a bot with an optional deep-link payload.',
    color: '#34d399',
    extraFields: [{ name: 'payload', type: 'string', description: 'Deep-link start parameter.' }],
    extraExample: { payload: 'ref_campaign' },
  },
]

export const OPERATION_STATES = [
  { code: 1, name: 'DRAFT', description: 'Created but not yet queued.' },
  { code: 2, name: 'QUEUED', description: 'Waiting for worker pickup.' },
  { code: 3, name: 'RUNNING', description: 'Actively being fulfilled.' },
  { code: 4, name: 'PAUSED', description: 'Temporarily halted.' },
  { code: 5, name: 'COMPLETED', description: 'All units completed successfully.' },
  { code: 6, name: 'FAILED', description: 'Stopped due to errors.' },
  { code: 7, name: 'CANCELLED', description: 'Cancelled before completion.' },
]

export const ACCOUNT_SUMMARY_EXAMPLE = {
  id: 7,
  msisdn: 989121234567,
  state: 'ACTIVE',
  country_iso: 'IR',
  reliability_score: 100,
  is_operational: true,
}

export const ACCOUNT_DETAIL_EXAMPLE = {
  ...ACCOUNT_SUMMARY_EXAMPLE,
  telegram_user_id: 123456789,
  telegram_username: 'demo_user',
  display_name: 'Demo User',
  is_rate_limited: false,
  rate_limited_until: null,
  restricted_until: null,
  last_online_at: null,
  two_factor_confirmed_at: null,
  foreign_sessions_revoked_at: null,
  last_engaged_at: null,
  account_ttl_configured: false,
  proxy_label: null,
  notes: null,
  provisioned_at: '2026-03-08T12:00:00Z',
  created_at: '2026-03-08T12:00:00Z',
  updated_at: '2026-03-08T12:00:00Z',
}

export const ACCOUNT_STATS_EXAMPLE = {
  total: 120,
  operational: 95,
  by_state: {
    ACTIVE: 95,
    RATE_LIMITED: 10,
    STANDBY: 8,
    DEACTIVATED: 7,
  },
}

export const ACCOUNT_STATES = [
  { code: 0, name: 'DEACTIVATED', description: 'Removed from the operational pool.' },
  { code: 1, name: 'ACTIVE', description: 'Ready for worker dispatch.' },
  { code: 2, name: 'RATE_LIMITED', description: 'Temporarily throttled by Telegram.' },
  { code: 3, name: 'STANDBY', description: 'Healthy but held back from dispatch.' },
  { code: 4, name: 'DUPLICATE', description: 'Session key conflict detected.' },
  { code: 5, name: 'RESTRICTED', description: 'Account restricted by Telegram.' },
  { code: 6, name: 'SESSION_EXPIRED', description: 'Session is no longer valid.' },
  { code: 10, name: 'PROVISIONING', description: 'Import or onboarding in progress.' },
]

export const ENDPOINTS = [
  {
    id: 'health',
    method: 'GET',
    path: '/v1/health',
    title: 'Health check',
    description: 'Lightweight liveness probe. Returns immediately — safe for load balancers and uptime monitors.',
    responseExample: HEALTH_RESPONSE,
    statusCodes: [200],
  },
  {
    id: 'status',
    method: 'GET',
    path: '/v1/status',
    title: 'System status',
    description: 'Full diagnostics report with per-component health (config, database, redis, api).',
    responseExample: STATUS_RESPONSE,
    statusCodes: [200],
  },
  {
    id: 'operations-queued',
    method: 'GET',
    path: '/v1/operations/queued',
    title: 'List queued operations',
    description: 'Returns operations in QUEUED state, newest first. Useful for monitoring backlog.',
    queryParams: [{ name: 'limit', type: 'integer', default: '50', description: 'Max results (1–500).' }],
    responseExample: [OPERATION_SUMMARY_EXAMPLE],
    statusCodes: [200],
  },
  {
    id: 'operations-get',
    method: 'GET',
    path: '/v1/operations/{id}',
    title: 'Get operation',
    description: 'Fetch a single operation by numeric ID. Returns 404 if not found.',
    responseExample: OPERATION_SUMMARY_EXAMPLE,
    statusCodes: [200, 404],
  },
  {
    id: 'operations-create',
    method: 'POST',
    path: '/v1/operations',
    title: 'Create operation',
    description: 'Queue a new batch operation. Validates type-specific extra fields before enqueueing.',
    bodyExample: {
      type: 1,
      quantity: 500,
      target: '@yourchannel',
      extra: { message_ids: [42] },
      country: 'IR',
    },
    responseExample: { ...OPERATION_SUMMARY_EXAMPLE, completed: 0, remaining: 500, state: 'QUEUED', progress_ratio: 0 },
    statusCodes: [201, 422],
  },
  {
    id: 'accounts-list',
    method: 'GET',
    path: '/v1/accounts',
    title: 'List accounts',
    description: 'Browse the account pool with pagination and optional filters. Requires HTTP Basic auth.',
    queryParams: [
      { name: 'limit', type: 'integer', default: '50', description: 'Max results (1–500).' },
      { name: 'offset', type: 'integer', default: '0', description: 'Pagination offset.' },
      { name: 'state', type: 'string', description: 'Filter by AccountState name, e.g. ACTIVE.' },
      { name: 'country', type: 'string', description: 'Filter by ISO country code.' },
    ],
    responseExample: {
      items: [ACCOUNT_SUMMARY_EXAMPLE],
      total: 1,
      limit: 50,
      offset: 0,
    },
    statusCodes: [200, 401],
  },
  {
    id: 'accounts-stats',
    method: 'GET',
    path: '/v1/accounts/stats',
    title: 'Account pool stats',
    description: 'Aggregate counts by state for monitoring pool health.',
    responseExample: ACCOUNT_STATS_EXAMPLE,
    statusCodes: [200, 401],
  },
  {
    id: 'accounts-get',
    method: 'GET',
    path: '/v1/accounts/{id}',
    title: 'Get account',
    description: 'Detailed account view without exposing the encrypted session payload.',
    responseExample: ACCOUNT_DETAIL_EXAMPLE,
    statusCodes: [200, 401, 404],
  },
  {
    id: 'accounts-update',
    method: 'PATCH',
    path: '/v1/accounts/{id}',
    title: 'Update account',
    description: 'Adjust operational metadata such as state, notes, proxy label, or reliability score.',
    bodyExample: {
      state: 'STANDBY',
      notes: 'Cooling down after rate limit',
      reliability_score: 80,
    },
    responseExample: { ...ACCOUNT_DETAIL_EXAMPLE, state: 'STANDBY', notes: 'Cooling down after rate limit', reliability_score: 80 },
    statusCodes: [200, 401, 404, 422],
  },
  {
    id: 'accounts-deactivate',
    method: 'POST',
    path: '/v1/accounts/{id}/deactivate',
    title: 'Deactivate account',
    description: 'Move an account out of the operational pool without deleting history.',
    responseExample: { ...ACCOUNT_DETAIL_EXAMPLE, state: 'DEACTIVATED', is_operational: false },
    statusCodes: [200, 401, 404],
  },
  {
    id: 'accounts-import',
    method: 'POST',
    path: '/v1/accounts/import',
    title: 'Import session',
    description: 'Upload a Telethon or Pyrogram .session file. Optionally renew via QR login like the legacy Matrix importer.',
    bodyExample: {
      file: '(multipart .session file)',
      password: 'optional-2fa-password',
      renew: true,
      ignore_2fa: false,
      ignore_revoke: false,
    },
    responseExample: {
      created: true,
      account: ACCOUNT_DETAIL_EXAMPLE,
    },
    statusCodes: [201, 401, 422],
  },
]

export function getOperationType(code) {
  return OPERATION_TYPES.find((item) => item.code === code)
}
