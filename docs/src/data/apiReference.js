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

export const ENDPOINTS = [
  {
    id: 'health',
    method: 'GET',
    path: '/v1/health',
    title: 'Health check',
    description: 'Lightweight liveness probe returning {"status": "ok"}.',
  },
  {
    id: 'status',
    method: 'GET',
    path: '/v1/status',
    title: 'System status',
    description: 'Detailed health report with component breakdown.',
  },
  {
    id: 'operations-queued',
    method: 'GET',
    path: '/v1/operations/queued',
    title: 'List queued operations',
    description: 'Returns operations in QUEUED state, newest first.',
    queryParams: [{ name: 'limit', type: 'integer', default: '50', description: 'Max results (1–500).' }],
  },
  {
    id: 'operations-get',
    method: 'GET',
    path: '/v1/operations/{id}',
    title: 'Get operation',
    description: 'Fetch a single operation by ID.',
  },
  {
    id: 'operations-create',
    method: 'POST',
    path: '/v1/operations',
    title: 'Create operation',
    description: 'Queue a new batch operation against a Telegram target.',
    bodyExample: {
      type: 1,
      quantity: 500,
      target: '@yourchannel',
      extra: { message_ids: [42] },
      country: 'IR',
    },
  },
]

export function getOperationType(code) {
  return OPERATION_TYPES.find((item) => item.code === code)
}
