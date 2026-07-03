# Deploying the Maharahjong Founding Edition landing page to Shopify

This guide takes the files in `web/landing/` and gets the pre-order landing page
live on **maharahjong.com**, with working email capture. Estimated time: ~20 min.

Files in this folder:
- `index.html` — standalone preview (open locally to see the design; not uploaded to Shopify)
- `shopify-page.liquid` — the page to paste into your theme
- `DEPLOY.md` — this guide

---

## Step 1 — Upload the marketing images as theme assets

**Admin → Online Store → Themes → (your live theme) → ⋯ → Edit code → Assets → Add a new asset.**

Upload each file below, **renamed exactly** as shown (the Liquid references these
flat filenames via `{{ '...' | asset_url }}`):

| Upload this repo file | Rename the asset to |
|---|---|
| `design/marketing/hero/hero-banner.png` | `hero-banner.png` |
| `design/marketing/hero/tile-showcase-strip.png` | `tile-showcase-strip.png` |
| `design/marketing/hero/og-image.png` | `og-image.png` |
| `design/tiles/print-ready/honors/deity-garuda.png` | `tile-garuda.png` |
| `design/tiles/print-ready/bonus-festival/festival-diwali.png` | `tile-diwali.png` |
| `design/tiles/print-ready/suit-peacock/peacock-5.png` | `tile-peacock-5.png` |
| `design/tiles/print-ready/bonus-chakra/chakra-anahata.png` | `tile-anahata.png` |

> The 4 "marketing images" called out in the brief are the first three hero assets
> plus the showcase strip. The four tile close-ups are small extras for the artwork grid.

---

## Step 2 — Create the page from the Liquid template

**Option A — dedicated template (recommended, no theme header/footer clutter):**
1. Edit code → **Templates → Add a new template** → type **page** → **Liquid** → name **`maharahjong-landing`**.
2. Replace the placeholder with the entire contents of `shopify-page.liquid`. Save.
3. **Admin → Online Store → Pages → Add page.** Title: **Maharahjong**.
4. In the right sidebar **Theme template** dropdown, choose **`page.maharahjong-landing`**. Save.
5. Note the page handle (URL), e.g. `maharahjong.com/pages/maharahjong`.

**Option B — Custom Liquid section (fastest, keeps theme chrome):**
1. **Admin → Online Store → Themes → Customize.**
2. Add section → **Custom Liquid** → paste `shopify-page.liquid`. Save.

---

## Step 3 — Set the page as the homepage

So maharahjong.com opens directly on the landing page:

1. **Admin → Online Store → Preferences** — this is where the homepage/SEO title live,
   but the actual "homepage = this page" swap is done in the theme.
2. Easiest reliable method: **Themes → Customize → (top page-selector dropdown) → Pages → Maharahjong**,
   confirm it renders, then either:
   - **Redirect approach:** Admin → Online Store → Navigation → **URL Redirects** → Add redirect: `/` → `/pages/maharahjong`, **or**
   - **Homepage template approach:** rename/duplicate the section content into `templates/index.*` (the Home template) so the default homepage renders the landing content.
3. Publish the theme when you're happy with the preview.

> If you only need it live quickly, Option B (Custom Liquid on the existing Home page)
> plus publishing is the shortest path.

---

## Step 4 — Hook up the OG / social share image

The `index.html` preview references `og-image.png` directly. In Shopify, set it via SEO:

1. **Admin → Online Store → Preferences → Social sharing image** → upload
   `design/marketing/hero/og-image.png` (1200×630). This is what appears when the
   link is shared on social/messaging.
2. **Preferences → Title and meta description** — set:
   - Title: `Maharahjong — Founding Edition`
   - Description: `Four traditions, one table. A premium Indian-fusion mahjong set. Join the Founding Edition waitlist.`
3. (Optional) For a page-specific share image, edit the page's SEO section under
   **Pages → Maharahjong → Edit website SEO**.

---

## Step 5 — Verify email capture

The signup forms use Shopify's native `{% form 'customer' %}` and tag each
submission **`preorder`**. No app required.

1. Open the live page, enter a test email, submit. You should see the gold
   "Welcome. You're on the Founding Edition list" confirmation.
2. **Admin → Customers.** Your test email appears as a customer.
3. Filter/search by tag **`preorder`** to confirm the tag applied
   (Customers → Filters → Tagged with → `preorder`).
4. Each entry also carries a note indicating which form (hero vs. signup) captured it.

> To collect these as a marketing list, connect **Shopify Email** or your ESP and
> build a segment on `Customer tag = preorder`.

---

## Step 6 — Follow-up (do this later, not required for launch)

Once pricing and timing firm up, convert interest into reservations:

1. **Admin → Products → Add product** → **Founding Edition Maharahjong Set**.
2. Save it as a **Draft** for now (not published) so it doesn't appear before you're ready.
3. When ready to take reservations, decide the mechanism:
   - a **deposit** product (partial-payment app), or
   - a full **pre-order** listing with a clearly stated ship window, or
   - a "notify me / reserve" flow that just collects intent.
4. Email the `preorder` segment to announce reservations opening.

---

## Quick reference — asset filenames the Liquid expects

```
hero-banner.png
tile-showcase-strip.png
og-image.png
tile-garuda.png
tile-diwali.png
tile-peacock-5.png
tile-anahata.png
```

If an image doesn't show, the asset name almost certainly doesn't match one of
these exactly (Shopify asset names are case-sensitive).
