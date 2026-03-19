<template>
  <div class="border rounded-lg p-4 hover:shadow-lg transition-shadow duration-200 bg-white">
    <div class="flex justify-between items-start">
      <h2 class="text-lg font-semibold">{{ order.title }}</h2>
      <span :class="statusClass(order.status)" class="text-sm px-2 py-1 rounded">{{ order.status }}</span>
    </div>
    <p class="text-gray-700 mt-2">{{ order.description }}</p>

    <div class="mt-4 flex justify-between items-center">
      <div class="text-sm text-gray-500">{{ order.configuration }}</div>
      <div class="text-sm font-medium">{{ order.budget }} руб.</div>
    </div>

    <div class="mt-4 flex gap-2">
      <button class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition">
        Откликнуться
      </button>
      <button class="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 transition">
        Выбрать исполнителя
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  order: {
    type: Object,
    required: true
  }
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

<style scoped>
button {
  font-size: 0.875rem;
}
</style>