<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

router.push('/')
</script>

<template>
  <router-view />
</template>