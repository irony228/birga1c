<template>
  <UCard :class="cardThemeClass">
    <!-- Шапка карточки -->
    <template #header>
      <div class="flex justify-between items-start">
        <h2 class="text-lg font-semibold">
          {{ order.title }}
        </h2>
        <span
          :class="statusClass(order.status)"
          class="text-sm px-2 py-1 rounded"
        >
          {{ order.status }}
        </span>
      </div>
    </template>

    <!-- Основное содержимое -->
    <div class="mt-2 text-gray-700 dark:text-gray-200">
      <p>{{ order.description }}</p>

      <div class="mt-4 flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
        <div>{{ order.configuration || order.config_type }}</div>
        <div class="font-medium text-gray-900 dark:text-gray-100">
          {{ formatBudget(order.budget) }} руб.
        </div>
      </div>

      <div
        v-if="order.created_at"
        class="mt-2 text-xs text-gray-400"
      >
        Создан: {{ formatDate(order.created_at) }}
      </div>
    </div>

    <!-- Футер карточки с действиями -->
    <template #footer>
      <div class="flex gap-2">
        <UButton
          color="neutral"
          variant="soft"
          disabled
        >
          Отклик (скоро)
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<script setup>
import { defineProps, computed } from 'vue'

defineProps({
  order: {
    type: Object,
    required: true
  }
})

const statusClass = (status) => {
  switch (status) {
    case 'Открыт': return 'bg-green-100 text-green-800'
    case 'В работе': return 'bg-yellow-100 text-yellow-800'
    case 'Завершен': return 'bg-blue-100 text-blue-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const formatBudget = (value) => {
  return Number(value || 0).toLocaleString('ru-RU')
}

const formatDate = (value) => {
  return new Date(value).toLocaleString('ru-RU')
}

// Класс карточки, который зависит от темы
const cardThemeClass = computed(() => {
  return `
    ${useColorMode().value === 'dark'
      ? 'bg-elevated/50 dark:bg-elevated/70'
      : 'bg-elevated/70 light:bg-elevated/50'}
  `
})
</script>
