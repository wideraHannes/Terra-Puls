import { defineStore } from "pinia"

export interface PulseScore {
  iso3: string
  composite_score: number
  sentiment_score: number
  conflict_score: number
  trend: string
  name?: string
}

export const usePulseStore = defineStore("pulse", {
  state: () => ({
    scores: {} as Record<string, PulseScore>,
    lastUpdated: null as Date | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    scoreForCountry: (state) => (iso3: string) => state.scores[iso3] ?? null,
    allScores: (state) => Object.values(state.scores),
  },

  actions: {
    async fetchAll() {
      const config = useRuntimeConfig()
      this.loading = true
      this.error = null

      try {
        const data = await $fetch<Record<string, PulseScore>>(
          `${config.public.apiBase}/api/v1/pulse`
        )
        this.scores = data
        this.lastUpdated = new Date()
      } catch (e: any) {
        this.error = e.message ?? "Failed to fetch pulse data"
      } finally {
        this.loading = false
      }
    },

    async fetchOne(iso3: string) {
      const config = useRuntimeConfig()
      try {
        const data = await $fetch<PulseScore>(
          `${config.public.apiBase}/api/v1/pulse/${iso3}`
        )
        this.scores[iso3] = data
        return data
      } catch {
        return null
      }
    },
  },
})
