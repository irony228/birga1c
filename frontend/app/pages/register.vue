<template>
  <div class="max-w-lg mx-auto">
    <UPageHero
      title="Регистрация"
      description="Создайте аккаунт, чтобы начать пользоваться биржей."
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
            autocomplete="new-password"
            placeholder="••••••••"
            required
            class="w-full"
          />
        </UFormField>

        <UFormField
          label="Повторите пароль"
          name="confirmPassword"
          :error="errors.confirmPassword || undefined"
          required
          class="w-full"
        >
          <UInput
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="••••••••"
            required
            class="w-full"
          />
        </UFormField>

        <UFormField
          label="Роль"
          name="role"
          :error="errors.role || undefined"
          required
          class="w-full"
        >
          <URadioGroup
            v-model="role"
            :items="roleItems"
            name="role"
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
          Создать аккаунт
        </UButton>

        <div class="text-center text-sm text-muted">
          Уже есть аккаунт?
          <NuxtLink to="/login" class="text-orange-500 hover:text-orange-600">Вход</NuxtLink>
        </div>
      </form>
    </UCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('Заказчик')

const loading = ref(false)
const errors = ref({
  email: '',
  password: '',
  confirmPassword: '',
  role: ''
})

const submitMessage = ref(null)
// submitMessage: { type: 'error' | 'success', text: string }

const roleItems = [
  { value: 'Заказчик', label: 'Заказчик' },
  { value: 'Исполнитель', label: 'Исполнитель' }
]

function validate() {
  errors.value.email = ''
  errors.value.password = ''
  errors.value.confirmPassword = ''
  errors.value.role = ''

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

  if (!confirmPassword.value) {
    errors.value.confirmPassword = 'Повторите пароль'
    ok = false
  } else if (confirmPassword.value !== password.value) {
    errors.value.confirmPassword = 'Пароли не совпадают'
    ok = false
  }

  if (!role.value) {
    errors.value.role = 'Выберите роль'
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
    // Пока нет бэкенда — только демонстрация UI.
    await new Promise(r => setTimeout(r, 700))
    submitMessage.value = {
      type: 'success',
      text: 'Заглушка: пока нет бэкенда, регистрация не выполняется.'
    }
  } finally {
    loading.value = false
  }
}
</script>
