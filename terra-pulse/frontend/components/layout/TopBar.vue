<template>
  <header
    class="fixed top-0 left-0 right-0 z-30 flex items-center justify-between px-6 py-3 border-b border-gray-800"
    style="background-color: rgba(10, 10, 15, 0.9); backdrop-filter: blur(10px)"
  >
    <div class="flex items-center gap-3">
      <div class="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
      <span class="font-mono font-bold text-white tracking-tight">TERRA PULSE</span>
      <span class="text-gray-500 font-mono text-xs hidden sm:block"
        >// the world's heartbeat, visualized</span
      >
    </div>

    <div class="flex items-center gap-4 text-xs font-mono">
      <span v-if="pulseStore.loading" class="text-yellow-400 animate-pulse">FETCHING</span>
      <span v-else-if="pulseStore.error" class="text-red-400">ERROR</span>
      <span v-else class="text-green-400">LIVE</span>

      <span class="text-gray-600">{{ Object.keys(pulseStore.scores).length }} countries</span>
    </div>
  </header>
</template>

<script setup lang="ts">
import { usePulseStore } from "~/stores/pulse"
const pulseStore = usePulseStore()
</script>
