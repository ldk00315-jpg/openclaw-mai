---
name: ebay-locale-setup
description: Set up eBay browsing locale for shopping automation. Use when asked to open eBay, switch Ship to to United States, and switch language to English before further browsing/actions.
---

# eBay locale setup

Use this flow at the start of eBay tasks.

## Steps

1. Open eBay top page.
   - Navigate to `https://www.ebay.com/`.

2. Set shipping country to United States.
   - Click the top-bar **Ship to** button.
   - In the country list, select **United States**.
   - Confirm/apply if a Done/Apply button appears.

3. Set language to English.
   - Click the top-bar language button (often shows current language like 日本語/English).
   - Select **English** from the dropdown.

4. Verify before continuing.
   - Confirm top bar shows:
     - `Ship to United States`
     - `Select Language. Current: English`

## Notes

- eBay may auto-localize from system/browser locale. Prefer UI switching (top-bar controls) over URL params.
- If controls are missing, refresh once and retry from step 1.
- Re-run this flow when a new browser context/session starts.
