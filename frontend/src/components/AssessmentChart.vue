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
  criteria: Object,
});

// Compute chart data dynamically from `criteria` prop
const chartData = computed(() => ({
  labels: [
    "Novelty",
    "Feasibility",
    "Impact",
    "Scalability",
    "Originality",
    "Relevance",
  ],
  datasets: [
    {
      label: "Assessment",
      data: Object.values(props.criteria),
      borderColor: "rgba(54, 162, 235, 1)",
      backgroundColor: "rgba(54, 162, 235, 0.2)",
      pointBackgroundColor: "rgba(54, 162, 235, 1)",
      pointBorderColor: "#fff",
      pointHoverBackgroundColor: "#fff",
      pointHoverBorderColor: "rgba(54, 162, 235, 1)",
    },
  ],
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
