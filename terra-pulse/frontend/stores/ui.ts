import { defineStore } from "pinia"

export const useUiStore = defineStore("ui", {
  state: () => ({
    selectedIso3: null as string | null,
    sidePanelOpen: false,
    activeLayer: "pulse" as "pulse" | "sentiment" | "conflict",
    globeRotating: true,
  }),

  actions: {
    selectCountry(iso3: string | null) {
      this.selectedIso3 = iso3
      this.sidePanelOpen = iso3 !== null
    },

    closePanel() {
      this.selectedIso3 = null
      this.sidePanelOpen = false
    },

    setLayer(layer: "pulse" | "sentiment" | "conflict") {
      this.activeLayer = layer
    },
  },
})
