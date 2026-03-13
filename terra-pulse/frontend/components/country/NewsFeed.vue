<template>
  <div class="space-y-3">
    <div v-if="loading" class="text-gray-500 text-xs font-mono animate-pulse">
      Fetching news...
    </div>
    <div v-else-if="articles.length === 0" class="text-gray-500 text-xs font-mono">
      No recent news available.
    </div>
    <a
      v-for="article in articles"
      :key="article.id"
      :href="article.url"
      target="_blank"
      rel="noopener noreferrer"
      class="block border border-gray-800 rounded-lg p-3 hover:border-gray-600 transition-colors"
    >
      <div class="text-sm text-white font-medium leading-snug mb-2">
        {{ article.title }}
      </div>
      <!-- Sentiment bar -->
      <div class="flex items-center gap-2">
        <div class="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :style="{
              width: `${(article.sentiment ?? 0.5) * 100}%`,
              backgroundColor: sentimentColor(article.sentiment),
            }"
          />
        </div>
        <span class="text-[10px] font-mono text-gray-500">
          {{ sentimentLabel(article.sentiment) }}
        </span>
      </div>
      <div v-if="article.published_at" class="text-[10px] text-gray-600 mt-1 font-mono">
        {{ formatDate(article.published_at) }}
      </div>
    </a>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import { interpolateRdYlGn } from "d3-scale-chromatic"

const props = defineProps<{ iso3: string }>()
const config = useRuntimeConfig()

interface Article {
  id: string
  title: string
  summary: string
  url: string
  sentiment: number
  published_at: string
  source: string
}

const articles = ref<Article[]>([])
const loading = ref(false)

async function fetchNews() {
  loading.value = true
  try {
    const data = await $fetch<Article[]>(
      `${config.public.apiBase}/api/v1/news/${props.iso3}?limit=5`
    )
    articles.value = data
  } catch {
    articles.value = []
  } finally {
    loading.value = false
  }
}

const sentimentColor = (s: number | null) => interpolateRdYlGn(s ?? 0.5)
const sentimentLabel = (s: number | null) => {
  if (s === null || s === undefined) return "neutral"
  if (s >= 0.65) return "positive"
  if (s <= 0.35) return "negative"
  return "neutral"
}
const formatDate = (d: string) => {
  try {
    return new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric" })
  } catch {
    return d
  }
}

watch(() => props.iso3, fetchNews, { immediate: true })
</script>
