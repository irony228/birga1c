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

import { computed } from 'vue'

const accessToken = useCookie('access_token')
const isAuthenticated = computed(() => !!accessToken.value)

function onLogout() {
  accessToken.value = null
  navigateTo('/')
}

const menuItems = [
  [
    {
      label: 'Профиль',
      icon: 'i-lucide-user',
      to: '/profile'
    }
  ],
  [
    {
      label: 'Выйти',
      icon: 'i-lucide-log-out',
      onSelect: () => onLogout()
    }
  ]
]

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
        <UButton
          v-if="!isAuthenticated"
          label="Вход"
          color="neutral"
          variant="ghost"
          class="font-bold rounded-full cursor-pointer"
          icon="i-lucide-arrow-right"
          to="login"
        />
        <UDropdownMenu
          v-else
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
