<template>
  <v-card class="pa-4">
    <v-list v-if="groups.length">
      <v-list-item
        v-for="group in groups"
        :key="group.id"
        @click="handleItemClick(group)"
        :class="{
          'selected-item': selectedGroup && group.id === selectedGroup.id,
        }"
        class="list-item"
      >
        <v-list-item-content>
          <v-list-item-title class="text-truncate">
            {{ group.description }}
          </v-list-item-title>
        </v-list-item-content>

        <!-- Info Button with Tooltip -->
        <v-tooltip bottom>
          <template v-slot:activator="{ props }">
            <v-btn icon v-bind="props">
              <v-icon>mdi-information-outline</v-icon>
            </v-btn>
          </template>
          <span>{{ group.description }}</span>
        </v-tooltip>

        <!-- Delete Button -->
        <v-btn icon @click.stop="deleteProjectIdea(group.id)">
          <v-icon color="red">mdi-delete</v-icon>
        </v-btn>
      </v-list-item>
    </v-list>

    <v-alert v-else type="info" class="text-center">
      No project ideas available.
    </v-alert>
  </v-card>
</template>

<style scoped>
.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white; /* Default background */
  padding: 4px;
  border-radius: 8px;
  border-bottom: 2px solid #f5f5f5; /* Light grey border */
  transition: background 0.3s;
  max-width: 500px; /* Adjust max width */
  cursor: pointer;
}

.list-item:hover {
  background-color: #f5f5f5; /* Light grey hover effect */
}

.selected-item {
  background-color: #e0e0e0 !important; /* Gray background for selected group */
}

.text-truncate {
  max-width: 300px; /* Prevents long text from breaking layout */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<script setup>
defineProps([
  "groups",
  "handleItemClick",
  "deleteProjectIdea",
  "selectedGroup",
]);
</script>
