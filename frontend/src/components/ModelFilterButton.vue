<template>
  <div class="multi-model-container">
    <!-- Button to Open Dropdown -->
    <BasicButton @click="toggleDropdown" :disabled="disabled || isLoading">
      <span v-if="isLoading" class="loading-spinner"></span>
      <span v-else> Filter Models </span>
    </BasicButton>

    <!-- Dropdown for Multi-Selection -->
    <div v-if="dropdownOpen" class="dropdown-menu">
      <label v-for="model in models" :key="model" class="dropdown-item">
        <input
          type="checkbox"
          :value="model"
          v-model="selectedModelsComputed"
        />
        {{ model }}
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import BasicButton from "./Buttons/BasicButton.vue";

const dropdownOpen = ref(false);
const isLoading = ref(false);

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  models: {
    type: Array,
    required: true,
  },
  selectedModels: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["selectModels"]);

const selectedModelsComputed = computed({
  get: () => props.selectedModels,
  set: (newValue) => {
    emit("selectModels", newValue);
  },
});

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};
</script>

<style scoped>
.multi-model-container {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  top: 40px;
  left: 10px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
  width: 150px;
  font: 0.8em sans-serif;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: #fff;
  border-right-color: #fff;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
