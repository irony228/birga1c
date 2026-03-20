<template>
  <div class="max-w-lg mx-auto pt-6">
    <UPageHero
      title="Профиль"
      description="Данные аккаунта и баланс."
    />

    <UCard class="mt-6 w-full">
      <template #header>
        <h2 class="text-lg font-semibold">
          Баланс
        </h2>
      </template>

      <div
        v-if="pending"
        class="p-4 space-y-2"
      >
        <USkeleton class="h-8 w-full" />
        <USkeleton class="h-8 w-2/3" />
      </div>

      <div
        v-else-if="me"
        class="p-4 sm:p-6 space-y-4"
      >
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="rounded-lg border border-default p-4">
            <div class="text-xs text-muted">
              Доступно
            </div>
            <div class="text-xl font-semibold tabular-nums">
              {{ formattedBalance }}
            </div>
          </div>
          <div class="rounded-lg border border-default p-4">
            <div class="text-xs text-muted">
              Заморожено
            </div>
            <div class="text-xl font-semibold tabular-nums">
              {{ formattedFrozen }}
            </div>
          </div>
        </div>

        <p class="text-sm text-muted">
          Замороженные средства удерживаются по активным заказам до завершения или отмены.
        </p>

        <div class="flex flex-wrap gap-2 items-end">
          <UInput
            v-model.number="topUpAmount"
            type="number"
            label="Сумма пополнения (₽)"
            :min="1"
            class="w-full sm:w-48"
          />
          <UButton
            type="button"
            color="primary"
            :loading="topUpLoading"
            :disabled="topUpLoading"
            @click="onTopUp"
          >
            Пополнить
          </UButton>
        </div>

        <UAlert
          v-if="banner"
          :color="banner.kind === 'error' ? 'error' : 'success'"
          variant="soft"
          :description="banner.text"
        />
      </div>

      <div
        v-else
        class="p-4 text-sm text-muted"
      >
        Не удалось загрузить профиль. Войдите снова.
      </div>
    </UCard>

    <UCard
      v-if="me"
      class="mt-6 w-full"
    >
      <template #header>
        <h2 class="text-lg font-semibold">
          Аккаунт
        </h2>
      </template>
      <div class="p-4 sm:p-6 space-y-2 text-sm">
        <div>
          <span class="text-muted">Email:</span>
          {{ me.email }}
        </div>
        <div v-if="me.name">
          <span class="text-muted">Имя:</span>
          {{ me.name }}
        </div>
        <div>
          <span class="text-muted">Роль:</span>
          {{ me.role === 'customer' ? 'Заказчик' : me.role === 'worker' ? 'Исполнитель' : me.role }}
        </div>
        <div class="pt-2">
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-log-out"
            @click="logout"
          >
            Выйти
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const { me, refresh, pending, formattedBalance, formattedFrozen } = useCurrentUser()

const topUpAmount = ref(10000)
const topUpLoading = ref(false)
const banner = ref(null)

async function onTopUp() {
  banner.value = null
  const amount = Number(topUpAmount.value)
  if (!Number.isFinite(amount) || amount <= 0) {
    banner.value = { kind: 'error', text: 'Укажите сумму больше нуля' }
    return
  }
  topUpLoading.value = true
  try {
    await $fetch('/api/users/top-up', {
      method: 'POST',
      body: { amount }
    })
    await refresh()
    banner.value = { kind: 'success', text: 'Баланс пополнен.' }
  } catch (err) {
    const d = err?.data?.detail || err?.response?._data?.detail || err?.message
    banner.value = { kind: 'error', text: d || 'Не удалось пополнить' }
  } finally {
    topUpLoading.value = false
  }
}

const accessToken = useCookie('access_token')

async function logout() {
  accessToken.value = null
  await navigateTo('/')
}
</script>
