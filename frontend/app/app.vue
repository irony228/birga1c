<script setup>
import { computed } from 'vue'

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
  ogDescription: description
})

const accessToken = useCookie('access_token')
const isAuthenticated = computed(() => {
  const token = accessToken.value
  return typeof token === 'string' && token.trim() !== '' && token !== 'null'
})

const menuItems = [
  {
    label: 'Профиль',
    icon: 'i-lucide-user',
    to: '/profile'
  },
  {
    label: 'Выйти',
    icon: 'i-lucide-log-out',
    onSelect: onLogout
  }
]

async function onLogout() {
  accessToken.value = undefined
  await navigateTo('/')
}
</script>

<template>
  <UApp>
    <UHeader>
      <template #left>
        <div class="flex items-center gap-2">
          <NuxtLink to="/">
            <AppLogo class="w-auto h-6 shrink-0" />
          </NuxtLink>
          <UButton
            v-if="isAuthenticated"
            to="/dashboard"
            color="neutral"
            variant="ghost"
            icon="i-lucide-list"
            class="font-bold rounded-full cursor-pointer"
          >
            Лента заказов
          </UButton>
        </div>
      </template>

      <template #right>
        <UColorModeButton />
        <!-- TODO сделать проверку на текущего пользователя -->
        <!-- что-то типа div v-if="currentUser" -->
        <!-- UDropdownMenu с профиль мои-заказы выйти -->
        <!-- div v-else -->

        <UButton
          v-if="!isAuthenticated"
          label="Вход"
          color="neutral"
          variant="ghost"
          class="font-bold rounded-full cursor-pointer"
          icon="i-lucide-arrow-right"
          to="/login"
        />

        <UDropdownMenu
          v-if="isAuthenticated"
          :items="menuItems"
          :content="{
            align: 'end',
            side: 'bottom'
          }"
        >
          <UButton
            variant="ghost"
            color="neutral"
            icon="i-lucide-user"
            aria-label="Меню пользователя"
            class="font-bold cursor-pointer"
            trailing-icon="i-lucide-chevron-down"
          >
            Профиль
          </UButton>
        </UDropdownMenu>
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
