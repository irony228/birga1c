<template>
  <div class="flex items-center gap-2">
    <UButton
      v-if="!isAuthenticated"
      to="/login"
      variant="ghost"
      color="neutral"
      icon="i-lucide-log-in"
      aria-label="Вход"
    >
      Вход
    </UButton>

    <UButton
      v-if="!isAuthenticated"
      to="/register"
      variant="ghost"
      color="neutral"
      icon="i-lucide-user-plus"
      aria-label="Регистрация"
    >
      Регистрация
    </UButton>

    <UButton
      v-else
      to="/profile"
      variant="ghost"
      color="neutral"
      icon="i-lucide-user"
      aria-label="Профиль"
    >
      Профиль
    </UButton>

    <UButton
      v-if="isAuthenticated"
      variant="ghost"
      color="neutral"
      icon="i-lucide-log-out"
      aria-label="Выйти"
      @click="onLogout"
    >
      Выйти
    </UButton>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const accessToken = useCookie('access_token')
const isAuthenticated = computed(() => !!accessToken.value)

function onLogout() {
  accessToken.value = null
  navigateTo('/')
}
</script>
