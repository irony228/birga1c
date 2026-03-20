export default defineEventHandler(async (event) => {
  const bidId = getRouterParam(event, 'bidId')
  if (!bidId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { detail: 'Не указан отклик' }
    })
  }

  const config = useRuntimeConfig()
  const accessToken = getCookie(event, 'access_token')

  if (!accessToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { detail: 'Нужно войти в аккаунт' }
    })
  }

  return await $fetch(`${config.public.apiBase}/bids/${bidId}/reject`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  })
})
