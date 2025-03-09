<template>
  <div class="chart-container">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from "vue";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "vue-chartjs";

// Register required Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const props = defineProps({
  criteria: Array, // Expect an array of objects instead of a single object
});

// Define a set of colors to be used for different datasets
const colors = [
  "rgba(54, 162, 235, 1)",
  "rgba(255, 99, 132, 1)",
  "rgba(255, 206, 86, 1)",
  "rgba(75, 192, 192, 1)",
  "rgba(153, 102, 255, 1)",
  "rgba(255, 159, 64, 1)",
];

// Compute chart data dynamically for multiple datasets
const chartData = computed(() => ({
  labels: [
    "Novelty",
    "Usefulness",
    "Market Potential",
    "Applicability",
    "Complexity",
    "Completeness",
  ],
  datasets: props.criteria.map((criteriaSet, index) => {
    const color = colors[index % colors.length]; // Cycle through colors

    // Filter out non-numeric fields
    const filteredData = Object.keys(criteriaSet)
      .filter(
        (key) =>
          ![
            "project_id",
            "id",
            "feedback",
            "model",
            "username",
            "num_evaluations",
          ].includes(key)
      ) // Remove unwanted fields
      .map((key) => criteriaSet[key]); // Extract values

    return {
      label: `Assessment ${index + 1}`, // Label each dataset
      data: filteredData,
      borderColor: color,
      backgroundColor: color.replace("1)", "0.2)"), // Adjust transparency
      pointBackgroundColor: color,
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: color,
    };
  }),
}));

// Chart options for styling
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      beginAtZero: true,
      suggestedMin: 0,
      suggestedMax: 5, // Adjust the max value based on your scale
      grid: {
        color: "rgba(200, 200, 200, 0.3)",
      },
      pointLabels: {
        font: {
          size: 14,
        },
      },
    },
  },
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 350px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
