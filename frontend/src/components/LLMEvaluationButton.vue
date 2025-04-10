<template>
  <div class="evaluation-container">
    <!-- Model Selection -->
    <select v-model="selectedModel" class="model-dropdown">
      <option v-for="model in models" :key="model" :value="model">
        {{ model }}
      </option>
    </select>

    <!-- Advanced Prompt Checkbox -->
    <label class="checkbox-label">
      <input type="checkbox" v-model="advancedPrompt" />
      Adv. Prompt
    </label>

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
import { ref, watch } from "vue";
import BasicButton from "./Buttons/BasicButton.vue";
import axios from "axios";

const status = ref(null);
const isLoading = ref(false);
const selectedModel = ref(null);
const advancedPrompt = ref(false);

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  id: Number,
  models: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["evaluationSuccess"]);

// Set default selected model when models are available
watch(
  () => props.models,
  (newModels) => {
    if (newModels.length > 0 && !selectedModel.value) {
      selectedModel.value = newModels[0];
    }
  },
  { immediate: true }
);

const performEvaluation = async () => {
  if (!selectedModel.value || props.disabled || isLoading.value) {
    console.log("Evaluation is disabled or already in progress.");
  }

  isLoading.value = true;
  status.value = null;

  try {
    const response = await axios.post("/api/llm/evaluate", {
      model: selectedModel.value,
      id: props.id,
      advanced_prompt: advancedPrompt.value,
    });

    if (response.status === 200) {
      status.value = "success";
      emit("evaluationSuccess");
    } else {
      status.value = "error";
    }
  } catch (error) {
    console.log("Error during evaluation:", error);
    status.value = "error";
  } finally {
    isLoading.value = false;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.7rem;
  cursor: pointer;
}

.checkbox-label input {
  cursor: pointer;
}
</style>
