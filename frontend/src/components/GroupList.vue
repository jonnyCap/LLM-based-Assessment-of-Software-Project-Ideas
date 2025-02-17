<template>
  <v-card class="pa-4" fluid>
    <v-list>
      <v-list-item v-for="group in groups" :key="group.name">
        <v-list-item-content>
          <v-list-item-title>{{ group.name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup>
defineProps(["groups"]);
</script>
