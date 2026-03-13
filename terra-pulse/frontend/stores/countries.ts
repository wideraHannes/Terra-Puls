import { defineStore } from "pinia"

export interface Country {
  iso3: string
  iso2: string
  name: string
  capital: string | null
  region: string
  subregion: string
  population: number
  latitude: number
  longitude: number
  currency_code: string | null
  flag_url: string
}

export const useCountriesStore = defineStore("countries", {
  state: () => ({
    countries: [] as Country[],
    loading: false,
  }),

  getters: {
    byIso3: (state) => {
      const map: Record<string, Country> = {}
      state.countries.forEach((c) => {
        map[c.iso3] = c
      })
      return map
    },
  },

  actions: {
    async fetchAll() {
      const config = useRuntimeConfig()
      this.loading = true
      try {
        const data = await $fetch<Country[]>(
          `${config.public.apiBase}/api/v1/countries`
        )
        this.countries = data
      } finally {
        this.loading = false
      }
    },
  },
})
