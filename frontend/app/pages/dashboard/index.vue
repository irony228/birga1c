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

      <!-- Фильтр ленты по статусу -->
      <div class="mb-4 flex flex-wrap gap-2">
        <USelect
          v-model="filterStatus"
          :items="statusOptions"
          class="w-56"
          placeholder="Все статусы"
          clearable
        />
      </div>

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

      <!-- Пустая выдача после фильтрации -->
      <div
        v-else-if="filteredOrders.length === 0"
        class="rounded-lg border border-dashed p-8 text-center text-muted"
      >
        Заказы не найдены. Попробуйте изменить фильтры.
      </div>

      <!-- Список карточек заказов -->
      <div
        v-else
        class="flex flex-col gap-4"
      >
        <OrderCard
          v-for="order in filteredOrders"
          :key="order.id"
          :order="order"
        />
      </div>
    </UContainer>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import OrderCard from '~/components/order/OrderCard.vue'

const filterConfig = ref(null)
const filterStatus = ref(null)
const route = useRoute()
const accessToken = useCookie('access_token')

const { data, pending, error } = await useAsyncData('orders-feed', () => $fetch('/api/orders'))

const statusLabelMap = {
  open: 'Открыт',
  in_progress: 'В работе',
  closed: 'Завершен'
}

const errorMessage = computed(() => {
  return error.value?.data?.detail || error.value?.message || ''
})

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

const userRole = computed(() => decodeJwtPayload(accessToken.value)?.role || null)
const isCustomer = computed(() => userRole.value === 'customer')
const accessDeniedMessage = computed(() => {
  if (route.query.denied === 'create-order') {
    return 'Создавать заказ может только заказчик (customer).'
  }
  return ''
})

const orders = computed(() => {
  const rawOrders = Array.isArray(data.value) ? data.value : []

  return rawOrders.map(order => ({
    ...order,
    configuration: order.config_type,
    status: statusLabelMap[order.status] || order.status
  }))
})

const statuses = computed(() => {
  return Array.from(new Set(orders.value.map(order => order.status).filter(Boolean)))
})

const statusOptions = computed(() => {
  return [
    { label: 'Все статусы', value: null },
    ...statuses.value.map(status => ({ label: status, value: status }))
  ]
})

const filteredOrders = computed(() => {
  return orders.value.filter((order) => {
    const statusOk = !filterStatus.value || order.status === filterStatus.value
    return statusOk
  })
})
</script>
