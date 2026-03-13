import { test } from "@playwright/test"

test("find pinia via __vue_app__", async ({ page }) => {
  await page.goto("http://localhost:3001")
  await page.waitForLoadState("networkidle")
  await page.waitForTimeout(2000)
  
  const info = await page.evaluate(() => {
    const app = (window as any).__nuxt?.__vue_app__
    const provides = app?._context?.provides
    const piniaKey = provides ? Object.keys(provides).find(k => provides[k]?._s) : null
    const pinia = piniaKey ? provides[piniaKey] : null
    return {
      provideKeys: provides ? Object.keys(provides).slice(0, 30) : [],
      piniaKey,
      storeIds: pinia ? Array.from(pinia._s.keys()) : [],
    }
  })
  console.log(JSON.stringify(info, null, 2))
})
