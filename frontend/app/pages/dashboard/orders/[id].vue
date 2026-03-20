<template>
  <div class="pt-6">
    <UContainer>
      <div class="mb-6 flex flex-wrap items-center gap-3">
        <UButton
          to="/dashboard"
          color="neutral"
          variant="ghost"
          icon="i-lucide-arrow-left"
        >
          К ленте
        </UButton>
      </div>

      <UAlert
        v-if="errorMessage"
        color="error"
        variant="soft"
        class="mb-4"
        :description="errorMessage"
      />

      <UAlert
        v-if="actionMessage"
        color="error"
        variant="soft"
        class="mb-4"
        :description="actionMessage"
      />

      <div
        v-if="pending"
        class="space-y-4"
      >
        <USkeleton class="h-40 w-full" />
        <USkeleton class="h-64 w-full" />
      </div>

      <template v-else-if="order">
        <!-- Карточка заказа -->
        <UCard class="mb-8">
          <template #header>
            <div class="flex flex-wrap items-start justify-between gap-3">
              <h1 class="text-xl font-semibold">
                {{ order.title }}
              </h1>
              <span
                class="rounded px-2 py-1 text-sm"
                :class="orderStatusClass(order.status)"
              >
                {{ orderStatusLabel(order.status) }}
              </span>
            </div>
          </template>

          <div class="space-y-3 text-default">
            <p class="text-muted">
              {{ order.description }}
            </p>
            <div class="flex flex-wrap gap-4 text-sm">
              <div>
                <span class="text-muted">Конфигурация:</span>
                {{ order.config_type }}
              </div>
              <div>
                <span class="text-muted">Бюджет:</span>
                {{ formatBudget(order.budget) }} руб.
              </div>
              <div v-if="order.created_at">
                <span class="text-muted">Создан:</span>
                {{ formatDate(order.created_at) }}
              </div>
            </div>
          </div>
        </UCard>

        <!-- Отклики исполнителей -->
        <div class="mb-3 flex items-center justify-between gap-2">
          <h2 class="text-lg font-semibold">
            Отклики исполнителей
          </h2>
          <UButton
            v-if="!pending"
            color="neutral"
            variant="ghost"
            size="sm"
            icon="i-lucide-refresh-cw"
            :loading="refreshing"
            @click="onRefresh"
          >
            Обновить
          </UButton>
        </div>

        <div
          v-if="bids.length === 0"
          class="rounded-lg border border-dashed p-8 text-center text-muted"
        >
          Пока нет откликов на этот заказ.
        </div>

        <div
          v-else
          class="flex flex-col gap-4"
        >
          <UCard
            v-for="bid in bids"
            :key="bid.id"
            variant="subtle"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="space-y-2">
                <div class="font-medium">
                  {{ workerDisplayName(bid) }}
                </div>
                <div
                  v-if="bid.worker_email"
                  class="text-sm text-muted"
                >
                  {{ bid.worker_email }}
                </div>
                <div class="text-sm">
                  <span class="text-muted">Предложенная цена:</span>
                  {{ formatBudget(bid.price) }} руб.
                </div>
                <div
                  v-if="bid.comment"
                  class="text-sm text-muted"
                >
                  {{ bid.comment }}
                </div>
                <div class="text-xs text-muted">
                  {{ formatDate(bid.created_at) }} · {{ bidStatusLabel(bid.status) }}
                </div>
              </div>

              <div
                v-if="canManageBids && bid.status === 'pending'"
                class="flex shrink-0 flex-wrap gap-2"
              >
                <UButton
                  color="primary"
                  size="sm"
                  :loading="actionBidId === bid.id && actionKind === 'accept'"
                  :disabled="actionBidId !== null"
                  @click="acceptBid(bid.id)"
                >
                  Принять
                </UButton>
                <UButton
                  color="neutral"
                  variant="soft"
                  size="sm"
                  :loading="actionBidId === bid.id && actionKind === 'reject'"
                  :disabled="actionBidId !== null"
                  @click="rejectBid(bid.id)"
                >
                  Отклонить
                </UButton>
              </div>
            </div>
          </UCard>
        </div>
      </template>
    </UContainer>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const route = useRoute()
const orderId = computed(() => String(route.params.id || ''))

const { data, pending, error, refresh } = await useAsyncData(
  () => `order-detail-${orderId.value}`,
  async () => {
    const id = orderId.value
    if (!id) {
      return null
    }
    // SSR: обычный $fetch не пробрасывает Cookie → 401 на /api/*. См. useRequestFetch в доке Nuxt.
    const requestFetch = useRequestFetch()
    const [order, bids] = await Promise.all([
      requestFetch(`/api/orders/${id}`),
      requestFetch(`/api/bids/${id}`)
    ])
    return {
      order,
      bids: Array.isArray(bids) ? bids : []
    }
  },
  { watch: [orderId] }
)

const order = computed(() => data.value?.order ?? null)
const bids = computed(() => data.value?.bids ?? [])

const errorMessage = computed(() => {
  return error.value?.data?.detail || error.value?.message || ''
})

const canManageBids = computed(() => order.value?.status === 'open')

const refreshing = ref(false)
const actionBidId = ref(null)
const actionKind = ref(null)
const actionMessage = ref('')

async function onRefresh() {
  refreshing.value = true
  try {
    await refresh()
  } finally {
    refreshing.value = false
  }
}

function orderStatusLabel(status) {
  const map = { open: 'Открыт', in_progress: 'В работе', closed: 'Завершен' }
  return map[status] || status
}

function orderStatusClass(status) {
  switch (status) {
    case 'open': return 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200'
    case 'in_progress': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200'
    case 'closed': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200'
    default: return 'bg-elevated text-muted'
  }
}

function bidStatusLabel(status) {
  const map = {
    pending: 'Ожидает решения',
    accepted: 'Принят',
    rejected: 'Отклонён'
  }
  return map[status] || status
}

function workerDisplayName(bid) {
  if (bid.worker_name?.trim()) {
    return bid.worker_name
  }
  return `Исполнитель #${bid.worker_id}`
}

function formatBudget(value) {
  return Number(value || 0).toLocaleString('ru-RU')
}

function formatDate(value) {
  return new Date(value).toLocaleString('ru-RU')
}

async function acceptBid(bidId) {
  actionMessage.value = ''
  actionBidId.value = bidId
  actionKind.value = 'accept'
  try {
    await $fetch(`/api/orders/${orderId.value}/accept/${bidId}`, { method: 'POST' })
    await refresh()
  } catch (err) {
    console.error(err)
    actionMessage.value = err?.data?.detail || err?.message || 'Не удалось принять отклик'
  } finally {
    actionBidId.value = null
    actionKind.value = null
  }
}

async function rejectBid(bidId) {
  actionMessage.value = ''
  actionBidId.value = bidId
  actionKind.value = 'reject'
  try {
    await $fetch(`/api/bids/${bidId}/reject`, { method: 'POST' })
    await refresh()
  } catch (err) {
    console.error(err)
    actionMessage.value = err?.data?.detail || err?.message || 'Не удалось отклонить отклик'
  } finally {
    actionBidId.value = null
    actionKind.value = null
  }
}

const pageTitle = computed(() =>
  order.value?.title ? `${order.value.title} · Заказ` : 'Заказ'
)
useHead({ title: pageTitle })
</script>
