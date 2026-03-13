import { test, expect } from "@playwright/test"

test("debug page render", async ({ page }) => {
  const logs: string[] = []
  page.on("console", (msg) => logs.push(`${msg.type()}: ${msg.text()}`))
  page.on("pageerror", (err) => logs.push(`PAGEERROR: ${err.message}`))

  await page.goto("http://localhost:3001")
  await page.waitForTimeout(5000)

  const html = await page.evaluate(() => document.getElementById("__nuxt")?.innerHTML ?? "EMPTY")
  console.log("__nuxt innerHTML length:", html.length)
  console.log("__nuxt innerHTML preview:", html.slice(0, 500))
  console.log("Console logs:", logs.slice(0, 20))
  
  await page.screenshot({ path: "tests/screenshot.png", fullPage: true })
})
