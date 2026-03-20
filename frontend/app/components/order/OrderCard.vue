<template>
  <UCard :class="cardThemeClass">
    <!-- Шапка карточки -->
    <template #header>
      <div class="flex justify-between items-start">
        <h2 class="text-lg font-semibold">
          <ULink :to="`dashboard/orders/${order.id}`">{{ order.title }}</ULink>
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

    <!-- Футер: отклик исполнителя на открытый заказ из ленты -->
    <template #footer>
      <!-- Ссылка на страницу заказа для заказчика (отклики) -->
      <div
        v-if="showOrderPageLink && !showBidSection"
        class="flex flex-wrap gap-2"
      >
        <UButton
          :to="`/dashboard/orders/${order.id}`"
          color="neutral"
          variant="soft"
          size="sm"
          icon="i-lucide-users"
        >
          Отклики
        </UButton>
      </div>

      <div
        v-else-if="showBidSection"
        class="flex flex-col gap-3"
      >
        <div
          v-if="!bidFormOpen"
          class="flex flex-wrap gap-2"
        >
          <UButton
            color="primary"
            icon="i-lucide-send"
            @click="openBidForm"
          >
            Откликнуться
          </UButton>
        </div>

        <div
          v-else
          class="space-y-3 rounded-lg border border-default p-3"
        >
          <UAlert
            v-if="bidError"
            color="error"
            variant="soft"
            :description="bidError"
          />
          <UInput
            v-model.number="bidPrice"
            type="number"
            label="Ваша цена (руб.)"
            :min="0"
            step="1"
            required
          />
          <UTextarea
            v-model="bidComment"
            label="Комментарий к отклику"
            placeholder="Сроки, опыт, детали..."
            :rows="3"
          />
          <div class="flex flex-wrap gap-2">
            <UButton
              color="primary"
              :loading="bidSubmitting"
              :disabled="bidSubmitting"
              @click="submitBid"
            >
              Отправить отклик
            </UButton>
            <UButton
              color="neutral"
              variant="ghost"
              :disabled="bidSubmitting"
              @click="cancelBidForm"
            >
              Отмена
            </UButton>
          </div>
        </div>
      </div>
    </template>
  </UCard>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  /** Показать отклик (только для исполнителя в зоне открытых заказов) */
  showBidButton: {
    type: Boolean,
    default: false
  },
  /** Ссылка «Отклики» на страницу заказа (заказчик) */
  showOrderPageLink: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['bid-submitted'])

const showBidSection = computed(() => {
  return props.showBidButton && props.order.statusKey === 'open'
})

const bidFormOpen = ref(false)
const bidPrice = ref(null)
const bidComment = ref('')
const bidSubmitting = ref(false)
const bidError = ref('')

watch(
  () => props.order.id,
  () => {
    bidFormOpen.value = false
    bidError.value = ''
  }
)

function openBidForm() {
  bidError.value = ''
  bidPrice.value = Number(props.order.budget) || null
  bidComment.value = ''
  bidFormOpen.value = true
}

function cancelBidForm() {
  bidFormOpen.value = false
  bidError.value = ''
}

async function submitBid() {
  const price = Number(bidPrice.value)
  if (!Number.isFinite(price) || price <= 0) {
    bidError.value = 'Укажите цену больше нуля'
    return
  }

  bidSubmitting.value = true
  bidError.value = ''

  try {
    await $fetch(`/api/bids/${props.order.id}`, {
      method: 'POST',
      body: {
        price,
        comment: bidComment.value.trim() || ''
      }
    })
    bidFormOpen.value = false
    emit('bid-submitted')
  } catch (err) {
    bidError.value = err?.data?.detail || err?.response?._data?.detail || err?.message || 'Не удалось отправить отклик'
  } finally {
    bidSubmitting.value = false
  }
}

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
