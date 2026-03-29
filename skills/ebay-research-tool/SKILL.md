---
name: ebay-research-tool
description: eBay sold listings research tool. Search any eBay site (ebay.com, ebay.co.uk, ebay.de, etc.) by category, price range, and item location (e.g. Japan). Outputs results to CSV. Use when user asks for eBay market research, sold items analysis, price research, or competitor analysis.
user-invocable: true
---

# eBay Research Tool

Research sold items on eBay and generate a CSV report.

## Parameters

Ask the user for all of the following before starting:
- **eBay site**: target market (e.g. uk, us, de, au)
- **keyword**: product category or search term (e.g. "fountain pen", "seiko watch")
- **price range**: min and max in local currency
- **item location**: country of origin (e.g. Japan)
- **output filename**: optional, default to `~/research/{keyword}_{site}_{date}.csv`

## Workflow

### Step 1: Build the search URL

Construct the URL directly. Do NOT use browser form input (it causes timeouts).

Format:
```
https://{domain}/sch/i.html?_nkw={keyword}&LH_Sold=1&LH_Complete=1&_udlo={min_price}&_udhi={max_price}&LH_PrefLoc=3&_salic={country_code}
```

Domain mapping:
- uk -> www.ebay.co.uk
- us -> www.ebay.com
- de -> www.ebay.de
- au -> www.ebay.com.au
- fr -> www.ebay.fr
- it -> www.ebay.it
- jp -> www.ebay.co.jp

Item location `_salic` codes (verify if unsure):
- Japan: 206
- US: 1
- UK: 3
- Germany: 77
- Australia: 15
- China: 45

URL-encode the keyword (spaces become +).

### Step 2: Access the page

1. Use the browser tool to navigate to the constructed URL.
2. Take a screenshot to verify results loaded correctly.
3. If the page times out, retry once with the same URL.

### Step 3: Extract data

From the search results page, extract for each item:
- Product title
- Sold price (in local currency)
- Shipping cost
- Sold date (if visible)
- Seller name
- Item URL

Check up to 2-3 pages maximum. Navigate to the next page if needed.

### Step 4: Save to CSV

- Create `~/research/` directory if it does not exist.
- Save as UTF-8 CSV with columns: title, price, currency, shipping, total, sold_date, seller, url
- Default filename: `~/research/{keyword}_{site}_{YYYY-MM-DD}.csv`

### Step 5: Report summary

Tell the user:
- Total items found
- Price range (min / avg / max)
- Top sellers (if patterns visible)
- Any notable items

## Important Rules

- ALWAYS build the URL directly. NEVER fill in search forms.
- Prices are in the local currency of the target eBay site.
- If `_salic` code is unknown for a country, try searching "ebay _salic {country}" or skip the filter and tell the user.
- Keep CSV UTF-8 encoded for Japanese and other non-ASCII characters.

## References

See `references/country_codes.md` for the full domain and _salic code table.
See `references/category_keywords.md` for recommended search keywords by category.
