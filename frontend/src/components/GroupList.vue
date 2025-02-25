<template>
  <v-card class="pa-4" fluid>
    <v-list>
      <v-list-item
        v-for="group in groups"
        :key="group.id"
        @click="handleItemClick(group)"
        class="d-flex justify-space-between align-center"
      >
        <v-list-item-content>
          <v-list-item-title>{{ group.description }}</v-list-item-title>
        </v-list-item-content>

        <v-btn icon @click.stop="deleteProjectIdea(group.id)">
          <v-icon color="red">mdi-delete</v-icon>
        </v-btn>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup>
defineProps(["groups", "handleItemClick", "deleteProjectIdea"]);
</script>
