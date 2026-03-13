<template>
  <div class="absolute top-4 left-4 z-10 flex flex-col gap-2">
    <!-- Layer toggles -->
    <div
      class="bg-gray-900 bg-opacity-90 border border-gray-700 rounded-lg p-3 text-xs font-mono"
    >
      <div class="text-gray-400 mb-2 uppercase tracking-wider text-[10px]">Layers</div>
      <button
        v-for="layer in layers"
        :key="layer.id"
        @click="uiStore.setLayer(layer.id as any)"
        class="block w-full text-left px-2 py-1 rounded transition-colors mb-1"
        :class="
          uiStore.activeLayer === layer.id
            ? 'bg-blue-600 text-white'
            : 'text-gray-400 hover:text-white hover:bg-gray-700'
        "
      >
        {{ layer.label }}
      </button>
    </div>

    <!-- Last updated -->
    <div v-if="pulseStore.lastUpdated" class="text-[10px] text-gray-500 font-mono px-1">
      Updated {{ timeAgo }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { usePulseStore } from "~/stores/pulse"
import { useUiStore } from "~/stores/ui"

const pulseStore = usePulseStore()
const uiStore = useUiStore()

const layers = [
  { id: "pulse", label: "Pulse Score" },
  { id: "sentiment", label: "Sentiment" },
  { id: "conflict", label: "Conflict" },
]

const timeAgo = computed(() => {
  if (!pulseStore.lastUpdated) return ""
  const secs = Math.floor((Date.now() - pulseStore.lastUpdated.getTime()) / 1000)
  if (secs < 60) return `${secs}s ago`
  return `${Math.floor(secs / 60)}m ago`
})
</script>
