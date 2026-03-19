<template>
  <div class="max-w-lg mx-auto">
    <UPageHero
      title="Профиль"
      description="Вы вошли."
    />

    <UCard class="mt-6 w-full">
      <div class="p-4 sm:p-6 space-y-3">
        <div class="text-sm text-muted">
          Состояние авторизации: <span class="text-green-600 font-medium">залогинен</span>
        </div>
        <div class="text-sm text-muted">
          Токен хранится в cookie: <span class="text-muted-foreground font-medium">access_token</span>
        </div>
        <div class="text-sm text-muted">
          Debug роль из JWT:
          <span class="font-medium text-primary">{{ debugRole }}</span>
        </div>
        <div class="pt-2">
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-log-out"
            @click="logout"
          >
            Выйти
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const accessToken = useCookie('access_token')
const debugRole = computed(() => extractRoleFromToken(accessToken.value))

function decodeJwtPayload(token) {
  if (!token || typeof token !== 'string') return null

  const parts = token.split('.')
  if (parts.length < 2) return null

  try {
    const payloadPart = parts[1]
    const normalized = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = atob(padded)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

function extractRoleFromToken(token) {
  const payload = decodeJwtPayload(token)
  if (!payload || typeof payload !== 'object') return 'не определена'

  return payload.role || payload.user_role || payload.userRole || 'не определена'
}

async function logout() {
  accessToken.value = null
  await navigateTo('/')
}
</script>
