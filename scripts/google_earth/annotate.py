"""Annotate Google Earth Pro window captures (top-down, heading 0) for the Nigeria CO2 hotspots.

Capture geometry (calibrated 2026-10-09 with magenta markers at known coordinates):
  window capture 2940x1684 px (Retina), LookAt target at px (1469.5, 895.5),
  metres per px = range * 2.812e-4. Clean crop = (199, 250, 2740, 1541).
"""
import json, math, sys
from PIL import Image, ImageDraw, ImageFont

CROP = (199, 250, 2740, 1541)
CX, CY = 1469.5 - CROP[0], 895.5 - CROP[1]
K = 2.812e-4
INK, PAPER, ACC, MUTED = (15, 23, 32), (242, 239, 232), (232, 105, 44), (184, 196, 204)
F = '/System/Library/Fonts/Supplemental/'
def font(sz, bold=False):
    for n in (['Arial Bold.ttf'] if bold else ['Arial.ttf']):
        try: return ImageFont.truetype(F + n, sz)
        except OSError: pass
    return ImageFont.load_default()

def geo2px(lat, lon, lat0, lon0, rng):
    mpp = rng * K
    dx = (lon - lon0) * 111320 * math.cos(math.radians(lat0)) / mpp
    dy = (lat - lat0) * 110574 / mpp
    return CX + dx, CY - dy

def label(d, xy, text, anchor_xy, sub=None):
    """Callout: dot at anchor, leader line, boxed text at xy."""
    ax, ay = anchor_xy; tx, ty = xy
    d.line([(ax, ay), (tx, ty)], fill=PAPER, width=5)
    d.line([(ax, ay), (tx, ty)], fill=ACC, width=3)
    d.ellipse([ax - 11, ay - 11, ax + 11, ay + 11], outline=PAPER, width=4, fill=ACC)
    f1, f2 = font(40, True), font(30)
    w = max(d.textlength(text, font=f1), d.textlength(sub, font=f2) if sub else 0)
    h = 52 + (40 if sub else 0)
    bx = tx - w / 2 - 18; by = ty - h if ty < ay else ty
    d.rounded_rectangle([bx, by, bx + w + 36, by + h], 8, fill=INK + (225,))
    d.text((bx + 18, by + 6), text, font=f1, fill=PAPER)
    if sub: d.text((bx + 18, by + 52), sub, font=f2, fill=MUTED)

def outline(d, pts, dash=False):
    d.line(pts + [pts[0]], fill=ACC, width=6, joint='curve')

def annotate(src, out, site, view, when_label, labels, polys=(), rng_override=None):
    lat0, lon0, rng = view; rng = rng_override or rng
    site = dict(site, sub=site['sub'].replace('₂', '2'), name=site['name'].replace('₂', '2'))
    im = Image.open(src).convert('RGB').crop(CROP)
    W, H = im.size
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for poly in polys:
        pts = [geo2px(a, b, lat0, lon0, rng) for a, b in poly['pts']]
        d.line(pts + [pts[0]], fill=ACC + (255,), width=7)
    for L in labels:
        if 'lat' in L: ax, ay = geo2px(L['lat'], L['lon'], lat0, lon0, rng)
        else: ax, ay = L['fx'] * W, L['fy'] * H
        tx, ty = ax + L.get('dx', 0) * W, ay + L.get('dy', -0.12) * H
        label(d, (tx, ty), L['t'].replace('₂','2'), (ax, ay), (L.get('s') or '').replace('₂','2') or None)
    # scale bar
    mpp = rng * K; target = W * 0.18 * mpp
    nice = max(n for n in (100, 200, 250, 500, 1000, 2000, 2500, 5000) if n <= target)
    bl = nice / mpp; x0, y0 = 40, H - 70
    d.rectangle([x0 - 16, y0 - 54, x0 + bl + 16, y0 + 34], fill=INK + (200,))
    d.rectangle([x0, y0, x0 + bl / 2, y0 + 14], fill=PAPER); d.rectangle([x0 + bl / 2, y0, x0 + bl, y0 + 14], fill=ACC)
    d.text((x0, y0 - 46), f"{nice/1000:g} km" if nice >= 1000 else f"{nice} m", font=font(32, True), fill=PAPER)
    # north arrow
    nx, ny = W - 80, 110
    d.polygon([(nx, ny - 50), (nx - 26, ny + 30), (nx, ny + 14), (nx + 26, ny + 30)], fill=PAPER, outline=INK)
    d.text((nx - 12, ny + 36), 'N', font=font(36, True), fill=PAPER, stroke_width=3, stroke_fill=INK)
    im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    im.save(out.replace('annotated/','body/'), quality=90)
    HB, FB = 150, 64
    can = Image.new('RGB', (W, H + HB + FB), INK); can.paste(im, (0, HB)); c = ImageDraw.Draw(can)
    c.text((40, 20), f"{site['id']} · {site['name']}", font=font(58, True), fill=PAPER)
    c.text((40, 94), site['sub'], font=font(32), fill=MUTED)
    f = font(44, True); tw = c.textlength(when_label, font=f)
    c.rounded_rectangle([W - tw - 80, 38, W - 40, 112], 10, fill=ACC)
    c.text((W - tw - 60, 50), when_label, font=f, fill=INK)
    cr = 'Imagery: Google Earth Pro (provider shown on image) · Emissions: EDGAR 2025, Climate TRACE v6 · Annotation: Dinar Wali, RegenX · Oct 2026'
    c.text((40, H + HB + 16), cr, font=font(28), fill=MUTED)
    can.save(out, quality=92)

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); views = json.load(open('views.json'))
    for s in spec:
        for shot in s['shots']:
            annotate(f"raw/{s['id']}_{shot['tag']}.png", f"annotated/{s['id']}_{shot['tag']}.jpg", s, views[s['id']],
                     shot['when'], shot.get('labels', []), shot.get('polys', []))
            print(s['id'], shot['tag'])
