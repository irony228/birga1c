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
          label="Имя"
          name="name"
          :error="errors.name || undefined"
          required
          class="w-full"
        >
          <UInput
            v-model="name"
            type="text"
            autocomplete="name"
            placeholder="Как к вам обращаться"
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
const name = ref('')
const confirmPassword = ref('')
const role = ref('customer')

const loading = ref(false)
const errors = ref({
  email: '',
  password: '',
  name: '',
  confirmPassword: '',
  role: ''
})

const submitMessage = ref(null)
// submitMessage: { type: 'error' | 'success', text: string }

const roleItems = [
  { value: 'customer', label: 'Заказчик' },
  { value: 'worker', label: 'Исполнитель' }
]

function validate() {
  errors.value.email = ''
  errors.value.password = ''
  errors.value.name = ''
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

  if (!name.value.trim()) {
    errors.value.name = 'Введите имя'
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
    await $fetch('/api/users/register', {
      method: 'POST',
      body: {
        email: email.value.trim(),
        password: password.value,
        name: name.value.trim(),
        role: role.value
      }
    })

    submitMessage.value = {
      type: 'success',
      text: 'Аккаунт создан. Теперь можно войти.'
    }
  } catch (error) {
    const detail = error?.data?.detail || error?.response?._data?.detail || error?.message || 'Не удалось выполнить регистрацию'

    submitMessage.value = {
      type: 'error',
      text: detail
    }
  } finally {
    loading.value = false
  }
}
</script>
