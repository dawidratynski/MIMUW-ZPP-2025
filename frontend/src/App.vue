<script setup>
import Navbar from './components/Navbar.vue'
</script>

<template>
  <main>
    <Navbar />
    <RouterView />
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
</style>