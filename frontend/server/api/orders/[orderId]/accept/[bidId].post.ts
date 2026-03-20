export default defineEventHandler(async (event) => {
  const orderId = getRouterParam(event, 'orderId')
  const bidId = getRouterParam(event, 'bidId')
  if (!orderId || !bidId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { detail: 'Не указан заказ или отклик' }
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

  return await $fetch(`${config.public.apiBase}/orders/${orderId}/accept/${bidId}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  })
})
