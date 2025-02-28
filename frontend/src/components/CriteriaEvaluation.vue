<template>
  <!-- Handle empty criteria list -->
  <div v-if="!criteria.length" class="no-data">
    No assessment data available.
  </div>

  <template v-else>
    <v-card class="pa-4">
      <!-- Dropdown to select an entry -->
      <v-select
        v-model="selectedEntry"
        :items="
          criteria.map((item, index) => ({
            title: `Assessment ${index + 1}`,
            value: index,
          }))
        "
        label="Select Assessment"
        outlined
        dense
        class="dropdown"
      ></v-select>

      <!-- Grid Layout for criteria -->
      <div class="criteria-grid">
        <!-- First three rows: Two columns each -->
        <template v-for="(pair, index) in gridRows" :key="index">
          <div v-if="index < 3" class="row">
            <div v-for="(value, key) in pair" :key="key" class="column">
              <strong>{{ formatKey(key) }}:</strong> {{ value }}
            </div>
          </div>
        </template>

        <!-- Last row: Feedback (single column, full width) -->
        <div v-if="filteredCriteria.feedback" class="feedback-row">
          <strong>Feedback:</strong>
          <p class="feedback-text">{{ filteredCriteria.feedback }}</p>
        </div>
      </div>
    </v-card>
  </template>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  criteria: Array, // Expect an array of assessments
});

// Selected entry index (default to the first entry)
const selectedEntry = ref(0);

// Compute the currently selected entry, filtering out unnecessary fields
const filteredCriteria = computed(() => {
  if (!props.criteria.length) return null;

  const selected = props.criteria[selectedEntry.value];

  // Remove unwanted fields (except feedback)
  return Object.fromEntries(
    Object.entries(selected).filter(
      ([key]) => !["id", "project_id"].includes(key)
    )
  );
});

// Convert object to an array of key-value pairs, excluding feedback
const gridRows = computed(() => {
  if (!filteredCriteria.value) return [];

  const criteriaEntries = Object.entries(filteredCriteria.value).filter(
    ([key]) => key !== "feedback"
  );

  // Group into pairs (two columns per row)
  const rows = [];
  for (let i = 0; i < criteriaEntries.length; i += 2) {
    rows.push(Object.fromEntries(criteriaEntries.slice(i, i + 2)));
  }
  return rows;
});

// Format key names (capitalize first letter and replace underscores with spaces)
const formatKey = (key) =>
  key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
</script>

<style scoped>
.no-data {
  text-align: center;
  font-size: 14px;
  color: gray;
  padding: 16px;
}

.dropdown {
  margin-bottom: 12px;
}

.criteria-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Each row in the grid */
.row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

/* Each column inside a row */
.column {
  flex: 1;
  font-size: 14px;
  background-color: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
}

/* Feedback row with full width */
.feedback-row {
  display: flex;
  flex-direction: column;
  background-color: #e9ecef;
  padding: 12px;
  border-radius: 4px;
}

.feedback-text {
  font-size: 14px;
  white-space: pre-wrap; /* Ensures text wraps properly */
  word-break: break-word;
  margin-top: 4px;
  min-height: 100px;
  height: 100px;
  max-height: 100px;
  overflow-y: auto;
}
</style>
