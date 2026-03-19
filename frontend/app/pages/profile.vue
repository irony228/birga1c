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
const accessToken = useCookie('access_token')

async function logout() {
  accessToken.value = null
  await navigateTo('/')
}
</script>
