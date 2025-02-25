<template>
  <div class="evaluation-container">
    <BasicButton @click="performEvaluation" :disabled="disabled"
      >LLM Evaluation</BasicButton
    >
    <span v-if="status === 'success'" class="success">✔️</span>
    <span v-if="status === 'error'" class="error">❌</span>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import BasicButton from "./Buttons/BasicButton.vue";

const status = ref(null);

defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  id: Number,
});

const performEvaluation = async () => {
  try {
    const response = await axios.post("/api/llm/evaluate", { id });
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

.success {
  color: green;
  font-size: 1.5rem;
}

.error {
  color: red;
  font-size: 1.5rem;
}
</style>
