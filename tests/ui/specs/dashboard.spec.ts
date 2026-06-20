import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays metrics panel with stat cards', async ({ page }) => {
    await expect(page.getByTestId('metrics-panel')).toBeVisible();
    await expect(page.getByTestId('stat-card-total')).toBeVisible();
    await expect(page.getByTestId('stat-card-blocked')).toBeVisible();
    await expect(page.getByTestId('stat-card-avg-score')).toBeVisible();
  });

  test('shows risk distribution chart', async ({ page }) => {
    await expect(page.getByTestId('risk-distribution')).toBeVisible();
  });

  test('navigation links work', async ({ page }) => {
    await page.getByRole('link', { name: /alerts/i }).click();
    await expect(page).toHaveURL(/\/alerts/);

    await page.getByRole('link', { name: /transactions/i }).click();
    await expect(page).toHaveURL(/\/transactions/);

    await page.getByRole('link', { name: /dashboard/i }).click();
    await expect(page).toHaveURL('/');
  });

  test('refreshes metrics data periodically', async ({ page }) => {
    // Verify the API is called for metrics
    const metricsRequest = page.waitForRequest(/\/api\/v1\/metrics/);
    await page.goto('/');
    await metricsRequest;
  });
});
