<template>
  <div class="evaluation-container">
    <select v-model="selectedModel" class="model-dropdown">
      <option v-for="model in models" :key="model" :value="model">
        {{ model }}
      </option>
    </select>
    <BasicButton
      @click="performEvaluation"
      :disabled="disabled || !selectedModel"
    >
      LLM Evaluation
    </BasicButton>
    <span v-if="status === 'success'" class="success">✔️</span>
    <span v-if="status === 'error'" class="error">❌</span>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import BasicButton from "./Buttons/BasicButton.vue";

const status = ref(null);
const models = ref([]);
const selectedModel = ref(null);

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  id: Number,
});

onMounted(async () => {
  try {
    const response = await axios.get("/api/llm/models");
    models.value = response.data;
    if (models.value.length > 0) {
      selectedModel.value = models.value[0];
    }
  } catch (error) {
    console.error("Failed to fetch LLM models:", error);
  }
});

const performEvaluation = async () => {
  if (!selectedModel.value || props.disabled) return;
  try {
    const response = await axios.post("/api/llm/evaluate", {
      model: selectedModel.value,
      id: props.id,
    });
    if (response.status === 200) {
      status.value = "success";
    } else {
      status.value = "error";
    }
  } catch (error) {
    status.value = "error";
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
</style>
