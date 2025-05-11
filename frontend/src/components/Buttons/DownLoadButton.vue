<template>
  <button @click="downloadCSV">Download CSV</button>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  jsonData: {
    type: Object,
    required: true,
  },
});

function downloadCSV() {
  const data = props.jsonData;
  const keys = Object.keys(data);
  const values = keys.map((key) => JSON.stringify(data[key]));

  const csvContent = keys.join(",") + "\n" + values.join(",");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", "data.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
</script>
