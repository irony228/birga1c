import { computed } from 'vue'

/**
 * Уведомления текущего пользователя (GET /api/notifications, POST .../read).
 */
export function useNotifications() {
  const accessToken = useCookie('access_token')

  const { data: notifications, refresh, pending, error } = useAsyncData(
    'notifications',
    async () => {
      const t = accessToken.value
      if (!t || typeof t !== 'string' || !t.trim() || t === 'null') {
        return []
      }
      const requestFetch = useRequestFetch()
      return await requestFetch('/api/notifications')
    },
    {
      watch: [accessToken],
      server: false
    }
  )

  const unreadCount = computed(() => {
    const list = notifications.value
    if (!Array.isArray(list)) return 0
    return list.filter(n => !n.is_read).length
  })

  async function markAsRead(id) {
    const requestFetch = useRequestFetch()
    await requestFetch(`/api/notifications/${id}/read`, { method: 'POST' })
    await refresh()
  }

  return {
    notifications,
    refresh,
    pending,
    error,
    unreadCount,
    markAsRead
  }
}
