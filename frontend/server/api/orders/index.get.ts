const ALLOWED_SCOPES = [
  'customer_open',
  'customer_in_progress',
  'customer_closed',
  'worker_open_available',
  'worker_in_progress',
  'worker_bidded_active'
] as const

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const accessToken = getCookie(event, 'access_token')

  if (!accessToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { detail: 'Нужно авторизоваться, чтобы просматривать заказы' }
    })
  }

  const query = getQuery(event)
  const scope = query.scope

  if (!scope || typeof scope !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { detail: 'Параметр scope обязателен' }
    })
  }

  if (!ALLOWED_SCOPES.includes(scope as (typeof ALLOWED_SCOPES)[number])) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { detail: `Недопустимый scope. Допустимо: ${ALLOWED_SCOPES.join(', ')}` }
    })
  }

  // Trailing slash — без редиректа 307 (иначе часть клиентов теряет Authorization при редиректе)
  return await $fetch(`${config.public.apiBase}/orders/`, {
    method: 'GET',
    query: { scope },
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  })
})
