# Page Layout Library

Reusable page-local structures, still `kind: layout`. Select any number for
individual pages, optionally alongside one base collection in `layouts/`.
A package may offer multiple variants; it does not prescribe a whole-deck
sequence, brand, palette, or font identity. Whole-deck planning unifies those.

## Package contract

Use the same portable workspace and structured SVG/slot contract as
[`layouts/README.md`](../../workflows/pptx/resources/layouts/README.md). Each package contains
`templates/design_spec.md`, complete Slide prototypes, and its required
`images/` and `icons/` resources. Frontmatter adds `layout_scope: page`;
keep `layout_id`, `kind: layout`, canvas, roster, and placeholder declarations.

Discovery reads only `page_layouts_index.json`, never scans directories or
infers selection scope from page count. Layout IDs must be distinct across
all selected Layout packages. Selected structures must share one canvas.

## Registration

```bash
python3 ${SKILL_DIR}/scripts/register_template.py <id> --kind layout --layout-scope page --dry-run
python3 ${SKILL_DIR}/scripts/register_template.py <id> --kind layout --layout-scope page
```

## Application

Confirm the selected page packages in Stage 1, then install all selected
roots with `apply_template.py --root ... --root ...`. The installer keeps
source packages unchanged, prefixes page prototypes and Master/Layout keys,
namespaces images and imported icon names, and writes source/file fingerprints
to `template_install.json`. Conflicting IDs, canvas mismatches and destination
collisions stop before writing. Rerunning the same roots is idempotent.

Stage 2 reads every installed spec and the exact installed prototypes.
`page_layouts` records one prototype per output page; `page_pptx_layouts`
records its output Layout. Select only fitting pages, preserve the chosen
slot contract, and resolve appearance from the common Brand/project plan.
The installed composed project is not a new portable template root: to
repeat installation, supply the original selected roots.

Page-layout composition currently supports authored `standard` / `fidelity`
packages. `mirror` packages retain source payload/theme ancestry and stay in
the collection library; the installer rejects page-scoped mirror input before
writing rather than silently losing that ancestry.
