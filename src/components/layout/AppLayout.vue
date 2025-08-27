<template>
  <div class="app-layout">
    <main class="main-content">
      <slot><RouterView /></slot> <!-- Сюда вставляется RouterView -->
    </main>
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">

</script>