<template>
  <div class="flex flex-col items-center">
    <div class="relative w-32 h-16 overflow-hidden">
      <!-- Semicircle gauge -->
      <svg viewBox="0 0 100 50" class="w-full">
        <!-- Background arc -->
        <path
          d="M5,50 A45,45 0 0,1 95,50"
          fill="none"
          stroke="#1e1e2e"
          stroke-width="8"
          stroke-linecap="round"
        />
        <!-- Score arc -->
        <path
          d="M5,50 A45,45 0 0,1 95,50"
          fill="none"
          :stroke="color"
          stroke-width="8"
          stroke-linecap="round"
          :stroke-dasharray="`${dashArray} 141.4`"
          stroke-dashoffset="0"
          style="transition: stroke-dasharray 1s ease"
        />
        <!-- Center text -->
        <text
          x="50"
          y="45"
          text-anchor="middle"
          fill="white"
          font-size="14"
          font-family="monospace"
          font-weight="bold"
        >
          {{ displayScore }}
        </text>
      </svg>
    </div>
    <div class="text-xs font-mono mt-1" :style="{ color }">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { useColorScale } from "~/composables/useColorScale"

const props = defineProps<{ score: number | null }>()
const { scoreToColor, scoreToLabel } = useColorScale()

const color = computed(() => scoreToColor(props.score))
const label = computed(() => scoreToLabel(props.score))
const displayScore = computed(() =>
  props.score !== null ? Math.round((props.score ?? 0) * 100).toString() : "—"
)
// 141.4 is the approx arc length of the semicircle
const dashArray = computed(() => ((props.score ?? 0) * 141.4).toFixed(1))
</script>
