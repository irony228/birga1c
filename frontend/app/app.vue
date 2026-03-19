<script setup>
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'en'
  }
})

const title = 'Биржа заказов 1с'
const description = 'Специализированная площадка для заказчиков и программистов 1С. Система позволяет быстро найти исполнителя на доработки, консультации или внедрение конфигураций «1С:Предприятие».'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
})
</script>

<template>
  <UApp>
    <UHeader>
      <template #left>
        <NuxtLink to="/">
          <AppLogo class="w-auto h-6 shrink-0" />
        </NuxtLink>
      </template>

      <template #right>
        <UColorModeButton />
        <!--TODO сделать проверку на текущего пользователя-->
        <!--что-то типа div v-if="currentUser"-->
        <!--UDropdownMenu с профиль мои-заказы выйти-->
        <!--div v-else-->
        <UButton
          label="Вход"
          color="neutral"
          variant="ghost"
          class="font-bold rounded-full cursor-pointer"
          icon="i-lucide-arrow-right"
          to="login"
        />
      </template>
    </UHeader>

    <UMain>
      <NuxtPage />
    </UMain>

    <USeparator icon="file-icons:1c" />

    <UFooter>
      <template #left>
        <p class="text-sm text-muted">
          Created by <ULink to="https://github.com/babuwka0" target="_blank">Babuwka0</ULink> <ULink to="https://github.com/Tregyn-codein" target="_blank">Tregyn</ULink> <ULink to="https://github.com/irony228" target="_blank">Irony</ULink> • © {{ new Date().getFullYear() }}
        </p>
      </template>

      <template #right>
        <UButton
          to="https://github.com/irony228/birga1c"
          target="_blank"
          icon="i-simple-icons-github"
          aria-label="GitHub"
          color="neutral"
          variant="ghost"
        />
      </template>
    </UFooter>
  </UApp>
</template>
