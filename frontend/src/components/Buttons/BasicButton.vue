<template>
  <button class="base-button" @click="$emit('click')" :disabled="disabled">
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["click"]);
</script>

<style scoped>
.base-button {
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  font-size: 0.9rem;
  transition: background-color 0.3s;
  margin: 0 10px;
}

.base-button:hover {
  background-color: #0056b3;
}

.base-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
