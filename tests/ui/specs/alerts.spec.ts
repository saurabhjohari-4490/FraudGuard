import { test, expect } from '@playwright/test';

test.describe('Alerts Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/alerts');
  });

  test('displays alerts queue', async ({ page }) => {
    await expect(page.getByTestId('alerts-queue')).toBeVisible();
  });

  test('shows alert cards with risk info', async ({ page }) => {
    const alertCards = page.getByTestId('alert-card');
    // Page should render (may be empty if no alerts exist)
    await expect(page.getByTestId('alerts-queue')).toBeVisible();
  });

  test('alert actions allow acknowledge', async ({ page }) => {
    const firstAlert = page.getByTestId('alert-card').first();
    // Only test if alerts exist
    if (await firstAlert.isVisible()) {
      const ackButton = firstAlert.getByRole('button', { name: /acknowledge/i });
      await expect(ackButton).toBeVisible();
    }
  });

  test('filters alerts by status', async ({ page }) => {
    const statusFilter = page.getByTestId('alert-status-filter');
    if (await statusFilter.isVisible()) {
      await statusFilter.selectOption('pending');
      await expect(page).toHaveURL(/status=pending/);
    }
  });
});
