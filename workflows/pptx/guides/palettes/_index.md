# Palettes — Index

**Reference — not a constraint**: a set of reusable **starting color palettes**. Each entry supplies concrete HEX for the eight semantic color roles plus the temperament and usage limits those values carry.

**This catalog is not identity.** It never produces a brand identity, never acts as a default lock, and never overrides colors the user or an installed Brand/Deck workspace already fixed. Precedence: user-specified → template (Brand/Deck) identity → this catalog → a project-specific proposal authored from the deck's own material.

**Reading discipline**: during planning read this index only. After the direction is fixed, read the one or two selected entry files. Never glob the directory and never pre-read unselected siblings — the planning load set is already near its budget.

---

## 1. Catalog

| Palette | Temperament | Field | Primary | Accent | Accent as text | Paired visual styles (✓✓ best / ✓ workable) |
|---|---|---|---|---|---|---|
| [`prussian-cartier`](prussian-cartier.md) | Cold, restrained, authoritative | light | `#013E75` | `#A52424` | yes | ✓✓ `editorial` `photo-editorial` · ✓ `swiss-minimal` `data-journalism` `brutalist` `vintage-poster` `ink-notes` `ink-wash` |
| [`morandi-green`](morandi-green.md) | Fresh, quiet, natural | light | `#6B8957` | `#4E643F` | yes | ✓✓ `editorial` `photo-editorial` `ink-wash` · ✓ `swiss-minimal` `data-journalism` `paper-cut` `sketch-notes` `soft-rounded` `ink-notes` |
| [`avocado-lime`](avocado-lime.md) | Alert, modern, botanical | light | `#423F3D` | `#7FA921` | **no — fill only** | ✓✓ `swiss-minimal` `data-journalism` · ✓ `editorial` `photo-editorial` `brutalist` `paper-cut` `soft-rounded` |
| [`titien-green`](titien-green.md) | Retro, editorial, period | light | `#1F4433` | `#B05B24` | display / fill only | ✓✓ `editorial` `photo-editorial` `vintage-poster` · ✓ `data-journalism` `paper-cut` `brutalist` `swiss-minimal` |
| [`dior-gold-brown`](dior-gold-brown.md) | Established, rich, restrained luxury | light | `#592F23` | `#A99563` | **no — fill only** | ✓✓ `vintage-poster` `paper-cut` · ✓ `editorial` `photo-editorial` `data-journalism` `brutalist` `swiss-minimal` |
| [`hermes-orange`](hermes-orange.md) | Decisive, commercial, high impact | light | `#373A3E` | `#FF8A00` | **no — fill only** | ✓✓ `brutalist` `swiss-minimal` · ✓ `editorial` `data-journalism` `photo-editorial` `vintage-poster` `memphis` `paper-cut` |
| [`calm-down-winter`](calm-down-winter.md) | Cold, clear, atmospheric | light | `#223F59` | `#336383` | yes | ✓✓ `editorial` `photo-editorial` `data-journalism` · ✓ `swiss-minimal` `brutalist` `ink-notes` `ink-wash` |
| [`vintage-british`](vintage-british.md) | Old-world, dense, autumnal | light | `#2C1A1E` | `#6A1F2A` | yes | ✓✓ `vintage-poster` `editorial` · ✓ `photo-editorial` `paper-cut` `brutalist` `data-journalism` |

**Field lightness is a hard pairing constraint**: a `light` palette never pairs with a dark-field style (`dark-tech`, `glassmorphism`, `chalkboard`, `blueprint`); a `dark` palette never pairs with the light-field styles (`swiss-minimal`, `editorial`, `brutalist`, `memphis`, `zine`, `vintage-poster`, `paper-cut`, `sketch-notes`, `ink-notes`, `ink-wash`, `soft-rounded`). `data-journalism` accepts either field.

---

## 2. Selection boundary

