import { interpolateRdYlGn } from "d3-scale-chromatic"

export function useColorScale() {
  const scoreToColor = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return "#333344"
    const clamped = Math.max(0, Math.min(1, score))
    return interpolateRdYlGn(clamped)
  }

  const scoreToLabel = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return "No data"
    if (score >= 0.75) return "Stable"
    if (score >= 0.55) return "Moderate"
    if (score >= 0.35) return "Elevated Risk"
    return "Crisis"
  }

  const trendIcon = (trend: string): string => {
    switch (trend) {
      case "improving":
        return "↑"
      case "declining":
        return "↓"
      case "crisis":
        return "⚠"
      default:
        return "→"
    }
  }

  return { scoreToColor, scoreToLabel, trendIcon }
}
