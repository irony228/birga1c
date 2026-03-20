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

      <!-- Заказчик: три зоны (открытые | в работе | архив) -->
      <template v-else-if="isCustomer">
        <div
          class="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-stretch"
        >
          <!-- Зелёная зона: мои открытые заказы -->
          <section
            class="customer-zone customer-zone--open flex min-h-[200px] flex-col rounded-xl border-2 border-green-500/40 bg-green-500/10 p-4 dark:border-green-400/30 dark:bg-green-950/35"
            aria-labelledby="customer-zone-open-title"
          >
            <h2
              id="customer-zone-open-title"
              class="mb-3 flex items-center gap-2 text-lg font-semibold text-green-900 dark:text-green-100"
            >
              <span
                class="inline-block size-3 shrink-0 rounded-full bg-green-500"
                aria-hidden="true"
              />
              Открытые
            </h2>
            <div
              v-if="customerOpenOrders.length === 0"
              class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-green-600/30 p-6 text-center text-sm text-muted"
            >
              Нет открытых заказов
            </div>
            <div
              v-else
              class="flex flex-col gap-4"
            >
              <OrderCard
                v-for="order in customerOpenOrders"
                :key="order.id"
                :order="order"
                show-order-page-link
              />
            </div>
          </section>

          <!-- Правая колонка: розовая (в работе) + жёлтая (архив) -->
          <div class="flex flex-col gap-4">
            <!-- Розовая зона: в работе -->
            <section
              class="customer-zone customer-zone--progress flex min-h-[180px] flex-1 flex-col rounded-xl border-2 border-pink-500/40 bg-pink-500/10 p-4 dark:border-pink-400/30 dark:bg-pink-950/35"
              aria-labelledby="customer-zone-progress-title"
            >
              <h2
                id="customer-zone-progress-title"
                class="mb-3 flex items-center gap-2 text-lg font-semibold text-pink-900 dark:text-pink-100"
              >
                <span
                  class="inline-block size-3 shrink-0 rounded-full bg-pink-500"
                  aria-hidden="true"
                />
                В работе
              </h2>
              <div
                v-if="customerInProgressOrders.length === 0"
                class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-pink-600/30 p-6 text-center text-sm text-muted"
              >
                Нет заказов в работе
              </div>
              <div
                v-else
                class="flex flex-col gap-4"
              >
                <OrderCard
                  v-for="order in customerInProgressOrders"
                  :key="order.id"
                  :order="order"
                  show-order-page-link
                />
              </div>
            </section>

            <!-- Жёлтая зона: архив (завершённые) -->
            <section
              class="customer-zone customer-zone--archive flex min-h-[180px] flex-1 flex-col rounded-xl border-2 border-amber-400/50 bg-amber-400/15 p-4 dark:border-amber-400/35 dark:bg-amber-950/35"
              aria-labelledby="customer-zone-archive-title"
            >
              <h2
                id="customer-zone-archive-title"
                class="mb-3 flex items-center gap-2 text-lg font-semibold text-amber-950 dark:text-amber-100"
              >
                <span
                  class="inline-block size-3 shrink-0 rounded-full bg-amber-400"
                  aria-hidden="true"
                />
                Архив (завершённые)
              </h2>
              <div
                v-if="customerArchivedOrders.length === 0"
                class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-amber-600/30 p-6 text-center text-sm text-muted"
              >
                Архив пуст
              </div>
              <div
                v-else
                class="flex flex-col gap-4"
              >
                <OrderCard
                  v-for="order in customerArchivedOrders"
                  :key="order.id"
                  :order="order"
                  show-order-page-link
                />
              </div>
            </section>
          </div>
        </div>
      </template>

      <!-- Исполнитель: открытая лента | в работе | отклики -->
      <template v-else-if="isWorker">
        <div
          class="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:items-stretch"
        >
          <!-- Зелёная зона: все открытые заказы, на которые исполнитель ещё не откликался -->
          <section
            class="worker-zone worker-zone--market flex min-h-[200px] flex-col rounded-xl border-2 border-green-500/40 bg-green-500/10 p-4 dark:border-green-400/30 dark:bg-green-950/35"
            aria-labelledby="worker-zone-open-title"
          >
            <h2
              id="worker-zone-open-title"
              class="mb-3 flex items-center gap-2 text-lg font-semibold text-green-900 dark:text-green-100"
            >
              <span
                class="inline-block size-3 shrink-0 rounded-full bg-green-500"
                aria-hidden="true"
              />
              Открытые заказы
            </h2>
            <p class="mb-3 text-xs text-muted">
              Доступные заявки без вашего отклика
            </p>
            <div
              v-if="workerOpenMarketOrders.length === 0"
              class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-green-600/30 p-6 text-center text-sm text-muted"
            >
              Нет доступных открытых заказов
            </div>
            <div
              v-else
              class="flex flex-col gap-4"
            >
              <OrderCard
                v-for="order in workerOpenMarketOrders"
                :key="order.id"
                :order="order"
                show-bid-button
                @bid-submitted="onBidSubmitted"
              />
            </div>
          </section>

          <div class="flex flex-col gap-4">
            <!-- Розовая зона: взятые в работу -->
            <section
              class="worker-zone worker-zone--active flex min-h-[180px] flex-1 flex-col rounded-xl border-2 border-pink-500/40 bg-pink-500/10 p-4 dark:border-pink-400/30 dark:bg-pink-950/35"
              aria-labelledby="worker-zone-active-title"
            >
              <h2
                id="worker-zone-active-title"
                class="mb-3 flex items-center gap-2 text-lg font-semibold text-pink-900 dark:text-pink-100"
              >
                <span
                  class="inline-block size-3 shrink-0 rounded-full bg-pink-500"
                  aria-hidden="true"
                />
                В работе
              </h2>
              <p class="mb-3 text-xs text-muted">
                Заказы, за которые вы назначены исполнителем
              </p>
              <div
                v-if="workerActiveOrders.length === 0"
                class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-pink-600/30 p-6 text-center text-sm text-muted"
              >
                Нет заказов в работе
              </div>
              <div
                v-else
                class="flex flex-col gap-4"
              >
                <OrderCard
                  v-for="order in workerActiveOrders"
                  :key="order.id"
                  :order="order"
                />
              </div>
            </section>

            <!-- Жёлтая зона: откликнулись, ждём решения -->
            <section
              class="worker-zone worker-zone--bidded flex min-h-[180px] flex-1 flex-col rounded-xl border-2 border-amber-400/50 bg-amber-400/15 p-4 dark:border-amber-400/35 dark:bg-amber-950/35"
              aria-labelledby="worker-zone-bidded-title"
            >
              <h2
                id="worker-zone-bidded-title"
                class="mb-3 flex items-center gap-2 text-lg font-semibold text-amber-950 dark:text-amber-100"
              >
                <span
                  class="inline-block size-3 shrink-0 rounded-full bg-amber-400"
                  aria-hidden="true"
                />
                Мои отклики
              </h2>
              <p class="mb-3 text-xs text-muted">
                Заказы с активным откликом (ожидание выбора заказчиком)
              </p>
              <div
                v-if="workerBiddedOrders.length === 0"
                class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-amber-600/30 p-6 text-center text-sm text-muted"
              >
                Нет активных откликов
              </div>
              <div
                v-else
                class="flex flex-col gap-4"
              >
                <OrderCard
                  v-for="order in workerBiddedOrders"
                  :key="order.id"
                  :order="order"
                />
              </div>
            </section>
          </div>
        </div>
      </template>

      <!-- Прочие роли / нет данных -->
      <template v-else>
        <div class="rounded-lg border border-dashed p-8 text-center text-muted">
          Нет заказов для отображения или роль не поддерживается.
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
