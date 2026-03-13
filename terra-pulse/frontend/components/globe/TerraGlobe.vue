<template>
  <div ref="globeContainer" style="width: 100%; height: 100%; display: block;" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue"
import { usePulseStore } from "~/stores/pulse"
import { useUiStore } from "~/stores/ui"
import { useColorScale } from "~/composables/useColorScale"

const globeContainer = ref<HTMLDivElement | null>(null)
const pulseStore = usePulseStore()
const uiStore = useUiStore()
const { scoreToColor } = useColorScale()

let globe: any = null

async function loadGeoJson() {
  const res = await fetch("/ne_110m_countries.json")
  return res.json()
}

function getCountryColor(feature: any) {
  const iso3 = feature.properties?.ADM0_A3 || feature.properties?.ISO_A3
  const score = pulseStore.scores[iso3]
  return scoreToColor(score?.composite_score)
}

onMounted(async () => {
  await nextTick()
  if (!globeContainer.value) return

  const w = globeContainer.value.clientWidth || window.innerWidth
  const h = globeContainer.value.clientHeight || window.innerHeight

  const Globe = (await import("globe.gl")).default
  const geoJson = await loadGeoJson()

  globe = Globe()(globeContainer.value)
    .width(w)
    .height(h)
    .backgroundColor("#0a0a0f")
    .globeImageUrl("/earth-dark.jpg")
    .polygonsData(geoJson.features)
    .polygonCapColor(getCountryColor)
    .polygonSideColor(() => "rgba(30,30,50,0.5)")
    .polygonStrokeColor(() => "#1e1e2e")
    .polygonAltitude(0.01)
    .polygonLabel((feature: any) => {
      const iso3 = feature.properties?.ADM0_A3 || feature.properties?.ISO_A3
      const score = pulseStore.scores[iso3]
      const name = feature.properties?.NAME || iso3
      const scoreStr = score ? (score.composite_score * 100).toFixed(0) : "N/A"
      return `<div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;padding:8px 12px;font-family:monospace;"><div style="font-size:14px;font-weight:bold;color:#fff;">${name}</div><div style="font-size:12px;color:#aaa;">Pulse: ${scoreStr}/100</div></div>`
    })
    .onPolygonClick((feature: any) => {
      const iso3 = feature.properties?.ADM0_A3 || feature.properties?.ISO_A3
      if (iso3) {
        uiStore.selectCountry(iso3)
        globe.controls().autoRotate = false
      }
    })

  globe.controls().autoRotate = true
  globe.controls().autoRotateSpeed = 0.3
  globe.controls().enableZoom = true
  globe.pointOfView({ lat: 20, lng: 0, altitude: 2.5 })
})

watch(() => pulseStore.scores, () => {
  if (globe) globe.polygonCapColor(getCountryColor)
}, { deep: true })

function onResize() {
  if (!globe || !globeContainer.value) return
  globe.width(globeContainer.value.clientWidth).height(globeContainer.value.clientHeight)
}

onMounted(() => window.addEventListener("resize", onResize))
onUnmounted(() => {
  window.removeEventListener("resize", onResize)
  if (globe) globe._destructor?.()
})
</script>
