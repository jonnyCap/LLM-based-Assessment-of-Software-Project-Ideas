<template>
  <div class="container">
    <!-- Left Side -->
    <div class="left-side">
      <div class="idea-input">
        <IdeaInput @ideaSubmitted="handleIdea" />
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
      <div class="assessment-header">LLM-based Assessment</div>
      <div class="assessment-content">
        <AssessmentChart :criteria="criteria" class="chart-container" />
        <CriteriaEvaluation :criteria="criteria" class="criteria-container" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import IdeaInput from "./components/IdeaInput.vue";
import GroupList from "./components/GroupList.vue";
import AssessmentChart from "./components/AssessmentChart.vue";
import CriteriaEvaluation from "./components/CriteriaEvaluation.vue";
import axios from "axios";

const groups = ref([]);
const criteria = ref({
  novelty: 4,
  feasibility: 3,
  impact: 5,
  scalability: 2,
  originality: 4,
  relevance: 3,
});

onMounted(async () => {
  try {
    const response = await axios.get("/api/project-idea/get-ideas");
    groups.value = response.data;
    console.log("Fetched groups:", groups.value);
  } catch (error) {
    console.error("Failed to fetch groups:", error);
    groups.value = [];
  }
});

const handleIdea = async (idea) => {
  const ideas = [idea];
  try {
    await axios.post("/api/project-idea/add-ideas", { ideas }); // Pass data directly
  } catch (error) {
    console.error("Failed to add idea:", error);
  } finally {
    // Fetch the updated list of ideas
    const response = await axios.get("/api/project-idea/get-ideas");
    groups.value = response.data;
  }
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

const handleItemClick = async (groupId) => {
  try {
    await axios.post("/api/project-idea/load-evaluations", { id: groupId });
  } catch (error) {
    console.error("Failed to delete idea:", error);
  } finally {
    // Fetch the updated list of ideas
    const response = await axios.get("/api/project-idea/get-ideas");
    groups.value = response.data;
  }
};
</script>

<style scoped>
/* Container to split the screen */
.container {
  display: flex;
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
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  padding: 10px;
  border-bottom: 2px solid #ddd;
  margin-bottom: 20px;
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
  justify-content: center;
  align-items: center;
}

/* Criteria List takes the remaining space */
.criteria-container {
  flex: 1;
}
</style>
