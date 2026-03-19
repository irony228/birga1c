export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const config = useRuntimeConfig()

  // Proxy to FastAPI to avoid browser CORS issues.
  return await $fetch(`${config.public.apiBase}/users/login`, {
    method: 'POST',
    body
  })
})
