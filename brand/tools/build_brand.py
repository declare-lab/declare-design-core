#!/usr/bin/env python3
"""Build every DeCLaRe robot asset from one chest-panel definition.

The robot is a single `<rect fill="currentColor" mask="url(#robot-knockout)">`.
White in that mask is ink, black is a transparent hole.  The chest panel is a
hole, so painting white traces into it (after it, in document order) yields
ink-coloured circuit traces that inherit the theme colour like everything else.

Two optical cuts of the same board:

  full     two mirrored Z-traces.  The mark at display sizes (>= 48 px).
  compact  one trace at wall weight.  Below ~32 px the panel is barely 7 px
           tall and two traces silt up into grey; one heavy trace still reads.

Run with no arguments to write every consumer asset:

    python3 build_brand.py

`--check` renders without writing, for verifying sources still match.
"""
import os, re, struct, subprocess, sys, zlib

GITHUB = '/Users/poriasoujanya/Documents/GitHub'
LAB = os.path.join(GITHUB, 'declare-lab.github.io/assets/images')
PERSONAL = os.path.join(GITHUB, 'soujanyaporia.github.io/assets/images')
CORE_BRAND = os.path.join(GITHUB, 'declare-design-core/brand')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TMP = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'declare-brand-build')

# --------------------------------------------------------------- chest cuts
# The pristine chest: a window and a slot with an ink bar between them.
OLD_WINDOW = '<rect x="59.3" y="113.4" width="70.9" height="24" fill="#000"/>'
OLD_SLOT = '<rect x="59.3" y="144.6" width="70.9" height="8.3" fill="#000"/>'
# Both become one taller panel that carries the board.
PANEL = ('<!-- chest panel: one tall cut-out carrying the circuit board -->\n'
         '    <rect x="59.3" y="113.4" width="70.9" height="39.5" fill="#000"/>')

CUTS = {
    'full': '''<!-- Circuit board, display cut.  Two mirrored Z-traces: one enters from
         the left wall and steps down to a terminal node on the right, the other
         enters from the right wall and steps up to a node on the left, so the
         pair is rotationally symmetric about the panel centre.  Stroke 6 against
         the 7.2 walls keeps the board subordinate to the silhouette. -->
    <g stroke="#fff" stroke-width="6" stroke-linecap="butt" stroke-linejoin="miter" fill="none">
      <path d="M59.3 121H88l10 10h16"/>
      <path d="M130.2 145H101l-10-10H75"/>
    </g>
    <circle cx="114" cy="131" r="7" fill="#fff"/>
    <circle cx="75" cy="135" r="7" fill="#fff"/>''',

    'compact': '''<!-- Circuit board, small cut.  One trace at wall weight.  Below ~32 px
         the panel is about 7 px tall; two thin traces silt up into grey, while a
         single heavy trace and node still resolve. -->
    <g stroke="#fff" stroke-width="7.5" stroke-linecap="butt" stroke-linejoin="miter" fill="none">
      <path d="M59.3 128H92l10 10h10"/>
    </g>
    <circle cx="112" cy="138" r="8.5" fill="#fff"/>''',
}


def patch(text, cut):
    """Swap the pristine chest for the merged panel plus the given board."""
    assert text.count(OLD_WINDOW) == 1, 'chest window not found (already patched?)'
    assert text.count(OLD_SLOT) == 1, 'chest slot not found (already patched?)'
    out = text.replace(OLD_WINDOW, PANEL)
    i = out.index(OLD_SLOT)                       # drop the slot and its blank line
    out = out[:out.rfind('\n', 0, i) + 1] + out[out.index('\n', i) + 1:]
    a = out.index('</mask>')
    return out[:out.rfind('\n', 0, a) + 1] + '    ' + CUTS[cut] + '\n  ' + out[a:]


