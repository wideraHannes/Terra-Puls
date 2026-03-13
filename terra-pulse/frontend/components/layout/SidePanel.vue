<template>
  <Transition name="slide">
    <div
      v-if="uiStore.sidePanelOpen && uiStore.selectedIso3"
      data-testid="side-panel"
      class="fixed right-0 top-0 h-full w-80 bg-gray-900 border-l border-gray-800 z-40 flex flex-col overflow-hidden"
      style="background-color: #111118"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-800">
        <div class="flex items-center gap-3">
          <img
            v-if="country?.flag_url"
            :src="country.flag_url"
            class="w-8 h-5 object-cover rounded"
            :alt="country.name"
          />
          <div>
            <div class="text-white font-semibold text-sm">
              {{ country?.name ?? uiStore.selectedIso3 }}
            </div>
            <div class="text-gray-500 text-xs font-mono">{{ country?.region }}</div>
          </div>
        </div>
        <button
          data-testid="panel-close"
          @click="uiStore.closePanel()"
          class="text-gray-500 hover:text-white transition-colors text-lg leading-none"
        >
          ×
        </button>
      </div>

      <!-- Pulse Gauge -->
      <div class="p-4 border-b border-gray-800 flex items-center justify-between">
        <PulseGauge :score="pulse?.composite_score ?? null" />
        <div class="text-right font-mono text-xs">
          <div class="text-gray-400">Trend</div>
          <div class="text-white text-lg">{{ trendIcon(pulse?.trend ?? '') }}</div>
          <div class="text-gray-500 capitalize">{{ pulse?.trend ?? "—" }}</div>
        </div>
      </div>

      <!-- Score breakdown -->
      <div v-if="pulse" class="p-4 border-b border-gray-800">
        <div class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
          Dimensions
        </div>
        <div class="space-y-2">
          <ScoreRow label="Sentiment" :value="pulse.sentiment_score" />
          <ScoreRow label="Conflict" :value="pulse.conflict_score" />
        </div>
      </div>

      <!-- News Feed -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
          Latest News
        </div>
        <NewsFeed :iso3="uiStore.selectedIso3" />
      </div>

      <!-- Footer stats -->
      <div
        v-if="country"
        class="p-4 border-t border-gray-800 text-xs font-mono text-gray-500 grid grid-cols-2 gap-2"
      >
        <div>
          <div class="text-gray-600">Population</div>
          <div class="text-gray-300">{{ formatPop(country.population) }}</div>
        </div>
        <div>
          <div class="text-gray-600">Capital</div>
          <div class="text-gray-300">{{ country.capital ?? "—" }}</div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { useUiStore } from "~/stores/ui"
import { usePulseStore } from "~/stores/pulse"
import { useCountriesStore } from "~/stores/countries"
import { useColorScale } from "~/composables/useColorScale"

const uiStore = useUiStore()
const pulseStore = usePulseStore()
const countriesStore = useCountriesStore()
const { trendIcon } = useColorScale()

const pulse = computed(() =>
  uiStore.selectedIso3 ? pulseStore.scores[uiStore.selectedIso3] : null
)
const country = computed(() =>
  uiStore.selectedIso3 ? countriesStore.byIso3[uiStore.selectedIso3] : null
)

const formatPop = (n: number) => {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`
  return n.toString()
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
