<template>
  <div class="container">
    <!-- Left Side -->
    <div class="left-side">
      <div class="idea-input">
        <IdeaInput @updateGroups="updateGroups" />
      </div>
      <div class="group-list">
        <GroupList
          :groups="groups"
          :handleItemClick="handleItemClick"
          :deleteProjectIdea="deleteProjectIdea"
        />
      </div>
    </div>

    <!-- Right Side -->
    <div class="right-side">
      <div class="assessment-header">
        <h3>LLM-based Assessment</h3>
      </div>

      <template v-if="selectedGroup">
        <div class="assessment-content">
          <div class="chart-container">
            <div>
              <h5>Tutor Evaluations</h5>
            </div>
            <div>
              <h5>LLM Evaluations</h5>
            </div>
          </div>
          <template
            v-if="
              tutor_evaluations.length === 0 && llm_evaluations.length === 0
            "
          >
            <div class="no-data-placeholder">No data available yet.</div>
          </template>
          <template v-else>
            <div class="chart-container">
              <AssessmentChart
                :criteria="tutor_evaluations"
                class="chart-container"
              />
              <AssessmentChart
                :criteria="filtered_llm_evaluations"
                class="chart-container"
              />
            </div>
          </template>

          <div class="popup-container">
            <div class="inner_button_container">
              <EvaluationPopUp
                :disabled="!selectedGroup || selectedGroup === undefined"
                :title="'LLM Evaluation'"
                :description="
                  'Group Description: ' + selectedGroup?.description
                "
                :id="selectedGroup?.id"
                @evaluationSuccess="() => handleItemClick(selectedGroup)"
              />
            </div>
            <div class="inner_button_container">
              <LLMEvaluationButton
                :id="selectedGroup?.id"
                :disabled="!selectedGroup || selectedGroup === undefined"
                @evaluationSuccess="() => handleItemClick(selectedGroup)"
              />
              <ModelFilterButton
                :models="availableModels"
                :selectedModels="selectedModels"
                @selectModels="selectModels"
              />
            </div>
          </div>
          <div class="chart-container">
            <CriteriaEvaluation
              :criteria="tutor_evaluations"
              class="criteria-container"
            />

            <CriteriaEvaluation
              :criteria="filtered_llm_evaluations"
              class="criteria-container"
            />
          </div>
        </div>
      </template>
      <template v-else>
        <div class="no-data-placeholder">No group selected.</div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import IdeaInput from "./components/IdeaInput.vue";
import GroupList from "./components/GroupList.vue";
import AssessmentChart from "./components/AssessmentChart.vue";
import CriteriaEvaluation from "./components/CriteriaEvaluation.vue";
import EvaluationPopUp from "./components/EvaluationPopUp.vue";
import axios from "axios";
import LLMEvaluationButton from "./components/LLMEvaluationButton.vue";
import ModelFilterButton from "./components/ModelFilterButton.vue";

const groups = ref([]);
const tutor_evaluations = ref([]);
const llm_evaluations = ref([]);

const selectedGroup = ref(null);
const availableModels = ref([]);
const selectedModels = ref([]);

onMounted(async () => {
  try {
    // Fetch Groups
    await updateGroups();
    console.log("Fetched groups:", groups.value);

    // Fetch LLM Models
    const response = await axios.get("/api/llm/models");
    console.log("Fetched models:", response.data);
    availableModels.value = response.data;
    selectedModels.value = response.data;
  } catch (error) {
    console.error("Failed to fetch groups:", error);
    groups.value = [];
  }
});

const filtered_llm_evaluations = computed(() => {
  return llm_evaluations.value.filter((evaluation) => {
    return selectedModels.value.includes(evaluation.model);
  });
});

const updateGroups = async () => {
  return axios.get("/api/project-idea/get-ideas").then((response) => {
    groups.value = response.data;
  });
};

const selectModels = (models) => {
  console.log("Selected models:", models);
  selectedModels.value = models;
};

const deleteProjectIdea = async (id) => {
  try {
    await axios.delete("/api/project-idea/delete-idea", { data: { id } });
    groups.value = groups.value.filter((group) => group.id !== id); // Update UI
  } catch (error) {
    console.error("Failed to delete idea:", error);
  } finally {
    // Fetch the updated list of ideas
    const response = await axios.get("/api/project-idea/get-ideas");
    groups.value = response.data;
  }
};

const handleItemClick = async (group) => {
  try {
    if (!group) {
      console.error("Invalid group has been passed!");
      return;
    }

    // Set selected id
    selectedGroup.value = group;
    console.log("Selected group:", selectedGroup.value);
    const id = selectedGroup.value.id;

    // Fetch evaluations for the selected project idea
    const response = await axios.get(`/api/project-idea/load-evaluations`, {
      params: { id },
    });

    // Store the evaluations in the refs
    tutor_evaluations.value = response.data.tutor_evaluations || [];
    llm_evaluations.value = response.data.llm_evaluations || [];

    console.log("Evaluation data stored:", {
      tutor_evaluations: tutor_evaluations.value,
      llm_evaluations: llm_evaluations.value,
    });
  } catch (error) {
    console.error("Failed to load evaluations:", error);
  }
};
</script>

<style scoped>
/* Container to split the screen */
.container {
  display: flex;
  max-height: 100vh;
  height: 100vh;
}

/* Left Side (Idea Input + Group List) */
.left-side {
  width: 30%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  border-right: 2px solid #ddd; /* Divider */
}

/* Idea Input at the top */
.idea-input {
  margin-bottom: 20px;
}

/* Group List takes remaining space */
.group-list {
  flex-grow: 1;
  overflow-y: auto;
}

/* Right Side (Assessment) */
.right-side {
  width: 70%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

/* Title Section */
.assessment-header {
  font-size: 1.4rem;
  font-weight: bold;
  text-align: center;
  border-bottom: 2px solid #ddd;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

/* Chart and Criteria Section */
.assessment-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* Chart takes half the right side */
.chart-container {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.popup-container {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 20px;
}

/* Criteria List takes the remaining space */
.criteria-container {
  flex: 1;
}

.no-data-placeholder {
  width: 100%;
  height: 350px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.evaluation-button-container {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}

.inner_button_container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
</style>
