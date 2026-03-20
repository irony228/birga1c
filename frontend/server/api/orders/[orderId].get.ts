export default defineEventHandler(async (event) => {
  const orderId = getRouterParam(event, 'orderId')
  if (!orderId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { detail: 'Не указан заказ' }
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

  return await $fetch(`${config.public.apiBase}/orders/${orderId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  })
})
