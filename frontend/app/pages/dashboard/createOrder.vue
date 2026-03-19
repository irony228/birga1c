<template>
  <UCard variant="soft" class="max-w-xl mx-auto p-6">
    <template #header>
      <h2 class="text-2xl font-semibold">Создать заказ</h2>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-4 mt-4">
      <!-- Название заказа -->
      <UInput
        v-model="form.title"
        label="Название заказа"
        placeholder="Например: Разработка сайта"
        required
      />

      <!-- Описание -->
      <UTextarea
        v-model="form.description"
        label="Описание"
        placeholder="Краткое описание заказа"
        rows="4"
        required
      />

      <!-- Конфигурация / детали -->
      <UInput
        v-model="form.configuration"
        label="Конфигурация / детали"
        placeholder="Пример: React + Node.js"
      />

      <!-- Бюджет -->
      <UInput
        v-model.number="form.budget"
        label="Бюджет (руб.)"
        type="number"
        min="0"
        placeholder="Например: 15000"
        required
      />

      <!-- Статус -->
      <USelect
        v-model="form.status"
        label="Статус заказа"
        :items="statusOptions"
        required
      />

      <!-- Кнопка отправки -->
      <UButton type="submit" color="primary" class="w-full">
        Создать заказ
      </UButton>
    </form>
  </UCard>
</template>

<script setup>
import { reactive } from "vue";

// данные формы
const form = reactive({
  title: "",
  description: "",
  configuration: "",
  budget: null,
  status: "Открыт"
});

// варианты для селекта
const statusOptions = [
  { label: "Открыт", value: "Открыт" },
  { label: "В работе", value: "В работе" },
  { label: "Завершен", value: "Завершен" }
];

// сабмит формы
const handleSubmit = () => {
  console.log("Создан заказ:", { ...form });

  // сброс формы
  form.title = "";
  form.description = "";
  form.configuration = "";
  form.budget = null;
  form.status = "Открыт";

  // можно эмитить событие для родителя
  // emit('submit', { ...form })
};
</script>

<style scoped>
/* можно добавить кастомные стили, если нужно */
</style>