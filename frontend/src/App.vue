<template>
  <div class="container">
    <!-- Left Side -->
    <div class="left-side">
      <div class="idea-input">
        <IdeaInput @ideaSubmitted="handleIdea" />
      </div>
      <div class="group-list">
        <GroupList :groups="groups" />
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
import { ref } from "vue";
import IdeaInput from "./components/IdeaInput.vue";
import GroupList from "./components/GroupList.vue";
import AssessmentChart from "./components/AssessmentChart.vue";
import CriteriaEvaluation from "./components/CriteriaEvaluation.vue";

const groups = ref([
  { name: "Group A1", ideas: [] },
  { name: "Group A2", ideas: [] },
]);

const criteria = ref({
  novelty: 4,
  feasibility: 3,
  impact: 5,
  scalability: 2,
  originality: 4,
  relevance: 3,
});

const handleIdea = (idea) => {
  groups.value[0].ideas.push(idea);
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
