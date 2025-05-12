<template>
  <div>
    <BasicButton
      style="min-width: 100px"
      @click="handleQuickEval"
      :disabled="disabled || loading"
    >
      <span v-if="loading" class="loader"></span>
      <template v-else>Quick Eval.</template></BasicButton
    >
    <div v-if="isPopupOpen" class="popup-overlay">
      <div class="popup">
        <button class="close-icon" @click="closePopup">✖</button>

        <h2>Summarized Evaluation</h2>
        <template v-if="loading">
          <span class="loader"></span>
        </template>
        <template v-else-if="error">
          <div>
            <span>{{ error }}</span>
          </div>
        </template>
        <template v-else>
          <DownloadButton :jsonData="[...pre_evaluations, quick_eval]" />
          <AssessmentChart :criteria="[quick_eval, ...pre_evaluations]" />
          <CriteriaEvaluation :criteria="[quick_eval, ...pre_evaluations]" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, watch, computed } from "vue";
import BasicButton from "./Buttons/BasicButton.vue";
import AssessmentChart from "./AssessmentChart.vue";
import CriteriaEvaluation from "./CriteriaEvaluation.vue";
import DownloadButton from "./Buttons/DownLoadButton.vue";
import axios from "axios";

const props = defineProps({
  id: Number,
  disabled: {
    type: Boolean,
    default: false,
  },
});

const isPopupOpen = ref(false);
const loading = ref(false);
const error = ref(null);

const quick_eval = ref({});
const pre_evaluations = ref([]);

const emit = defineEmits(["evaluationSuccess"]);

const handleQuickEval = async (quickEval) => {
  try {
    loading.value = true;

    const response = await axios.post("/api/icl2025/quick_eval", {
      id: parseInt(props.id, 10),
    });

    if (response.status === 200) {
      console.log("Got result: ", response.data);
      error.value = null;
      quick_eval.value = response.data.quick_eval;
      pre_evaluations.value = response.data.evaluations;

      // Update llm evalutions
      emit("evaluationSuccess");
    } else {
      console.error("Failed to submit evaluation:", response.data);
      error.value =
        "An error occurred while summarizing your evaluations: " +
        response.data.detail;
    }
  } catch (err) {
    console.error("Error handling quick evaluation:", err);
    error.value =
      "An error occurred while summarizing your evaluations: " +
      err.response?.data?.detail;
  } finally {
    loading.value = false;
    openPopup();
  }
};

const openPopup = () => {
  console.log("Opening popup");
  isPopupOpen.value = true;
};

const closePopup = () => {
  console.log("Closing popup");
  isPopupOpen.value = false;
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
  max-height: 500px;
  overflow: auto;
  width: 700px;
  height: 800px;
}

.model-dropdown {
  padding: 7px;
  border-radius: 5px;
  border: 1px solid #ccc;
  font-size: 1rem !important;
}

.button {
  margin: 0 30px;
}

.reanalyze-button {
  background-color: green;
}
.close-button {
  background-color: #dc3545;
}

.loader {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: block;
  margin: 15px auto;
  position: relative;
  box-sizing: border-box;
  animation: animloader 1s linear infinite alternate;
  z-index: 2000;
  color: gray;
}

@keyframes animloader {
  0% {
    box-shadow: -38px -12px, -14px 0, 14px 0, 38px 0;
  }
  33% {
    box-shadow: -38px 0px, -14px -12px, 14px 0, 38px 0;
  }
  66% {
    box-shadow: -38px 0px, -14px 0, 14px -12px, 38px 0;
  }
  100% {
    box-shadow: -38px 0, -14px 0, 14px 0, 38px -12px;
  }
}

.button-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.close-icon {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #333;
}

.close-icon:hover {
  color: red;
}

.popup {
  position: relative; /* Ensure the close button is positioned within the popup */
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  max-height: 500px;
  overflow: auto;
  width: 700px;
  height: 800px;
}

.text {
  font-size: 14px;
  margin-bottom: 20px;
  font-weight: 100;
}
</style>
