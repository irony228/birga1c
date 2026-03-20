import { computed } from 'vue'

/**
 * Карточка текущего пользователя с балансом (GET /api/users/me).
 * Общий ключ useAsyncData — данные переиспользуются в app.vue и профиле.
 */
export function useCurrentUser() {
  const accessToken = useCookie('access_token')

  const { data: me, refresh, pending, error, clear } = useAsyncData(
    'current-user',
    async () => {
      const t = accessToken.value
      if (!t || typeof t !== 'string' || !t.trim() || t === 'null') {
        return null
      }
      // server: false — только в браузере: cookie access_token уходит к Nitro; иначе на SSR часто 401 и me=null.
      const requestFetch = useRequestFetch()
      return await requestFetch('/api/users/me')
    },
    {
      watch: [accessToken],
      server: false
    }
  )

  const formattedBalance = computed(() => {
    const b = me.value?.balance
    if (b == null || me.value == null) return '—'
    return `${Number(b).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} ₽`
  })

  const formattedFrozen = computed(() => {
    const b = me.value?.frozen_balance
    if (b == null || me.value == null) return '—'
    return `${Number(b).toLocaleString('ru-RU', { maximumFractionDigits: 2 })} ₽`
  })

  return {
    me,
    refresh,
    pending,
    error,
    clear,
    formattedBalance,
    formattedFrozen
  }
}
