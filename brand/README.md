# Brand artwork

The DeCLaRe robot. Both websites show this mark, so it lives here rather than in
either one — the same test the rest of the core uses.

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
| small | `declare-icon-compact-*` | 32 px and below — favicons, small chrome |

The display cut is two mirrored Z-traces: one enters from the left wall and
steps down to a terminal node on the right, the other enters from the right wall
and steps up to a node on the left, so the pair is rotationally symmetric about
the panel centre. Stroke 6 against the 7.2 walls keeps the board subordinate to
the silhouette.

The small cut is a single trace at wall weight. Below about 32 px the panel is
roughly 7 px tall; two thin traces silt up into an even grey, while one heavy
trace and its node still resolve. This is optical scaling, not a different mark
— the silhouette is identical, so the two cuts are interchangeable at any size
where both still read.

At 16 px the chest is about 3 px tall and no board survives in either cut. That
is a property of the robot, not of the board: the mark reads by its head and
base at that size.

## Regenerating

`tools/build_brand.py` writes every consumer asset from the definitions at the
top of that file — the eight SVGs here, and the logo, favicon, touch-icon and
identity-page assets in both websites.

```sh
python3 tools/build_brand.py            # write everything
python3 tools/build_brand.py --check    # verify sources still match, write nothing
```

It reads each site's SVGs from `git show HEAD:`, so it always patches pristine
sources and re-running never stacks one edit on another. PNG crops are measured
rather than assumed: each committed raster is a tight box around its own drawn
content, so the tool renders a probe, finds the alpha bounding box, maps it back
to user units, and re-renders at the committed pixel size. Headless Chrome does
the rasterising; PNG decoding is stdlib only.

Changing the board means editing `CUTS` in that file and re-running. Do not edit
the generated SVGs — they carry no information the generator does not.
