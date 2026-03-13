export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],
  components: {
    dirs: [{ path: "~/components", pathPrefix: false }],
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
    },
  },

  app: {
    head: {
      title: "Terra Pulse — The world's heartbeat, visualized",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content:
            "Real-time geopolitical intelligence platform. Every country's pulse, live.",
        },
        { property: "og:title", content: "Terra Pulse" },
        { property: "og:description", content: "The world's heartbeat, visualized." },
      ],
    },
  },

  tailwindcss: {
    config: {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            "terra-dark": "#0a0a0f",
            "terra-panel": "#111118",
            "terra-border": "#1e1e2e",
          },
          fontFamily: {
            mono: ["JetBrains Mono", "Fira Code", "monospace"],
          },
        },
      },
    },
  },

  ssr: false, // Globe needs browser APIs
})
