# Brand artwork

The DeCLaRe robot. Both websites show this mark, so it lives here rather than in
either one, which is the same test the rest of the core uses.

## How the robot is built

One `<rect fill="currentColor" mask="url(#robot-knockout)">`. White in that mask
is ink, black is a transparent hole. Nothing is painted in a literal colour, so
the mark takes the theme colour and composites on any background; the cut-outs
are real holes rather than opaque light-coloured fills.

The green eye (`#34A853`) and the red angular eye (`#EB4336`) sit on top of the
silhouette and stay fixed in both themes.

## The chest board

The chest panel is a circuit board. Its cut-outs were a window and a slot; they
are now one taller panel (`59.3, 113.4, 70.9 × 39.5`) carrying traces painted
white into the mask, so the board is ink like the rest of the silhouette.

Two optical cuts of the same board:

| Cut | Files | Use |
|---|---|---|
| display | `declare-icon-*`, `declare-horizontal-*`, `declare-square-theme-*` | 48 px and above, and every vector context |
| small | `declare-icon-compact-*` | 32 px and below: favicons, small chrome |

The display cut is two mirrored Z-traces: one enters from the left wall and
steps down to a terminal node on the right, the other enters from the right wall
and steps up to a node on the left, so the pair is rotationally symmetric about
the panel centre. Stroke 6 against the 7.2 walls keeps the board subordinate to
the silhouette.

The small cut is a single trace at wall weight. Below about 32 px the panel is
roughly 7 px tall; two thin traces silt up into an even grey, while one heavy
trace and its node still resolve. This is optical scaling, not a different
mark: the silhouette is identical, so the two cuts are interchangeable at any
size where both still read.

At 16 px the chest is about 3 px tall and no board survives in either cut. That
is a property of the robot, not of the board: the mark reads by its head and
base at that size.

## Using it

Both websites point straight at this directory through their submodule:

```html
<img src="/assets/declare-core/brand/logos/declare-icon-light.svg" alt="DeCLaRe Lab">
```

Each `viewBox` is tight to the drawn artwork, with no baked-in padding, so
these are drop-in replacements for a tight-cropped PNG and spacing stays with
the consumer's CSS.

Rasters stay local to each site: favicons, touch icons and Open Graph images
need pixel dimensions and framing that belong to the site, not to the mark.
`tools/build_brand.py` writes those too.

## Layout

    src/     the robot as authored, before any board.  Edit nothing else.
    logos/   generated.  Tight viewBox, dead defs stripped, board applied.
    tools/   the generator.

```sh
python3 tools/build_brand.py            # write everything
python3 tools/build_brand.py --check    # verify src still matches, write nothing
```

`logos/` and every consumer raster are generated, so do not hand-edit them. To
change the board, edit `CUTS` in the generator and re-run.

PNG crops are measured rather than assumed: each committed raster is a tight box
around its own drawn content, so the tool renders a probe, finds the alpha
bounding box, maps it back to user units, and re-renders at the committed pixel
size. Headless Chrome does the rasterising; PNG decoding is stdlib only.

The generator also drops what nothing renders: an unused alternate line-art
robot that still carried the pre-circuit chest, the styles only it used, and the
wordmark the icon files never draw. That is verified by rendering before and
after through one fixed viewBox and requiring the pixels to match.
