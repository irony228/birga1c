<template>
  <div class="pt-6">
    <UContainer>
      <!-- Заголовок страницы и переход к созданию заказа -->
      <div class="mb-4 flex items-center justify-between gap-3">
        <h1 class="text-2xl font-bold">
          Лента заказов
        </h1>
        <UButton
          v-if="isCustomer"
          to="/dashboard/createOrder"
          icon="i-lucide-plus"
        >
          Создать заказ
        </UButton>
      </div>

      <UAlert
        v-if="accessDeniedMessage"
        color="warning"
        variant="soft"
        class="mb-4"
        :description="accessDeniedMessage"
      />

      <!-- Ошибка загрузки заказов -->
      <UAlert
        v-if="errorMessage"
        color="error"
        variant="soft"
        class="mb-4"
        :description="errorMessage"
      />

      <!-- Состояние загрузки -->
      <div
        v-if="pending"
        class="flex flex-col gap-4"
      >
        <USkeleton class="h-36 w-full" />
        <USkeleton class="h-36 w-full" />
        <USkeleton class="h-36 w-full" />
      </div>

      <!-- Заказчик -->
      <template v-else-if="isCustomer">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-stretch h-[calc(100vh-220px)]">

          <!-- Открытые -->
          <section class="customer-zone customer-zone--open flex min-h-0 flex-col rounded-xl border-2 border-green-500/40 bg-green-500/10 p-4 dark:border-green-400/30 dark:bg-green-950/35">
            <h2 class="mb-3 text-lg font-semibold">Открытые</h2>

            <div v-if="customerOpenOrders.length === 0" class="flex flex-1 items-center justify-center">
              Нет открытых заказов
            </div>

            <UScrollArea v-else class="flex-1">
              <div class="flex flex-col gap-4 pr-2">
                <OrderCard
                  v-for="order in customerOpenOrders"
                  :key="order.id"
                  :order="order"
                  show-order-page-link
                />
              </div>
            </UScrollArea>
          </section>

          <!-- Правая колонка -->
          <div class="flex flex-col gap-4 min-h-0">

            <!-- В работе -->
            <section class="customer-zone customer-zone--progress flex min-h-0 flex-1 flex-col rounded-xl border-2 border-pink-500/40 bg-pink-500/10 p-4 dark:border-pink-400/30 dark:bg-pink-950/35">
              <h2 class="mb-3 text-lg font-semibold">В работе</h2>

              <div v-if="customerInProgressOrders.length === 0" class="flex flex-1 items-center justify-center">
                Нет заказов
              </div>

              <UScrollArea v-else class="flex-1">
                <div class="flex flex-col gap-3 pr-2">
                  <OrderCard
                    v-for="order in customerInProgressOrders"
                    :key="order.id"
                    :order="order"
                    show-order-page-link
                    compact
                  />
                </div>
              </UScrollArea>
            </section>

            <!-- Архив -->
            <section class="customer-zone customer-zone--archive flex min-h-0 flex-1 flex-col rounded-xl border-2 border-amber-400/50 bg-amber-400/15 p-4 dark:border-amber-400/35 dark:bg-amber-950/35">
              <h2 class="mb-3 text-lg font-semibold">Архив</h2>

              <div v-if="customerArchivedOrders.length === 0" class="flex flex-1 items-center justify-center">
                Пусто
              </div>

              <UScrollArea v-else class="flex-1">
                <div class="flex flex-col gap-3 pr-2">
                  <OrderCard
                    v-for="order in customerArchivedOrders"
                    :key="order.id"
                    :order="order"
                    show-order-page-link
                    compact
                  />
                </div>
              </UScrollArea>
            </section>

          </div>
        </div>
      </template>

      <!-- Worker -->
      <template v-else-if="isWorker">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-stretch h-[calc(100vh-220px)]">

          <!-- Открытые -->
          <section class="worker-zone worker-zone--market flex min-h-0 flex-col rounded-xl border-2 border-green-500/40 bg-green-500/10 p-4">
            <h2 class="mb-3 text-lg font-semibold">Открытые заказы</h2>

            <div v-if="workerOpenMarketOrders.length === 0" class="flex flex-1 items-center justify-center">
              Нет заказов
            </div>

            <UScrollArea v-else class="flex-1">
              <div class="flex flex-col gap-4 pr-2">
                <OrderCard
                  v-for="order in workerOpenMarketOrders"
                  :key="order.id"
                  :order="order"
                  show-bid-button
                  @bid-submitted="onBidSubmitted"
                />
              </div>
            </UScrollArea>
          </section>

          <div class="flex flex-col gap-4 min-h-0">

            <!-- В работе -->
            <section class="worker-zone worker-zone--active flex min-h-0 flex-1 flex-col rounded-xl border-2 border-pink-500/40 bg-pink-500/10 p-4">
              <h2 class="mb-3 text-lg font-semibold">В работе</h2>

              <div v-if="workerActiveOrders.length === 0" class="flex flex-1 items-center justify-center">
                Нет заказов
              </div>

              <UScrollArea v-else class="flex-1">
                <div class="flex flex-col gap-3 pr-2">
                  <OrderCard
                    v-for="order in workerActiveOrders"
                    :key="order.id"
                    :order="order"
                    compact
                    show-worker-complete-button
                    @order-completed="onOrderCompleted"
                  />
                </div>
              </UScrollArea>
            </section>

            <!-- Отклики -->
            <section class="worker-zone worker-zone--bidded flex min-h-0 flex-1 flex-col rounded-xl border-2 border-amber-400/50 bg-amber-400/15 p-4">
              <h2 class="mb-3 text-lg font-semibold">Мои отклики</h2>

              <div v-if="workerBiddedOrders.length === 0" class="flex flex-1 items-center justify-center">
                Нет откликов
              </div>

              <UScrollArea v-else class="flex-1">
                <div class="flex flex-col gap-3 pr-2">
                  <OrderCard
                    v-for="order in workerBiddedOrders"
                    :key="order.id"
                    :order="order"
                    compact
                  />
                </div>
              </UScrollArea>
            </section>

          </div>
        </div>
      </template>

    </UContainer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import OrderCard from '~/components/order/OrderCard.vue'

