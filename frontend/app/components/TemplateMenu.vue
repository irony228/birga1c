<template>
  <div class="flex items-center gap-2">
    <UButton
      to="/login"
      variant="ghost"
      color="neutral"
      icon="i-lucide-log-in"
      aria-label="Вход"
    >
      Вход
    </UButton>

    <UButton
      to="/register"
      variant="ghost"
      color="neutral"
      icon="i-lucide-user-plus"
      aria-label="Регистрация"
    >
      Регистрация
    </UButton>
  </div>
</template>
