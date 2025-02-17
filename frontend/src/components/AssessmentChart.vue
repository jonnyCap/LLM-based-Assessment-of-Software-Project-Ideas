<template>
  <v-card class="pa-4">
    <RadarChart :data="chartData" />
  </v-card>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Radar } from "vue-chartjs";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
} from "chart.js";

ChartJS.register(RadialLinearScale, PointElement, LineElement);

const props = defineProps(["criteria"]);

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
      borderColor: "blue",
      backgroundColor: "rgba(0, 0, 255, 0.2)",
    },
  ],
}));
</script>
