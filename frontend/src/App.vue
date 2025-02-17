<template>
  <v-container>
    <v-row>
      <!-- Input Idea Section -->
      <v-col cols="12">
        <IdeaInput @ideaSubmitted="handleIdea" />
      </v-col>
    </v-row>

    <v-row>
      <!-- Group List -->
      <v-col cols="4">
        <GroupList :groups="groups" />
      </v-col>

      <!-- LLM-Based Assessment Section -->
      <v-col cols="8">
        <v-card class="pa-4">
          <v-card-title class="text-center">LLM-based Assessment</v-card-title>
          <v-row>
            <v-col cols="6" class="d-flex justify-center">
              <AssessmentChart :criteria="criteria" />
            </v-col>
            <v-col cols="6">
              <CriteriaEvaluation :criteria="criteria" />
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from "vue";
import IdeaInput from "./components/IdeaInput.vue";
import GroupList from "./components/GroupList.vue";
import AssessmentChart from "./components/AssessmentChart.vue";
import CriteriaEvaluation from "./components/CriteriaEvaluation.vue";

const groups = ref<{ name: string; ideas: string[] }[]>([
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

const handleIdea = (idea: string) => {
  groups.value[0].ideas.push(idea);
};
</script>

<style scoped></style>
