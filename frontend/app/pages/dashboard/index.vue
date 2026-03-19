<template>
  <div>
    <UContainer>
        <h1 class="text-2xl font-bold mb-4">Лента заказов</h1>

        <div class="mb-4 flex gap-2">
            <USelect 
                v-model="filterConfig" 
                :items="configOptions" 
                class="w-48" 
                placeholder="Все конфигурации"
                clearable
            />

            <USelect 
                v-model="filterStatus" 
                :items="statusOptions" 
                class="w-48" 
                placeholder="Все статусы"
                clearable
            />
        </div>

        <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-4">
                <OrderCard
                    v-for="order in filteredOrders"
                    :key="order.id"
                    :order="order"
                />
                </div>
        </div>
    </UContainer>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { orders } from "~/data/orders.js";
import OrderCard from "~/components/order/OrderCard.vue";

const filterConfig = ref("");
const filterStatus = ref("");

const configurations = Array.from(new Set(orders.map(o => o.configuration)));
const statuses = Array.from(new Set(orders.map(o => o.status)));

const configOptions = [
  { label: "Все конфигурации", value: null },
  ...configurations.map(config => ({ label: config, value: config }))
];

const statusOptions = [
    { label: "Все статусы", value: null },
    ...statuses.map(status => ({ label: status, value: status}))
];

const filteredOrders = computed(() => {
  return orders.filter(o => {
    return (!filterConfig.value || o.configuration === filterConfig.value) &&
           (!filterStatus.value || o.status === filterStatus.value);
  });
});

const statusClass = (status) => {
  switch (status) {
    case "Открыт": return "bg-green-100 text-green-800";
    case "В работе": return "bg-yellow-100 text-yellow-800";
    case "Завершен": return "bg-blue-100 text-blue-800";
    default: return "bg-gray-100 text-gray-800";
  }
};
</script>