# ------------------------------------------- minimal PNG decode (8-bit, no interlace)
def decode_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', path
    pos = 8; w = h = ct = None; idat = b''
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos + 4])[0]; typ = d[pos + 4:pos + 8]
        ch = d[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if typ == b'IHDR':
            w, h, _bd, ct = struct.unpack('>IIBB', ch[:10])
        elif typ == b'IDAT':
            idat += ch
        elif typ == b'IEND':
            break
    raw = zlib.decompress(idat)
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    stride = w * nch
    rows = []; prev = bytes(stride); i = 0
    for _ in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i + stride]); i += stride
        if f == 1:
            for x in range(nch, stride):
                line[x] = (line[x] + line[x - nch]) & 255
        elif f == 2:
            line = bytearray((v + p) & 255 for v, p in zip(line, prev))
        elif f == 3:
            for x in range(stride):
                a = line[x - nch] if x >= nch else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - nch] if x >= nch else 0
                b = prev[x]; c = prev[x - nch] if x >= nch else 0
                p = a + b - c; pa = abs(p - a); pb = abs(p - b); pc = abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        rows.append(bytes(line)); prev = line
    return w, h, nch, rows


# One byte per pixel, 1 where there is ink.  Kept at C speed: translate() maps
# the test over a channel slice, big-int OR folds channels, find/rfind bound the
# row.  A per-pixel Python loop here costs minutes on a 4000px probe.
_OPAQUE = bytes(0 if v <= 8 else 1 for v in range(256))
_NONWHITE = bytes(1 if v < 246 else 0 for v in range(256))


def ink_bbox(path):
    """Box of drawn content: alpha for RGBA, non-white for RGB."""
    w, h, nch, rows = decode_png(path)
    x0, y0, x1, y1 = w, h, -1, -1
    for y in range(h):
        r = rows[y]
        if nch == 4:
            m = r[3::4].translate(_OPAQUE)
        elif nch == 2:
            m = r[1::2].translate(_OPAQUE)
        elif nch == 3:
            m = (int.from_bytes(r[0::3].translate(_NONWHITE), 'big')
                 | int.from_bytes(r[1::3].translate(_NONWHITE), 'big')
                 | int.from_bytes(r[2::3].translate(_NONWHITE), 'big')).to_bytes(w, 'big')
        else:
            m = r.translate(_NONWHITE)
        i = m.find(b'\x01')
        if i < 0:
            continue
        x0 = min(x0, i); x1 = max(x1, m.rfind(b'\x01'))
        y0 = min(y0, y); y1 = max(y1, y)
    return x0, y0, x1 + 1, y1 + 1, w, h


def px_size(path):
    w, h, _n, _r = decode_png(path)
    return w, h


# ------------------------------------------------------------------ rendering
def render(svg, out, px_w, px_h, view=None, bg='00000000'):
    os.makedirs(TMP, exist_ok=True)
    s = svg
    if view:
        s = re.sub(r'viewBox="[^"]*"', 'viewBox="%.4f %.4f %.4f %.4f"' % view, s, count=1)
    s = _set_root_size(s, px_w, px_h)
    html = os.path.join(TMP, '_r.html')
    open(html, 'w').write('<!doctype html><meta charset="utf-8">'
                          '<style>html,body{margin:0;padding:0}svg{display:block}</style>' + s)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', '--default-background-color=' + bg,
                    '--screenshot=' + out, '--window-size=%d,%d' % (px_w, px_h), html],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


_views = {}


def _set_root_size(svg, w, h):
    """Set width/height on the root <svg>, replacing any already there."""
    m = re.search(r'<svg\b[^>]*>', svg)
    tag = re.sub(r'\s+(width|height)="[^"]*"', '', m.group(0))
    tag = tag.replace('<svg', '<svg width="%s" height="%s"' % (w, h), 1)
    return svg[:m.start()] + tag + svg[m.end():]



def content_view(svg, probe):
    """Tight box around an SVG's drawn content, in user units.

    Measuring costs one probe render, so the result is cached.  Theme colour and
    viewBox do not move the geometry, so light and dark (and each site's own
    framing of the same mark) share one measurement.

    `probe` must be at least the width the box will be re-rendered at: the
    measurement is only accurate to one probe pixel, and anything coarser shifts
    the crop off the content by a visible pixel or two.
    """
    key = (re.sub(r'style="color:#[0-9A-Fa-f]{6}"', '',
                  re.sub(r'viewBox="[^"]*"', '', svg)), probe)
    if key in _views:
        return _views[key]
    vx, vy, vw, vh = [float(v) for v in re.search(r'viewBox="([^"]*)"', svg).group(1).split()]
    p = render(svg, os.path.join(TMP, '_probe.png'), probe, max(1, round(probe * vh / vw)))
    x0, y0, x1, y1, w, h = ink_bbox(p)
    _views[key] = (vx + x0 * vw / w, vy + y0 * vh / h, (x1 - x0) * vw / w, (y1 - y0) * vh / h)
    return _views[key]


