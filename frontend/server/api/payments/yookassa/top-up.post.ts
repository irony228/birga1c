export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const config = useRuntimeConfig()
  const accessToken = getCookie(event, 'access_token')

  if (!accessToken) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { detail: 'Нужно войти в аккаунт' }
    })
  }

  return await $fetch(`${config.public.apiBase}/payments/yookassa/top-up`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`
    },
    body
  })
})
