<template>
  <v-card class="pa-4">
    <v-list>
      <v-list-item v-for="(value, key) in criteria" :key="key">
        <v-list-item-content>
          <v-list-item-title
            >{{ formatKey(key) }}: {{ value }}</v-list-item-title
          >
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup>
defineProps(["criteria"]);

const formatKey = (key) => key.charAt(0).toUpperCase() + key.slice(1);
</script>