def export_tight(svg, out, w, h):
    """Re-export at the committed pixel size, cropped tight like the original."""
    # Probe above the target: measuring at exactly the target width leaves the
    # crop a pixel shy of the edges once antialiased fringe is thresholded away.
    render(svg, out, w, h, view=content_view(svg, min(4000, max(round(w * 1.6), 1600))))


def export_square(svg, out, px, height_frac, bg='ffffffff'):
    """Robot centred in a square, occupying `height_frac` of the canvas."""
    cx0, cy0, cw, ch = content_view(svg, 1600)
    size = ch / height_frac
    render(svg, out, px, px, bg=bg,
           view=(cx0 + cw / 2 - size / 2, cy0 + ch / 2 - size / 2, size, size))


def favicon_svg():
    """The small cut as a scalable favicon that follows the tab bar's theme.

    A vector favicon is the only one that is sharp at every size a browser asks
    for. The theme colour moves out of the inline style so a media query can
    reach it: a black robot is invisible on a dark tab strip.
    """
    svg = logo('declare-icon-compact-light')
    assert svg.count('style="color:#000000"') == 1
    svg = svg.replace(' style="color:#000000"', '')
    rule = ('\n  #robot { color: #141413; }\n'
            '  @media (prefers-color-scheme: dark) { #robot { color: #F5F4EF; } }\n')
    return svg.replace('</style>', rule + '</style>', 1)


