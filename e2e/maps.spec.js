// @ts-check
const { test, expect } = require('@playwright/test');

// Wait for Leaflet tiles — CartoDB tiles render as <img> inside .leaflet-tile-pane
async function waitForTiles(page) {
  await page.waitForLoadState('domcontentloaded');
  await expect(
    page.locator('.leaflet-tile-pane img.leaflet-tile').first()
  ).toBeVisible({ timeout: 20_000 });
}

// ── Home page choropleth map ────────────────────────────────────────────────
// County geometry is not yet imported; home page shows ZIP polygons only.
test.describe('Home page map', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('map container renders', async ({ page }) => {
    await expect(page.locator('#map')).toBeVisible();
  });

  test('Leaflet tiles load', async ({ page }) => {
    await waitForTiles(page);
  });

  test('ZIP GeoJSON polygons render', async ({ page }) => {
    await expect(
      page.locator('.leaflet-overlay-pane svg path').first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('hovering a polygon updates the info panel', async ({ page }) => {
    await page.waitForSelector('.leaflet-overlay-pane svg path', { timeout: 10_000 });
    await page.locator('.leaflet-overlay-pane svg path').first().hover();
    // Info control (not the legend) shows radon data
    await expect(
      page.locator('.leaflet-control.info:not(.legend)')
    ).toContainText('pCi/L');
  });

  test('clicking a polygon opens a popup link', async ({ page }) => {
    await page.waitForSelector('.leaflet-overlay-pane svg path', { timeout: 10_000 });
    await page.locator('.leaflet-overlay-pane svg path').first().click();
    await expect(page.locator('.leaflet-popup-content a')).toBeVisible({ timeout: 5_000 });
  });

  test('map legend is visible', async ({ page }) => {
    await expect(page.locator('.legend')).toBeVisible();
  });
});

// ── ZIP code page map ───────────────────────────────────────────────────────
test.describe('ZIP code page map', () => {
  test.beforeEach(async ({ page }) => {
    // 43016 (Dublin, OH) — confirmed to have geometry and radon data
    await page.goto('/zip/43016/');
  });

  test('map container renders', async ({ page }) => {
    await expect(page.locator('#map')).toBeVisible();
  });

  test('Leaflet tiles load', async ({ page }) => {
    await waitForTiles(page);
  });

  test('ZIP boundary polygon renders', async ({ page }) => {
    await expect(
      page.locator('.leaflet-overlay-pane svg path').first()
    ).toBeVisible({ timeout: 10_000 });
  });

  test('radon stat card is visible with a pCi/L value', async ({ page }) => {
    await expect(page.locator('.stat-radon')).toBeVisible();
    await expect(page.locator('.stat-radon')).toContainText('pCi/L');
  });

  test('stat card shows risk color class', async ({ page }) => {
    const cls = await page.locator('.stat-radon').getAttribute('class');
    expect(cls).toMatch(/risk-(high|medium|low)/);
  });
});

// ── County page — no map (county geometry not yet imported) ─────────────────
test.describe('County page data', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/county/franklin/');
  });

  test('page loads and shows county name', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Franklin County');
  });

  test('radon stat card shows county average', async ({ page }) => {
    await expect(page.locator('.stat-radon')).toBeVisible();
    await expect(page.locator('.stat-radon')).toContainText('pCi/L');
  });

  test('ZIP code table has risk-encoded rows', async ({ page }) => {
    const riskRows = page.locator('tr.row-risk-high, tr.row-risk-medium, tr.row-risk-low');
    const count = await riskRows.count();
    expect(count).toBeGreaterThan(0);
  });
});

// ── State page map ──────────────────────────────────────────────────────────
// County geometry not yet imported so choropleth is empty; map + tiles still tested.
test.describe('State page map', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/state/ohio/');
  });

  test('map container renders', async ({ page }) => {
    await expect(page.locator('#map')).toBeVisible();
  });

  test('Leaflet tiles load', async ({ page }) => {
    await waitForTiles(page);
  });

  test('county table has risk-encoded rows', async ({ page }) => {
    const count = await page.locator('tr.row-risk-high, tr.row-risk-medium, tr.row-risk-low').count();
    expect(count).toBeGreaterThan(0);
  });
});

// ── Regression: Leaflet L defined on all map pages ──────────────────────────
test('Leaflet global L is defined on all map pages', async ({ page }) => {
  for (const url of ['/', '/zip/43016/', '/county/franklin/', '/state/ohio/']) {
    await page.goto(url);
    const leafletDefined = await page.evaluate(() => typeof window.L !== 'undefined');
    expect(leafletDefined, `L not defined on ${url}`).toBe(true);
  }
});
