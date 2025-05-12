<template>
  <BasicButton @click="downloadCSV">Download CSV</BasicButton>
</template>

<script setup>
import { defineProps } from "vue";
import BasicButton from "./BasicButton.vue";
import axios from "axios";

const props = defineProps({
  jsonData: {
    type: [Object, Array],
    required: true,
  },
});

async function fetchProjectDescription(projectId) {
  try {
    const response = await axios.get(`/api/project-idea/get-idea/${projectId}`);
    return response.data.description;
  } catch (error) {
    console.error(
      `Failed to fetch description for project ${projectId}:`,
      error
    );
    return ""; // Fallback or throw if preferred
  }
}

async function downloadCSV() {
  const dataArray = Array.isArray(props.jsonData)
    ? props.jsonData.slice(0, 5)
    : [props.jsonData];

  const projectId = dataArray[0]?.project_id;
  const description = await fetchProjectDescription(projectId); // Fetch once

  const headers = [
    "ID",
    "Model",
    "Project Description",
    "Novelty (Score)",
    "Novelty (Rationale)",
    "Usefulness (Score)",
    "Usefulness (Rationale)",
    "Market Potential (Score)",
    "Market Potential (Rationale)",
    "Applicability (Score)",
    "Applicability (Rationale)",
    "Complexity (Score)",
    "Complexity (Rationale)",
    "Completeness (Score)",
    "Completeness (Rationale)",
    "General Feedback",
  ];

  const rows = dataArray.map((data) => {
    const values = [
      data.project_id,
      data.model,
      description, // same for all rows
      data.novelty,
      data.novelty_justification,
      data.usefulness,
      data.usefulness_justification,
      data.market_potential,
      data.market_potential_justification,
      data.applicability,
      data.applicability_justification,
      data.complexity,
      data.complexity_justification,
      data.completeness,
      data.completeness_justification,
      data.feedback,
    ];

    return values.map((val) => JSON.stringify(val ?? "")).join(",");
  });

  const csvContent = headers.join(",") + "\n" + rows.join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "evaluation.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>
