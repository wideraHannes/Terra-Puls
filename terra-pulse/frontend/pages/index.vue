<template>
  <div class="relative w-screen h-screen overflow-hidden" style="background-color: #0a0a0f">
    <TopBar />

    <!-- Globe fills the entire screen -->
    <div style="position: absolute; inset: 0; padding-top: 48px;">
      <TerraGlobe />
    </div>

    <!-- Controls overlay -->
    <GlobeControls class="pt-12" />

    <!-- Side panel -->
    <SidePanel />

    <!-- Legend -->
    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10">
      <div
        class="flex items-center gap-3 bg-gray-900 bg-opacity-80 border border-gray-800 rounded-full px-4 py-2"
      >
        <div class="flex items-center gap-1">
          <div data-testid="legend-crisis-dot" class="w-3 h-3 rounded-full" style="background: #d73027" />
          <span class="text-xs font-mono text-gray-400">Crisis</span>
        </div>
        <div
          data-testid="legend-gradient"
          class="w-16 h-1 rounded-full"
          style="background: linear-gradient(to right, #d73027, #ffffbf, #1a9850)"
        />
        <div class="flex items-center gap-1">
          <div data-testid="legend-stable-dot" class="w-3 h-3 rounded-full" style="background: #1a9850" />
          <span class="text-xs font-mono text-gray-400">Stable</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue"
import { usePulse } from "~/composables/usePulse"
import { useCountriesStore } from "~/stores/countries"
import { useUiStore } from "~/stores/ui"

const { start } = usePulse()
const countriesStore = useCountriesStore()
const uiStore = useUiStore()
const route = useRoute()

onMounted(async () => {
  await countriesStore.fetchAll()
  await start()

  // URL-based country selection (?country=DEU) — shareable links + test hook
  const iso3 = route.query.country as string | undefined
  if (iso3) uiStore.selectCountry(iso3.toUpperCase())

  // Expose stores on window for e2e tests
  if (import.meta.dev) {
    ;(window as any).__terraUiStore = uiStore
  }
})
</script>
