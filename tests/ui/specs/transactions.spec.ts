import { test, expect } from '@playwright/test';

test.describe('Transactions Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/transactions');
  });

  test('displays transaction search bar', async ({ page }) => {
    await expect(page.getByTestId('transaction-search')).toBeVisible();
  });

  test('displays transaction list', async ({ page }) => {
    await expect(page.getByTestId('transaction-list')).toBeVisible();
  });

  test('search filters transactions', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('user_0001');
    await searchInput.press('Enter');
    // Verify API was called with search param
    await page.waitForResponse(resp =>
      resp.url().includes('/api/v1/transactions') && resp.url().includes('user_0001')
    );
  });

  test('clicking transaction shows detail view', async ({ page }) => {
    const firstRow = page.getByTestId('transaction-row').first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
      await expect(page.getByTestId('transaction-detail')).toBeVisible();
      await expect(page.getByTestId('risk-breakdown')).toBeVisible();
    }
  });

  test('pagination controls work', async ({ page }) => {
    const nextPage = page.getByRole('button', { name: /next/i });
    if (await nextPage.isEnabled()) {
      await nextPage.click();
      await expect(page).toHaveURL(/page=2/);
    }
  });
});
