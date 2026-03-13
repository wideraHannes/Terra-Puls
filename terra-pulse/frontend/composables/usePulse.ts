export function usePulse() {
  const pulseStore = usePulseStore()

  let interval: ReturnType<typeof setInterval> | null = null

  const start = async () => {
    await pulseStore.fetchAll()
    interval = setInterval(() => {
      pulseStore.fetchAll()
    }, 60_000) // Poll every 60s
  }

  const stop = () => {
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  onUnmounted(stop)

  return { start, stop }
}
