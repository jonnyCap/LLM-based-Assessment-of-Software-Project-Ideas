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

      <!-- Display selected assessment details with scrollable list -->
      <v-list v-if="filteredCriteria" class="scrollable-list">
        <v-list-item v-for="(value, key) in filteredCriteria" :key="key" dense>
          <v-list-item-content>
            <v-list-item-title class="small-text">
              {{ formatKey(key) }}: {{ value }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
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

  // Remove unwanted fields
  return Object.fromEntries(
    Object.entries(selected).filter(
      ([key]) => !["id", "project_id"].includes(key)
    )
  );
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
  margin-bottom: 8px;
}

.scrollable-list {
  max-height: 300px; /* Adjust max height */
  overflow-y: auto; /* Enable scrolling when content exceeds max height */
  border-top: 1px solid #ddd;
  padding-top: 4px;
}

.small-text {
  font-size: 14px; /* Reduce font size */
  line-height: 1; /* Adjust line height for less spacing */
}
</style>