def write_ico(path, pngs):
    """ICO container holding each PNG at its own size.

    Browsers still request /favicon.ico by name, and packing real per-size
    renders beats letting one bitmap be rescaled into all of them.
    """
    blobs = [open(p, 'rb').read() for p in pngs]
    offset = 6 + 16 * len(blobs)
    entries = b''
    for p, data in zip(pngs, blobs):
        w, h = px_size(p)
        entries += struct.pack('<BBBBHHII', w % 256, h % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    with open(path, 'wb') as f:
        f.write(struct.pack('<HHH', 0, 1, len(blobs)) + entries + b''.join(blobs))


def reembed(explanation_svg_path, lockup_png_path):
    """logo-explanation embeds a base64 copy of the horizontal lockup."""
    import base64
    t = open(explanation_svg_path).read()
    m = re.search(r'(<image[^>]*href="data:image/png;base64,)([^"]+)(")', t)
    assert m, explanation_svg_path
    old = base64.b64decode(m.group(2)); new = open(lockup_png_path, 'rb').read()
    assert struct.unpack('>II', old[16:24]) == struct.unpack('>II', new[16:24]), 'dimension drift'
    open(explanation_svg_path, 'w').write(
        t[:m.start(2)] + base64.b64encode(new).decode() + t[m.end(2):])



# -------------------------------------------------------------------- cleanup
# `#robot-premium` is an alternate line-art robot nothing references -- and it
# still draws the pre-circuit chest, so leaving it in the shared artwork invites
# someone editing the wrong panel.  `.r-*` styles exist only for it; `.thread`
# and the `.octa*` styles are left over from wordmark experiments.
DEAD_GROUPS = ['robot-premium']
DEAD_RULES = ['.r-panel', '.r-line', '.r-node', '.thread', '.octa', '.octa-seam']
DEAD_NOTES = [
    '  /* Premium line-art robot: chamfered panels in wordmark purple, faint fill,\n'
    '     green/red eyes kept as the accent. */\n',
    '  /* Octagon style: lightweight monoline letters, bevel-cut (octagonal) corners,\n'
    '     vertical gradient, and subtle "fused-lego" seams. */\n',
]


def drop_group(svg, gid):
    """Remove `<g id=gid> ... </g>`, matching nested groups."""
    start = svg.index('<g id="%s"' % gid)
    depth = 0; i = start
    while True:
        g = svg.find('<g', i); close = svg.find('</g>', i)
        if 0 <= g < close:
            depth += 1; i = g + 2
        else:
            depth -= 1; i = close + 4
            if depth == 0:
                break
    end = i
    while end < len(svg) and svg[end] in ' \t':
        end += 1
    if end < len(svg) and svg[end] == '\n':
        end += 1
    return svg[:svg.rfind('\n', 0, start) + 1] + svg[end:]


def strip_dead(svg):
    """Drop defs and style rules nothing in this file renders."""
    for gid in DEAD_GROUPS:
        svg = drop_group(svg, gid)
    # any <use> target that is no longer referenced is dead weight too --
    # the icon files carry the whole wordmark and never draw it
    body = svg[svg.index('</defs>'):]
    used = set(re.findall(r'xlink:href="#([^"]+)"', body))
    for gid in re.findall(r'<g id="([^"]+)"', svg):
        if gid.endswith('-master') and gid not in used:
            svg = drop_group(svg, gid)
    for note in DEAD_NOTES:
        svg = svg.replace(note, '')
    style = svg[svg.index('<style'):svg.index('</style>')]
    live = set()
    for attr in re.findall(r'class="([^"]+)"', svg.replace(style, '')):
        live.update('.' + c for c in attr.split())
    kept = [ln for ln in style.split('\n')
            if not any(ln.lstrip().startswith(r + ' ') for r in DEAD_RULES if r not in live)]
    return svg.replace(style, '\n'.join(kept))


# An <img> SVG with no width/height gets the browser's 300px default as its
# intrinsic size, and some engines rasterise at that and scale up. The header
# lockup sits at 138 CSS px, which is 414 device px on a 3x phone: past 300, so
# it upscaled and went soft. Only phones reach that ratio, which is why it never
# showed on a desktop. Declaring a generous intrinsic size settles it.
INTRINSIC_MAX = 1024


def tighten(svg):
    """Set the viewBox to the drawn content and declare an intrinsic size.

    Consumers swap these in for tight-cropped PNGs, so the SVG must carry the
    same aspect and no baked-in padding; spacing belongs to their CSS.
    """
    vx, vy, vw, vh = content_view(svg, 2000)
    svg = re.sub(r'viewBox="[^"]*"', 'viewBox="%.3f %.3f %.3f %.3f"' % (vx, vy, vw, vh),
                 svg, count=1)
    k = INTRINSIC_MAX / max(vw, vh)
    return _set_root_size(svg, round(vw * k), round(vh * k))


# -------------------------------------------------------------------- targets
SRC = os.path.join(CORE_BRAND, 'src')
LOGOS = os.path.join(CORE_BRAND, 'logos')
MARKS = ['declare-icon-light', 'declare-icon-dark',
         'declare-horizontal-light', 'declare-horizontal-dark',
         'declare-square-theme-light', 'declare-square-theme-dark']
# How much of a square icon's height the robot fills. One value per icon kind,
# shared by every site: the same mark should sit the same in every browser tab.
# The two sites had drifted to 42/48 and 39/48, which is only visible when you
# put the two tabs side by side, and is exactly the kind of difference nobody
# notices until it looks careless.
FAVICON_FILL = 42 / 48.0
TOUCH_ICON_FILL = 160 / 180.0
# A browser picks the icon nearest the physical pixels it needs, and a phone at
# 3x wants 48-72 of them for a tab slot. Jumping 48 -> 192 left it stretching the
# 48, which is what looked blurry on mobile. Fill the ladder instead.
#
# Every one of these is displayed small (a tab, a bookmark row) and merely drawn
# at high resolution, so they all use the small cut. Pixel count is not the same
# thing as perceived size.
ICON_SIZES = [16, 32, 48, 64, 96, 128]
ICO_SIZES = [16, 32, 48]
# Home-screen icons are perceived large, so these take the display cut.
TOUCH_SIZES = [192]

SITES = [
    ('declare-lab.github.io', dict(
        images=LAB, rasters=MARKS, favicon=FAVICON_FILL,
        apple=TOUCH_ICON_FILL, explanation=True)),
    # the personal site shows the vector only; its raster copies were duplicates
    # of the lab's and have been retired
    ('soujanyaporia.github.io', dict(
        images=PERSONAL, rasters=[], favicon=FAVICON_FILL)),
]


def build_core():
    """brand/src -> brand/logos.  The only place the artwork is authored."""
    os.makedirs(LOGOS, exist_ok=True)
    for name in MARKS:
        svg = tighten(strip_dead(patch(open(os.path.join(SRC, name + '.svg')).read(), 'full')))
        open(os.path.join(LOGOS, name + '.svg'), 'w').write(svg)
        print('   %-34s %d bytes' % (name + '.svg', len(svg)))
    for theme in ('light', 'dark'):
        src = open(os.path.join(SRC, 'declare-icon-%s.svg' % theme)).read()
        svg = tighten(strip_dead(patch(src, 'compact')))
        out = 'declare-icon-compact-%s.svg' % theme
        open(os.path.join(LOGOS, out), 'w').write(svg)
        print('   %-34s %d bytes' % (out, len(svg)))


def logo(name):
    return open(os.path.join(LOGOS, name + '.svg')).read()


def build_site(images, rasters, favicon, apple=None, explanation=False):
    """Only rasters live in the sites now; the vectors come from the submodule."""
    for name in rasters:
        png = os.path.join(images, 'logos', name + '.png')
        if not os.path.exists(png):
            continue
        w, h = px_size(png)
        export_tight(logo(name), png, w, h)
        print('   %-34s %dx%d' % (name + '.png', w, h))
    # Every icon is rendered at its final size. One bitmap rescaled by the
    # browser into 16, 32, 64 and 128 is what makes a favicon look soft.
    open(os.path.join(images, 'favicon.svg'), 'w').write(favicon_svg())
    print('   %-34s vector, theme-aware' % 'favicon.svg')
    written = {}
    for px in ICON_SIZES:
        # 48 keeps the plain name: things already point at favicon.png, and a
        # favicon-48.png beside it would be the same bytes under a second name
        out = os.path.join(images, 'favicon.png' if px == 48 else 'favicon-%d.png' % px)
        export_square(logo('declare-icon-compact-light'), out, px, favicon)
        written[px] = out
        print('   %-34s %dpx (small cut)' % (os.path.basename(out), px))
    write_ico(os.path.join(os.path.dirname(os.path.dirname(images)), 'favicon.ico'),
              [written[px] for px in ICO_SIZES])
    print('   %-34s %s' % ('favicon.ico', '+'.join(str(p) for p in ICO_SIZES)))
    for px in TOUCH_SIZES:
        out = os.path.join(images, 'icon-%d.png' % px)
        export_square(logo('declare-icon-light'), out, px, apple or TOUCH_ICON_FILL)
        print('   %-34s %dpx (display cut)' % (os.path.basename(out), px))
    ap = os.path.join(images, 'apple-touch-icon.png')
    export_square(logo('declare-icon-light'), ap, 180, apple or TOUCH_ICON_FILL)
    print('   %-34s 180px (display cut)' % 'apple-touch-icon.png')
    if explanation:
        for theme in ('light', 'dark'):
            reembed(os.path.join(images, 'resources', 'logo-explanation-%s.svg' % theme),
                    os.path.join(images, 'logos', 'declare-horizontal-%s.png' % theme))
            print('   %-34s re-embedded lockup' % ('logo-explanation-%s.svg' % theme))


if __name__ == '__main__':
    if '--check' in sys.argv:
        for name in MARKS:
            strip_dead(patch(open(os.path.join(SRC, name + '.svg')).read(), 'full'))
        print('brand/src matches the expected robot geometry')
        raise SystemExit

    print('declare-design-core/brand/logos:')
    build_core()
    for site, cfg in SITES:
        print('%s:' % site)
        build_site(**cfg)

    # Same source, same size, same framing, so the bytes must match. This is
    # what catches the framing drifting apart again.
    favicons = {}
    for site, cfg in SITES:
        p = os.path.join(cfg['images'], 'favicon.png')
        favicons[site] = (px_size(p), open(p, 'rb').read())
    sizes = set(v[0] for v in favicons.values())
    digests = set(v[1] for v in favicons.values())
    assert len(sizes) == 1 and len(digests) == 1, (
        'favicons differ across sites: ' +
        ', '.join('%s %dx%d %d bytes' % ((s,) + v[0] + (len(v[1]),))
                  for s, v in favicons.items()))
    print('every site favicon is identical (%dx%d)' % list(sizes)[0])
    print('done')
