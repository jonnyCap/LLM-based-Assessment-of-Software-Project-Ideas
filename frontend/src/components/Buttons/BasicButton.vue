<template>
  <button class="base-button" @click="$emit('click')">
    <slot></slot>
  </button>
</template>

<script setup>
defineEmits(["click"]);
</script>

<style scoped>
.base-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  font-size: 1rem;
  transition: background-color 0.3s;
  margin: 0 10px;
}

.base-button:hover {
  background-color: #0056b3;
}
</style>
