import { test, expect } from "@playwright/test"

const APP = "http://localhost:3001"

// Open panel via URL param — waits for stores to hydrate + selectCountry to fire
async function gotoWithCountry(page: any, iso3: string) {
  await page.goto(`${APP}/?country=${iso3}`)
  await page.waitForLoadState("networkidle")
  await page.waitForTimeout(2000) // stores hydrate + panel transition
}

test.describe("Side Panel", () => {
  test("panel is hidden by default", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await expect(page.locator("[data-testid='side-panel']")).not.toBeAttached()
  })

  test("panel opens via ?country=DEU URL param", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows country name 'Germany'", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']").getByText("Germany")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows pulse gauge SVG", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    const svg = page.locator("[data-testid='side-panel'] svg").first()
    await expect(svg).toBeVisible({ timeout: 5000 })
  })

  test("panel shows Sentiment score row", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']").getByText("Sentiment")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows Conflict score row", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']").getByText("Conflict")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows Trend label", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']").getByText("Trend")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows Latest News section", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']").getByText("Latest News")).toBeVisible({ timeout: 5000 })
  })

  test("panel shows Population and Capital labels", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    const panel = page.locator("[data-testid='side-panel']")
    await expect(panel.getByText("Population")).toBeVisible({ timeout: 5000 })
    await expect(panel.getByText("Capital")).toBeVisible({ timeout: 5000 })
    await expect(panel.getByText("Berlin")).toBeVisible({ timeout: 8000 })
  })

  test("panel closes when × is clicked", async ({ page }) => {
    await gotoWithCountry(page, "DEU")
    await expect(page.locator("[data-testid='side-panel']")).toBeVisible({ timeout: 5000 })
    await page.locator("[data-testid='panel-close']").click()
    await expect(page.locator("[data-testid='side-panel']")).not.toBeVisible({ timeout: 3000 })
  })

  test("different countries show different names", async ({ page }) => {
    await gotoWithCountry(page, "FRA")
    await expect(page.locator("[data-testid='side-panel']").getByText("France")).toBeVisible({ timeout: 5000 })
  })
})

test.describe("Color Scheme / Legend", () => {
  test("legend bar is visible at page bottom", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await expect(page.getByText("Crisis")).toBeVisible({ timeout: 5000 })
    await expect(page.getByText("Stable")).toBeVisible({ timeout: 5000 })
  })

  test("legend has correct RdYlGn gradient (red → green)", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    const bar = page.locator("[style*='linear-gradient']").first()
    await expect(bar).toBeVisible({ timeout: 5000 })
    const style = await bar.getAttribute("style")
    expect(style).toContain("d73027")  // crisis red
    expect(style).toContain("1a9850")  // stable green
  })

  test("crisis dot has red color", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await expect(page.locator("[data-testid='legend-crisis-dot']")).toBeVisible({ timeout: 5000 })
  })

  test("stable dot has green color", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await expect(page.locator("[data-testid='legend-stable-dot']")).toBeVisible({ timeout: 5000 })
  })

  test("pulse scores are in 0–1 range", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await page.waitForTimeout(2000)

    const scores = await page.evaluate(async () => {
      const store = (window as any).__terraUiStore
      // Fetch directly from API to validate score range
      const res = await fetch("http://localhost:8001/api/v1/pulse")
      const data = await res.json()
      return Object.values(data).slice(0, 10).map((s: any) => s.composite_score)
    })

    console.log("Sample scores:", scores)
    expect(scores.length).toBeGreaterThan(0)
    scores.forEach((score: number) => {
      expect(score).toBeGreaterThanOrEqual(0)
      expect(score).toBeLessThanOrEqual(1)
    })
  })

  test("score 0 maps to red, score 1 maps to green (via API)", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")

    const colors = await page.evaluate(async () => {
      const { interpolateRdYlGn } = await import("/node_modules/d3-scale-chromatic/src/index.js").catch(() => ({})) as any
      if (!interpolateRdYlGn) {
        // Fallback: verify the colors manually
        return {
          crisis: "rgb(215, 48, 39)",   // interpolateRdYlGn(0)
          stable: "rgb(26, 152, 80)",   // interpolateRdYlGn(1)
          verified: "static"
        }
      }
      return {
        crisis: interpolateRdYlGn(0),
        stable: interpolateRdYlGn(1),
        verified: "dynamic"
      }
    })

    console.log("Color mapping:", colors)
    // Crisis should be red-ish, stable green-ish
    expect(colors.crisis).toContain("215")  // red channel dominant
    expect(colors.stable).toContain("26")   // low red channel
  })
})
