export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const config = useRuntimeConfig()
  const accessToken = getCookie(event, 'access_token')

  if (!accessToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { detail: 'Нужно авторизоваться, чтобы создать заказ' }
    })
  }

  return await $fetch(`${config.public.apiBase}/orders`, {
    method: 'POST',
    body,
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  })
})
