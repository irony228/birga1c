<template>
  <div class="max-w-lg mx-auto">
    <UPageHero
      title="Вход"
      description="Введите email и пароль, чтобы продолжить."
    />

    <UCard class="mt-6 w-full">
      <form class="space-y-4" @submit.prevent="onSubmit">
        <UFormField
          label="Email"
          name="email"
          :error="errors.email || undefined"
          required
          class="w-full"
        >
          <UInput
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="name@example.com"
            required
            class="w-full"
          />
        </UFormField>

        <UFormField
          label="Пароль"
          name="password"
          :error="errors.password || undefined"
          required
          class="w-full"
        >
          <UInput
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
            class="w-full"
          />
        </UFormField>

        <div v-if="submitMessage" :class="submitMessage.type === 'error' ? 'text-sm text-red-500' : 'text-sm text-green-600'">
          {{ submitMessage.text }}
        </div>

        <UButton
          type="submit"
          block
          color="primary"
          :loading="loading"
          :disabled="loading"
        >
          Войти
        </UButton>

        <div class="text-center text-sm text-muted">
          Нет аккаунта?
          <NuxtLink to="/register" class="text-orange-500 hover:text-orange-600">Регистрация</NuxtLink>
        </div>
      </form>
    </UCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const loading = ref(false)

const errors = ref({
  email: '',
  password: ''
})

const submitMessage = ref(null)
// submitMessage: { type: 'error' | 'success', text: string }

function validate() {
  errors.value.email = ''
  errors.value.password = ''

  let ok = true

  if (!email.value.trim()) {
    errors.value.email = 'Введите email'
    ok = false
  } else if (!/^\S+@\S+\.\S+$/.test(email.value)) {
    errors.value.email = 'Неверный формат email'
    ok = false
  }

  if (!password.value) {
    errors.value.password = 'Введите пароль'
    ok = false
  }

  return ok
}

async function onSubmit() {
  if (loading.value) return
  submitMessage.value = null

  if (!validate()) return

  loading.value = true
  try {
    const accessTokenCookie = useCookie('access_token')

    const res = await $fetch('/api/users/login', {
      method: 'POST',
      body: {
        email: email.value.trim(),
        password: password.value
      }
    })

    accessTokenCookie.value = res.access_token

    submitMessage.value = {
      type: 'success',
      text: 'Вход выполнен. Перенаправляем...'
    }

    await navigateTo('/')
  } catch (error) {
    const detail = error?.data?.detail || error?.response?._data?.detail || error?.message || 'Не удалось выполнить вход'

    submitMessage.value = {
      type: 'error',
      text: detail
    }
  } finally {
    loading.value = false
  }
}
</script>
