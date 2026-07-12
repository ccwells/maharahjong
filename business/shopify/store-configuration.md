# Maharajong — Shopify Store Configuration Guide

**Store URL**: maharajong.myshopify.com/admin
**Custom domain**: maharajong.com (DNS propagated ✅ 2026-07-12)
**Shopify plan**: Basic
**Closes**: GitHub issue #22

---

## DNS & SSL status

| Record | Value | Status |
|--------|-------|--------|
| `maharajong.com` A | `23.227.38.71` (Shopify) | ✅ Propagated |
| `www.maharajong.com` CNAME | `shops.myshopify.com` | ✅ Propagated |
| SSL certificate | HTTPS / HTTP2 active | ✅ Active |

---

## 1. Store settings
**Path**: Settings → General

| Field | Value |
|-------|-------|
| Store name | Maharajong |
| Store email | hello@maharajong.com |
| Store currency | USD — United States Dollar |
| Unit system | Imperial |
| Default weight unit | Pounds (lb) |
| Time zone | *(set to your local timezone)* |

---

## 2. Domain configuration
**Path**: Settings → Domains

1. Confirm `maharajong.com` is listed and set as **Primary domain**
2. Enable **"Redirect all traffic to this domain"** so `www.maharajong.com` → `maharajong.com`
3. Verify the green "Connected" indicator appears next to maharajong.com

---

## 3. Branded email
**Path**: Settings → Notifications → Sender email

1. Set sender email to `hello@maharajong.com`
2. Shopify will send a verification email — click the link to confirm
3. If using Google Workspace:
   - Set up `hello@maharajong.com` in Google Workspace Admin
   - Add Shopify's SPF record to DNS: `v=spf1 include:shops.myshopify.com ~all`
   - This ensures transactional emails (order confirmations, shipping) pass spam filters

---

## 4. Brand assets
**Path**: Settings → Brand

### Interim logo (placeholder until issue #42 is resolved)
The standalone vector logo does not yet exist (see issue #42).
Use the tile back image as a placeholder:

1. Open `design/tiles/tile-back/tile-back.png`
2. Crop to a square, centred on the lotus-peacock motif
3. Export at **512 × 512 px PNG** with white or transparent background
4. Upload at Settings → Brand → **Logo**
5. Add a note internally: *"Placeholder — replace when #42 (logo design) is complete"*

### Favicon (placeholder)
1. From the same cropped square, export at **32 × 32 px** as `.png`
2. Upload at Settings → Brand → **Favicon image**

### Brand colours
Configure these under Settings → Brand → **Brand colours** if your theme supports it:

| Role | Colour | Hex |
|------|--------|-----|
| Primary / accent | Gold | `#D4AF37` |
| Background / base | Lapis navy | `#1C2E5E` |
| Surface | Ivory cream | `#F5EDD8` |
| Highlight | Magenta | `#C2185B` |
| Highlight 2 | Teal | `#00897B` |

---

## 5. Staff accounts
**Path**: Settings → Users and permissions

- Add collaborators with **Limited permissions** (Staff role) — do not share the Owner credential
- Owner account should use 2FA; enforce 2FA for staff in Settings → Security

---

## 6. Checkout & payments (preliminary — full setup in issue #25)
**Path**: Settings → Payments

Enable now to avoid blocking test orders:
- Activate **Shopify Payments** (primary, eliminates 2% transaction fee on Basic)
- Enable **PayPal** as backup
- Enable **Shop Pay**, **Apple Pay**, **Google Pay** under express checkout

---

## 7. Contact information
**Path**: Settings → Store details → Contact information

Ensure the following are set (required for policy pages and invoices):
- Business legal name
- Business address (used on tax invoices)
- Country: United States

---

## 8. Customer accounts
**Path**: Settings → Customer accounts

- Set to **Optional** (do not force account creation at checkout — reduces friction)

---

## 9. Checkout settings
**Path**: Settings → Checkout

| Setting | Value |
|---------|-------|
| Customer accounts | Guest checkout allowed |
| Require first and last name | Yes |
| Company name | Optional |
| Address line 2 | Optional |
| Shipping address phone number | Required |
| Tipping | Off (premium product, not applicable) |
| Order processing | Automatically fulfil only the gift cards of the order |

---

## 10. Post-setup checklist

- [ ] Store name set to "Maharajong"
- [ ] Currency set to USD
- [ ] maharajong.com confirmed as primary domain with redirect enabled
- [ ] SSL green in Settings → Domains
- [ ] hello@maharajong.com set as sender and verified
- [ ] Placeholder logo uploaded (512×512px, tile-back.png cropped)
- [ ] Favicon uploaded (32×32px)
- [ ] Brand colours configured
- [ ] Shopify Payments activated
- [ ] Customer accounts set to Optional
- [ ] Staff accounts created if needed
- [ ] Issue #42 (logo design) created and assigned ✅

---

## Next steps

| Issue | Task |
|-------|------|
| #42 | Replace placeholder logo with final vector logo mark |
| #23 | Storefront theme design & brand customisation |
| #25 | Payment processing & checkout optimisation (full setup) |
| #27 | Legal compliance — Privacy Policy, Terms, Refund Policy |
