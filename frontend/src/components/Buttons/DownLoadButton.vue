<template>
  <BasicButton @click="downloadCSV">Download CSV</BasicButton>
</template>

<script setup>
import { defineProps } from "vue";
import BasicButton from "./BasicButton.vue";

const props = defineProps({
  jsonData: {
    type: Object,
    required: true,
  },
});

function downloadCSV() {
  const data = props.jsonData;

  const headers = [
    "ID",
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

  const values = [
    data.project_id, // renamed to "ID"" in CSV
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
  ].map((val) => JSON.stringify(val ?? ""));

  const csvContent = headers.join(",") + "\n" + values.join(",");

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
