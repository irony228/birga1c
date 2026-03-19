<template>
  <UCard
    variant="soft"
    class="max-w-xl mx-auto mt-6 p-6"
  >
    <template #header>
      <h2 class="text-2xl font-semibold">
        Создать заказ
      </h2>
    </template>

    <form
      class="space-y-4 mt-4"
      @submit.prevent="handleSubmit"
    >
      <UFormField
        label="Название заказа"
        name="title"
        required
      >
        <UInput
          v-model="form.title"
          placeholder="Например: Разработка сайта"
          required
          class="w-full"
        />
      </UFormField>

      <UFormField
        label="Описание"
        name="description"
        required
      >
        <UTextarea
          v-model="form.description"
          placeholder="Краткое описание заказа"
          rows="4"
          required
          class="w-full"
        />
      </UFormField>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <UFormField
          label="Конфигурация / детали"
          name="configType"
          required
        >
          <UInput
            v-model="form.configType"
            placeholder="Пример: React + Node.js"
            required
            class="w-full"
          />
        </UFormField>

        <UFormField
          label="Бюджет (руб.)"
          name="budget"
          required
        >
          <UInput
            v-model.number="form.budget"
            type="number"
            min="0"
            placeholder="Например: 15000"
            required
            class="w-full"
          />
        </UFormField>
      </div>

      <div
        v-if="submitMessage"
        :class="submitMessage.type === 'error' ? 'text-sm text-red-500' : 'text-sm text-green-600'"
      >
        {{ submitMessage.text }}
      </div>

      <!-- Кнопка отправки -->
      <UButton
        type="submit"
        color="primary"
        class="w-full"
        :loading="loading"
        :disabled="loading"
      >
        Создать заказ
      </UButton>
    </form>
  </UCard>
</template>

<script setup>
import { reactive, ref } from 'vue'

// данные формы
const form = reactive({
  title: '',
  description: '',
  configType: '',
  budget: null
})

const loading = ref(false)
const submitMessage = ref(null)
const accessToken = useCookie('access_token')

const decodeJwtPayload = (token) => {
  if (!token || typeof token !== 'string') return null
  const parts = token.split('.')
  if (parts.length < 2) return null

  try {
    const normalized = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = atob(padded)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

const roleFromToken = decodeJwtPayload(accessToken.value)?.role
if (roleFromToken !== 'customer') {
  await navigateTo('/dashboard?denied=create-order')
}

// сабмит формы
const handleSubmit = async () => {
  if (loading.value) {
    return
  }

  submitMessage.value = null
  loading.value = true

  try {
    await $fetch('/api/orders', {
      method: 'POST',
      body: {
        title: form.title.trim(),
        description: form.description.trim(),
        config_type: form.configType.trim(),
        budget: Number(form.budget)
      }
    })

    submitMessage.value = {
      type: 'success',
      text: 'Заказ создан. Перенаправляем в ленту...'
    }

    await navigateTo('/dashboard')
  } catch (error) {
    const detail = error?.data?.detail || error?.response?._data?.detail || error?.message || 'Не удалось создать заказ'
    submitMessage.value = {
      type: 'error',
      text: detail
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* можно добавить кастомные стили, если нужно */
</style>