const route = useRoute()
const accessToken = useCookie('access_token')

function decodeJwtPayload(token) {
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

function scopesForRole(role) {
  if (role === 'customer') {
    return ['customer_open', 'customer_in_progress', 'customer_closed']
  }
  if (role === 'worker') {
    return ['worker_open_available', 'worker_in_progress', 'worker_bidded_active']
  }
  return []
}

/**
 * Подмечаем feedScope у каждого заказа — сами scope бэкенда.
 * Для worker нельзя делить только по status: «рынок» и «отклик» оба могут быть open.
 */
async function fetchOrdersFeed() {
  const token = accessToken.value
  if (!token || typeof token !== 'string' || !token.trim()) {
    return []
  }

  const role = decodeJwtPayload(token)?.role
  const scopes = scopesForRole(role)
  if (!scopes.length) {
    return []
  }

  const requestFetch = useRequestFetch()
  const results = await Promise.all(
    scopes.map(scope =>
      requestFetch('/api/orders', { query: { scope } })
    )
  )

  const merged = []
  const seen = new Set()
  for (let i = 0; i < results.length; i++) {
    const list = results[i]
    const scope = scopes[i]
    if (!Array.isArray(list)) continue
    for (const order of list) {
      if (order?.id == null || seen.has(order.id)) continue
      seen.add(order.id)
      merged.push({ ...order, feedScope: scope })
    }
  }

  merged.sort((a, b) => {
    const ta = new Date(a.created_at || 0).getTime()
    const tb = new Date(b.created_at || 0).getTime()
    return tb - ta
  })

  return merged
}

const { data, pending, error, refresh } = await useAsyncData('orders-feed', fetchOrdersFeed, {
  watch: [accessToken]
})

async function onBidSubmitted() {
  await refresh()
}

async function onOrderCompleted() {
  await refresh()
  await refreshNuxtData('current-user')
}

const statusLabelMap = {
  open: 'Открыт',
  in_progress: 'В работе',
  closed: 'Завершен'
}

const errorMessage = computed(() => {
  return error.value?.data?.detail || error.value?.message || ''
})

const userRole = computed(() => decodeJwtPayload(accessToken.value)?.role || null)
const isCustomer = computed(() => userRole.value === 'customer')
const isWorker = computed(() => userRole.value === 'worker')
const accessDeniedMessage = computed(() => {
  if (route.query.denied === 'create-order') {
    return 'Создавать заказ может только заказчик (customer).'
  }
  return ''
})

/** Карточка: feedScope с бэка, человекочитаемый status */
const orders = computed(() => {
  const rawOrders = Array.isArray(data.value) ? data.value : []

  return rawOrders.map(order => ({
    ...order,
    configuration: order.config_type,
    statusKey: order.status,
    feedScope: order.feedScope,
    status: statusLabelMap[order.status] || order.status
  }))
})

const customerOpenOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'customer_open')
)
const customerInProgressOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'customer_in_progress')
)
const customerArchivedOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'customer_closed')
)

const workerOpenMarketOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'worker_open_available')
)
const workerActiveOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'worker_in_progress')
)
const workerBiddedOrders = computed(() =>
  orders.value.filter(o => o.feedScope === 'worker_bidded_active')
)
</script>
