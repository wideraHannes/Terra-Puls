<template>
  <div class="flex items-center gap-2">
    <div class="text-gray-400 w-20 text-[11px] shrink-0">{{ label }}</div>
    <div class="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-700"
        :style="{ width: `${(value ?? 0) * 100}%`, backgroundColor: color }"
      />
    </div>
    <div class="text-gray-400 text-[11px] w-6 text-right">{{ display }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { interpolateRdYlGn } from "d3-scale-chromatic"

const props = defineProps<{ label: string; value: number | null }>()
const color = computed(() => interpolateRdYlGn(props.value ?? 0.5))
const display = computed(() =>
  props.value !== null ? Math.round((props.value ?? 0) * 100).toString() : "—"
)
</script>