Compare the project's actual conditions before taking an entry; never select by industry keyword or topic noun.

| Dimension | What to compare |
|---|---|
| Viewing distance and medium | Projection (needs contrast and size headroom) / on-screen reading (saturation can drop) / print (needs paper white) |
| Decision weight | Reviews and approvals lean cold and restrained; brand and narrative pages may lean warm or rich |
| Existing material | A dominant color already in the source (logo, charts, photography) — then the catalog only seeds an adjustment |
| Style already fixed | Take the intersection with the `Paired visual styles` column; when the intersection is empty, change palette rather than forcing a pairing |
| Accent use | A fill-only accent cannot carry text; plan its foreground (`body_text` on the accent block) before choosing it |

---

## 3. Division of labor with `visual-styles/`

- **`visual-styles/` owns form** — shape language, composition, whitespace, decoration density, texture — and states explicitly that it carries no HEX.
- **This catalog owns color** — concrete values, proportion, field lightness, and the limits of each accent.
- The two combine freely; the only hard interaction is the field-lightness constraint above. A style's §3 discipline (restraint, meaning-coded color, no gradients) must be honorable by the palette; when it is not, choose another palette.

---

## 4. Role derivation

An entry normally declares **three author colors** (background / primary / accent); the other five roles are derived by one fixed rule set and must not be hand-edited:

| Role | Rule |
|---|---|
| `secondary_bg` | background mixed 7% toward primary |
| `secondary_accent` | primary mixed 28% toward white (35% on a dark field) |
| `body_text` | primary hue, lightness driven to 0.10, saturation capped at 0.22 (on a dark field: accent hue, lightness 0.92) |
| `secondary_text` | body_text mixed 36% toward background (42% on a dark field) |
| `divider` | background mixed 15% toward body_text (18% on a dark field) |

**Documented exceptions** — allowed only when the entry states the reason:

- A source card with more than three colors may override one derived role (e.g. `morandi-green` is a four-color card whose white directly becomes `secondary_bg`).
- A monochromatic card may derive `accent` from `primary` by a lightness step, so the emphasis color can still carry text.
- An accent that is intrinsically low-contrast (bright green, orange, gold) may be declared **fill-only**: it carries no text, and the entry must state the foreground used on top of it together with its measured contrast.

**Contrast thresholds** (measured, recorded in every entry's value table; aligned with WCAG AA and the visual-review H4 dual threshold):

| Role | Threshold |
|---|---|
| `body_text` | ≥ 7:1 |
| `secondary_text` | ≥ 4.5:1 |
| `primary` | ≥ 4.5:1; or ≥ 3:1 with a "display only" note |
| `accent` | one of: ≥ 4.5:1; ≥ 3:1 with a "display / fill only" note; or fill-only at ≥ 1.3:1 with its on-fill foreground and contrast recorded |
| `secondary_accent` | no text duty; below 4.5:1 it must be marked as fill or series use |

---

## 5. Provenance and boundary

All eight entries come from palette cards the user supplied as images; the HEX labels printed on those cards were re-sampled and matched within ±2, and the printed values were kept. Per-entry provenance is in each file's `来源` bullet; the sampling record is in the session log.

Cards with more than three colors map one given color per role and document it: `morandi-green` (4 colors, white → `secondary_bg`), `calm-down-winter` (5 colors, near-black → `body_text`), `vintage-british` (10 colors, 5 adopted — sand/ink-maroon/deep-red/green-grey/maroon for background/primary/accent/secondary_accent/secondary_text; the remaining five stay a documented extension ramp).

The color names in the entries (including ones borrowed from fashion houses) follow the wording on the inspiration cards. **They are not any brand's official palette and carry no brand authorization.** For outward-facing material, use the brand's own supplied values.

> Entry prose is written in Chinese because the source cards and the library's owner are Chinese; role ids, catalog columns, and every field name stay English so the entries remain machine-consistent with the rest of this package.
