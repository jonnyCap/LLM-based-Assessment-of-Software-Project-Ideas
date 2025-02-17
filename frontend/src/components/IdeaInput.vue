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
    <v-btn color="secondary">
      <v-icon>mdi-upload</v-icon>
    </v-btn>
  </v-card>
</template>

<script setup>
import { ref } from "vue";

const idea = ref("");

const emit = defineEmits(["ideaSubmitted"]);

const submitIdea = () => {
  if (idea.value.trim()) {
    emit("ideaSubmitted", idea.value);
    idea.value = "";
  }
};
</script>
