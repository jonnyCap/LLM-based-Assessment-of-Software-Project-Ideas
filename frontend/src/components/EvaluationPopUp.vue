<template>
  <div>
    <BasicButton @click="openPopup" :disabled="disabled">Evaluate</BasicButton>

    <div v-if="isPopupOpen" class="popup-overlay">
      <div class="popup">
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>

        <div v-for="(value, key) in evaluation" :key="key" class="input-group">
          <label :for="key">{{
            key.charAt(0).toUpperCase() + key.slice(1)
          }}</label>
          <input
            type="number"
            :id="key"
            v-model.number="evaluation[key]"
            min="1"
            max="10"
          />
        </div>

        <div class="input-group">
          <label for="feedback">Additional Feedback</label>
          <textarea id="feedback" v-model="feedback" rows="4"></textarea>
        </div>

        <div class="button-group">
          <button @click="submitEvaluation" class="submit-button">
            Submit
          </button>
          <button @click="closePopup" class="close-button">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps } from "vue";
import BasicButton from "./Buttons/BasicButton.vue";
import axios from "axios";

const props = defineProps({
  title: String,
  description: String,
  disabled: {
    type: Boolean,
    default: false,
  },
  id: Number,
});

const isPopupOpen = ref(false);
const evaluation = ref({
  novelty: 1,
  feasibility: 1,
  impact: 1,
  scalability: 1,
  originality: 1,
  relevance: 1,
});
const feedback = ref("");

const openPopup = () => {
  isPopupOpen.value = true;
};

const closePopup = () => {
  isPopupOpen.value = false;
};

const submitEvaluation = async () => {
  try {
    await axios.post("/api/tutor/evaluate", {
      project_id: props.id,
      ...evaluation.value,
      feedback: feedback.value,
    });
    console.log("Evaluation submitted successfully.");
  } catch (error) {
    console.error("Failed to submit evaluation:", error);
  } finally {
    closePopup();
  }
};
</script>

<style scoped>
.open-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.input-group {
  margin-bottom: 10px;
}

.input-group label {
  display: block;
  font-weight: bold;
}

.input-group input,
.input-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.button-group {
  display: flex;
  justify-content: space-between;
}

.submit-button {
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.close-button {
  padding: 10px;
  background-color: #dc3545;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}
</style>
