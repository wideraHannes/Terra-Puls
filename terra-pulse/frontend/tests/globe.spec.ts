import { test, expect } from "@playwright/test"

const API = "http://localhost:8001"
const APP = "http://localhost:3001"

test.describe("Backend API", () => {
  test("GET /api/v1/countries returns data with CORS header", async ({ request }) => {
    const res = await request.get(`${API}/api/v1/countries`, {
      headers: { Origin: APP },
    })
    expect(res.status()).toBe(200)
    expect(res.headers()["access-control-allow-origin"]).toBe(APP)
    const body = await res.json()
    expect(Array.isArray(body)).toBe(true)
    expect(body.length).toBeGreaterThan(100)
  })

  test("GET /api/v1/pulse returns scores object", async ({ request }) => {
    const res = await request.get(`${API}/api/v1/pulse`, {
      headers: { Origin: APP },
    })
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(typeof body).toBe("object")
    expect(Object.keys(body).length).toBeGreaterThan(0)
  })

  test("GET /health returns ok", async ({ request }) => {
    const res = await request.get(`${API}/health`)
    expect(res.status()).toBe(200)
    expect((await res.json()).status).toBe("ok")
  })
})

test.describe("Frontend Globe", () => {
  test("page loads without JS errors", async ({ page }) => {
    const errors: string[] = []
    page.on("pageerror", (err) => errors.push(err.message))

    await page.goto(APP)
    await page.waitForLoadState("networkidle")

    const fatal = errors.filter(
      (e) =>
        !e.includes("favicon") &&
        !e.includes("ResizeObserver") &&
        !e.includes("WebGL context") // expected in headless Chromium (no GPU)
    )
    console.log("JS errors:", fatal)
    expect(fatal).toHaveLength(0)
  })

  test("frontend fetches countries successfully (no CORS block)", async ({ page }) => {
    const failedRequests: string[] = []
    page.on("requestfailed", (req) => {
      if (req.url().includes("localhost:8001")) {
        failedRequests.push(`${req.url()} — ${req.failure()?.errorText}`)
      }
    })

    await page.goto(APP)
    await page.waitForLoadState("networkidle")

    expect(failedRequests).toHaveLength(0)
  })

  test("TopBar shows TERRA PULSE", async ({ page }) => {
    await page.goto(APP)
    await expect(page.getByText("TERRA PULSE")).toBeVisible({ timeout: 10000 })
  })

  test("globe canvas is mounted with real dimensions (WebGL may be unavailable in headless)", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")
    await page.waitForTimeout(4000)

    // TerraGlobe component mounts a div that globe.gl injects a canvas into
    // In headless Chromium WebGL context creation fails but the container still renders
    const globeDiv = page.locator("div").filter({ has: page.locator("canvas") }).first()
    const containerExists = await page.evaluate(() => {
      // globe.gl appends canvas to the ref'd div
      return document.querySelectorAll("canvas").length > 0
    })

    if (containerExists) {
      const canvas = page.locator("canvas").first()
      const box = await canvas.boundingBox()
      console.log("Canvas bounding box:", box)
      expect(box).not.toBeNull()
      expect(box!.width).toBeGreaterThan(200)
    } else {
      // Headless WebGL unavailable — verify the container div at least has dimensions
      const dims = await page.evaluate(() => {
        const divs = Array.from(document.querySelectorAll("div"))
        const globe = divs.find(d => d.style.width === "100%" && d.style.height === "100%")
        return globe ? { w: globe.clientWidth, h: globe.clientHeight } : null
      })
      console.log("Globe container dims (no WebGL):", dims)
      // Container should still have dimensions even without WebGL
      expect(dims?.w ?? 0).toBeGreaterThan(0)
    }
  })

  test("runtime config uses correct API base", async ({ page }) => {
    await page.goto(APP)
    await page.waitForLoadState("networkidle")

    const apiBase = await page.evaluate(() => {
      // @ts-ignore
      return window.__nuxt_config?.apiBase ?? window.__nuxt?.config?.apiBase ?? null
    })
    console.log("Detected apiBase from window:", apiBase)

    // Check via network: any request to 8001 must have happened
    const requests: string[] = []
    page.on("request", (req) => {
      if (req.url().includes("8001")) requests.push(req.url())
    })

    await page.reload()
    await page.waitForLoadState("networkidle")
    console.log("Requests to :8001:", requests)
    expect(requests.some((r) => r.includes("/api/v1/"))).toBe(true)
  })
})
