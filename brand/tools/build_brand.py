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
    s = s.replace('<svg ', '<svg width="%d" height="%d" ' % (px_w, px_h), 1)
    html = os.path.join(TMP, '_r.html')
    open(html, 'w').write('<!doctype html><meta charset="utf-8">'
                          '<style>html,body{margin:0;padding:0}svg{display:block}</style>' + s)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', '--default-background-color=' + bg,
                    '--screenshot=' + out, '--window-size=%d,%d' % (px_w, px_h), html],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


_views = {}


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


# -------------------------------------------------------------------- targets
LAB_MARKS = ['declare-icon-light', 'declare-icon-dark',
             'declare-horizontal-light', 'declare-horizontal-dark',
             'declare-square-theme-light', 'declare-square-theme-dark']
PERSONAL_MARKS = ['declare-icon-light', 'declare-icon-dark',
                  'declare-square-theme-light', 'declare-square-theme-dark']
PERSONAL_RASTER = ['declare-icon-light', 'declare-icon-dark']


def pristine(repo_images, rel):
    """Read a file as committed, so re-running never double-patches."""
    root = os.path.dirname(os.path.dirname(repo_images))
    rel_to_root = os.path.relpath(os.path.join(repo_images, rel), root)
    return subprocess.run(['git', '-C', root, 'show', 'HEAD:' + rel_to_root],
                          capture_output=True, text=True, check=True).stdout


def build_site(images, marks, raster, favicon_frac, apple=None, explanation=False):
    for name in marks:
        svg_path = os.path.join(images, 'logos', name + '.svg')
        svg = patch(pristine(images, 'logos/' + name + '.svg'), 'full')
        open(svg_path, 'w').write(svg)
        png = os.path.join(images, 'logos', name + '.png')
        if name in raster and os.path.exists(png):
            w, h = px_size(png)
            export_tight(svg, png, w, h)
            print('   %-32s svg + %dx%d png' % (name, w, h))
        else:
            print('   %-32s svg' % name)

    icon_compact = patch(pristine(images, 'logos/declare-icon-light.svg'), 'compact')
    icon_full = patch(pristine(images, 'logos/declare-icon-light.svg'), 'full')
    fav = os.path.join(images, 'favicon.png')
    export_square(icon_compact, fav, px_size(fav)[0], favicon_frac)
    print('   %-32s %dpx (compact cut)' % ('favicon.png', px_size(fav)[0]))
    if apple:
        ap = os.path.join(images, 'apple-touch-icon.png')
        export_square(icon_full, ap, px_size(ap)[0], apple)
        print('   %-32s %dpx (display cut)' % ('apple-touch-icon.png', px_size(ap)[0]))
    if explanation:
        for theme in ('light', 'dark'):
            reembed(os.path.join(images, 'resources', 'logo-explanation-%s.svg' % theme),
                    os.path.join(images, 'logos', 'declare-horizontal-%s.png' % theme))
            print('   %-32s re-embedded lockup' % ('logo-explanation-%s.svg' % theme))


def build_core():
    """Canonical artwork for the design system."""
    out = os.path.join(CORE_BRAND, 'logos')
    os.makedirs(out, exist_ok=True)
    for name in LAB_MARKS:
        svg = patch(pristine(LAB, 'logos/' + name + '.svg'), 'full')
        open(os.path.join(out, name + '.svg'), 'w').write(svg)
        print('   %s.svg' % name)
    for theme in ('light', 'dark'):
        svg = patch(pristine(LAB, 'logos/declare-icon-%s.svg' % theme), 'compact')
        open(os.path.join(out, 'declare-icon-compact-%s.svg' % theme), 'w').write(svg)
        print('   declare-icon-compact-%s.svg' % theme)


if __name__ == '__main__':
    if '--check' in sys.argv:
        for name in LAB_MARKS:
            patch(pristine(LAB, 'logos/' + name + '.svg'), 'full')
        print('sources match the expected chest geometry')
        raise SystemExit

    print('declare-design-core/brand/logos:')
    build_core()
    print('declare-lab.github.io:')
    build_site(LAB, LAB_MARKS, LAB_MARKS, 42 / 48.0, apple=160 / 180.0, explanation=True)
    print('soujanyaporia.github.io:')
    build_site(PERSONAL, PERSONAL_MARKS, PERSONAL_RASTER, 39 / 48.0)
    print('done')
