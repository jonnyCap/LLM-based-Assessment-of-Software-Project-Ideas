<template>
  <div>
    <BasicButton @click="openPopup" :disabled="disabled"
      >Summarize Evaluations</BasicButton
    >
    <div v-if="isPopupOpen" class="popup-overlay">
      <div class="popup">
        <button class="close-icon" @click="closePopup">✖</button>

        <h2>Summerized Evaluation</h2>
        <!--YOU SHOULD PASS HERE NAMES FOR THE LABELS OTHERWISE IT WILL JUST BE ASSIGNMENT 1 AND ASSIGNMENT 2-->
        <template v-if="!options_chosen">
          <div>
            <h6>Choose the options for summarization</h6>
            <p class="text">
              By enabling the advanced evaluation, instead of simply calculating
              the means of each category, a LLM will receive all the given
              feedback and use them to reevaluate the project idea.
            </p>

            <v-checkbox
              v-model="advanced_llm_summary_enabled"
              label="LLM Advanced Summary"
              density="compact"
            ></v-checkbox>

            <v-checkbox
              v-model="advanced_tutor_summary_enabled"
              label="Tutor Advanced Summary"
              density="compact"
            ></v-checkbox>

            <select v-model="selectedModel" class="model-dropdown">
              <option v-for="model in models" :key="model" :value="model">
                {{ model }}
              </option>
            </select>

            <BasicButton @click="summerizeEvaluations" class="button"
              >Summarize</BasicButton
            >
          </div>
        </template>
        <template v-else-if="loading">
          <span class="loader"></span>
        </template>
        <template v-else-if="error">
          <div>
            <span>{{ error }}</span>
          </div>
        </template>
        <template v-else>
          <AssessmentChart
            :criteria="[summerized_llm_evaluation, summerized_tutor_evaluation]"
            :labels="labels"
          />
          <CriteriaEvaluation
            :criteria="[summerized_llm_evaluation, summerized_tutor_evaluation]"
            :labels="labels"
          />
        </template>
        <div class="button-container">
          <BasicButton
            v-show="options_chosen"
            class="button reanalyze-button"
            @click="enable_reevaluation"
            :disabled="loading"
            >Reanalyze</BasicButton
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, watch, computed } from "vue";
import BasicButton from "./Buttons/BasicButton.vue";
import AssessmentChart from "./AssessmentChart.vue";
import CriteriaEvaluation from "./CriteriaEvaluation.vue";
import axios from "axios";

const props = defineProps({
  id: Number,
  disabled: {
    type: Boolean,
    default: false,
  },
  models: {
    type: Array,
    default: () => [],
  },
});

const isPopupOpen = ref(false);
const loading = ref(false);
const error = ref(null);

const advanced_llm_summary_enabled = ref(false);
const advanced_tutor_summary_enabled = ref(false);
const options_chosen = ref(false);

const summerized_tutor_evaluation = ref({});
const num_tutor_evaluations = ref(0);
const summerized_llm_evaluation = ref({});
const num_llm_evaluations = ref(0);

const labels = computed(() => {
  return [
    `LLM summary (${num_llm_evaluations.value} evals.)`,
    `Tutor summary (${num_tutor_evaluations.value} evals.)`,
  ];
});

const selectedModel = ref(null);

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

// For cancelling requests
let cancelTokenSource = null;

const openPopup = () => {
  isPopupOpen.value = true;
};

const closePopup = () => {
  isPopupOpen.value = false;

  // Cancel the ongoing Axios request if exists
  if (cancelTokenSource) {
    cancelTokenSource.cancel("Request canceled due to popup close.");
  }

  // enable reevaluation
  options_chosen.value = false;
};

const enable_reevaluation = () => {
  options_chosen.value = false;
};

const summerizeEvaluations = async () => {
  try {
    options_chosen.value = true;
    loading.value = true;

    // For canceling
    cancelTokenSource = axios.CancelToken.source();

    const response = await axios.post(
      "/api/project-idea/summarize",
      {
        id: parseInt(props.id, 10),
        llm_advanced_summary_enabled: advanced_llm_summary_enabled.value,
        tutor_advanced_summary_enabled: advanced_tutor_summary_enabled.value,
        model: selectedModel.value,
      },
      { cancelToken: cancelTokenSource.token }
    );

    if (response.status === 200) {
      console.log("Got result: ", response.data);
      error.value = false;

      summerized_llm_evaluation.value = response.data.llm_summary;
      summerized_tutor_evaluation.value = response.data.tutor_summary;

      num_llm_evaluations.value = response.data.llm_summary.num_evaluations;
      num_tutor_evaluations.value = response.data.tutor_summary.num_evaluations;
      console.log("Evaluation submitted successfully.");
    } else {
      console.error("Failed to submit evaluation:", response.data);
    }
  } catch (err) {
    if (axios.isCancel(err)) {
      console.log("Request was canceled:", err.message);
    } else {
      console.error("Failed to submit evaluation:", err);
      error.value =
        "An error occured while summarizing your evaluations: " +
        err.response?.data?.detail;
    }
  } finally {
    loading.value = false;
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
  max-height: 500px;
  overflow: auto;
  width: 700px;
  height: 800px;
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
