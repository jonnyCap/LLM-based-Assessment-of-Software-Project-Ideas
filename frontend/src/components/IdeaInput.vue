<template>
  <v-card class="pa-4">
    <v-text-field
      v-model="idea"
      label="Input Idea..."
      outlined
      dense
    ></v-text-field>
    <v-btn color="primary" @click="submitIdea" class="mr-2">
      <v-icon>mdi-send</v-icon>
    </v-btn>
    <v-btn color="secondary" @click="openFile">
      <v-icon>mdi-upload</v-icon>
    </v-btn>
    <input
      type="file"
      ref="fileInput"
      accept=".csv"
      @change="handleFileUpload"
      style="display: none"
    />
  </v-card>
</template>

<script setup>
import { ref } from "vue";
import Papa from "papaparse";
import axios from "axios";

const idea = ref("");
const fileInput = ref(null);

const openFile = () => {
  fileInput.value.click(); // Trigger file input click
};

const emit = defineEmits(["updateGroups"]);

const submitIdea = async () => {
  const ideas = [idea.value];
  try {
    await axios.post("/api/project-idea/add-ideas", { ideas }); // Pass data directly
  } catch (error) {
    console.error("Failed to add idea:", error);
  } finally {
    // Fetch the updated list of ideas
    emit("updateGroups");
    idea.value = "";
  }
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  Papa.parse(file, {
    complete: async (result) => {
      // Extract second column and filter out empty values
      const ideas = result.data
        .slice(1) // Skip header row
        .map((row) => row[1]) // Second column
        .filter((idea) => idea); // Remove empty values

      if (ideas.length > 0) {
        try {
          await axios.post("/api/project-idea/add-ideas", { ideas });
        } catch (error) {
          console.error("Error adding ideas:", error);
        } finally {
          // Fetch the updated list of ideas
          emit("updateGroups");
        }
      }
    },
    skipEmptyLines: true, // Ignore empty lines
  });
};
</script>
