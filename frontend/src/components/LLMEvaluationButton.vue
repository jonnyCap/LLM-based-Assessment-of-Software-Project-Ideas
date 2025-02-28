<template>
  <div class="evaluation-container">
    <!-- Model Selection -->
    <select v-model="selectedModel" class="model-dropdown">
      <option v-for="model in models" :key="model" :value="model">
        {{ model }}
      </option>
    </select>

    <!-- Button with Loading State -->
    <BasicButton
      @click="performEvaluation"
      :disabled="disabled || !selectedModel || isLoading"
    >
      <span v-if="isLoading" class="loading-spinner"></span>
      <span v-else>LLM Evaluation</span>
    </BasicButton>

    <!-- Status Icons -->
    <span v-if="status === 'success'" class="success">✔️</span>
    <span v-if="status === 'error'" class="error">❌</span>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import BasicButton from "./Buttons/BasicButton.vue";

const status = ref(null);
const isLoading = ref(false); // Loading state
const models = ref([]);
const selectedModel = ref(null);

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  id: Number,
});

const emit = defineEmits(["evaluationSuccess"]);

onMounted(async () => {
  try {
    const response = await axios.get("/api/llm/models");
    models.value = response.data;
    if (models.value.length > 0) {
      selectedModel.value = models.value[0];
    } else {
      console.error("No LLM models found");
    }
  } catch (error) {
    console.error("Failed to fetch LLM models:", error);
  }
});

const performEvaluation = async () => {
  if (!selectedModel.value || props.disabled || isLoading.value) return;

  isLoading.value = true; // Start loading
  status.value = null; // Reset status

  try {
    const response = await axios.post("/api/llm/evaluate", {
      model: selectedModel.value,
      id: props.id,
    });

    if (response.status === 200) {
      status.value = "success";
      emit("evaluationSuccess"); // Notify parent
    } else {
      status.value = "error";
    }
  } catch (error) {
    status.value = "error";
  } finally {
    isLoading.value = false; // Stop loading after API call
  }
};
</script>

<style scoped>
.evaluation-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-dropdown {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

.success {
  color: green;
  font-size: 1.5rem;
}

.error {
  color: red;
  font-size: 1.5rem;
}

/* Loading Spinner */
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

/* Animation for Spinner */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
