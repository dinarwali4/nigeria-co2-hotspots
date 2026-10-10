"""Builds site/index.html (artifact page) from the analysis outputs."""
import json, html

H = json.load(open('data/hotspots_final.json'))
S = json.load(open('out/hotspot_satellite_stats.json'))
HS = json.load(open('out/hotspots.json'))
CT = json.load(open('data/ct_facilities.json'))
BG = S['no2_background_2025']
BG_TREND = 0.165  # national median NO2 2019 -> 2025
edg = {i + 1: r for i, r in enumerate(HS['hotspots'])}

STORY = {
 'H01': "Nigeria's largest fossil-CO₂ cluster: 962 km² of Lagos with road transport, the Egbin gas plant and Ikeja–Agbara industry. Emissions roughly doubled 2005→2015, then flattened. NO₂ growth (+12%) is below the national background (+16.5%).",
 'H02': "Bush in 2000–02, a sand-filled platform in 2016–17, and a complete 650,000 bbl/day refinery with tank farms by 2025–26. Climate TRACE puts it at 2.65 Mt in 2024, its first operating year. EDGAR's 1 km grid does not show it yet. AlphaEarth flags 58% of the surrounding 2 km as changed since 2017.",
 'H03': "Second-largest cluster: the Port Harcourt and Onne fertiliser complexes (3.15 + 1.64 Mt), the Eleme refineries, and the Afam V/VI power stations. It has the highest NO₂ of any site (×2.34 the national median), and persistent flares sit on its southern and eastern edges.",
 'H04': "The NLNG trains and their power plant on Bonny Island. Bonny is the national LNG export point. CO₂ stripped from the feed gas, plus fuel burned on site, gives a 5.4 Mt EDGAR cluster in only 100 km². Persistent fire pixels sit on the plant every year.",
 'H05': "Africa's largest cement plant. The 2000–02 frame is untouched savanna; the plant was built later that decade. EDGAR's emissions for this cell rose from 0.7 to 6.5 Mt between 2005 and 2025. Climate TRACE estimates 3.87 Mt for the plant itself.",
 'H06': "Absent from EDGAR's grid, but Climate TRACE estimates 2.83 Mt. Imagery shows a small works in 2016–17 grown into a multi-line plant with new quarry benches by 2025–26. NO₂ rose 45% between 2019 and 2025, the strongest rise above background of any site.",
 'H07': "Dangote's Ibese works in Ogun: no plant in 2000–02, kilns by 2016–17, and expanded quarries and clinker storage by 2025–26. 2.0–2.2 Mt/yr. NO₂ ×2.28 the national median.",
 'H08': "The far north's only large point source, at about 2.4 Mt (Climate TRACE). New kiln lines and quarry floors appear between 2016–17 and 2025–26. EDGAR under-allocates it.",
 'H09': "A transport-dominated urban cluster of 310 km². This hotspot comes from road fuel and generators, not one chimney. Emissions rose from 2.3 to 4.1 Mt between 2005 and 2025 at 0.1°.",
 'H10': "Ughelli gas-fired station (1.81 Mt, Climate TRACE). Persistent flares from the surrounding Ughelli fields sit just south-east. EDGAR's estimate for the 0.1° cells here fell slightly from 3.2 to 2.6 Mt over 2005–2025.",
 'H11': "Azura-Edo IPP: cleared ground in 2016–17 and an operating 461 MW plant by 2025–26, beside the older Ihovbor station. Climate TRACE estimates 2.12 Mt for Azura alone.",
 'H12': "Dangote Gboko in Benue: quarry pit and kiln lines grow steadily across the three frames. NO₂ rose 31% between 2019 and 2025, which is above the background.",
 'H13': "Lafarge Mfamosing near Calabar: a rural landscape in 2000–02, the plant and quarry by 2016–17, and a second quarry by 2025–26. NO₂ rose 36% between 2019 and 2025.",
 'H14': "The largest persistent gas-flare site of 2024–25, with fire on up to 229 of 730 days across 19 km². It was not in the 2014–15 top list. Climate TRACE assigns 9.5 Mt to the onshore conventional fields that include this area.",
 'H15': "The largest flare site of 2014–15, with fire on up to 255 days, and still second in 2024–25. Flares emit little NO₂ (×1.16), so the satellite fire record is the evidence here, not the NO₂ map.",
 'H16': "Rejected. EDGAR puts 0.69 Mt into a single 1 km pixel here that first appears in 2025. The imagery shows farmland and villages, NO₂ is at background (×1.11), and no facility is listed. This is an inventory allocation error, not an emitter.",
}
FL = {'H14': (2935, 19, 229), 'H15': (2008, 14, 225)}

def fmt(x, d=2):
    return f"{x:.{d}f}"

def best(h):
    e = edg.get(h['edgar_cluster']) if h['edgar_cluster'] else None
    fac = [f for f in CT if abs(f['lat'] - h['lat']) < 0.06 and abs(f['lon'] - h['lon']) < 0.06 and f['sector'] not in ('international-shipping', 'domestic-shipping', 'international-aviation', 'domestic-aviation')]
    fac.sort(key=lambda f: -f['co2_t'])
    return e, fac

rows = []
for h in H:
    if h['id'] in ('H14', 'H15', 'H16'):
        continue
    e, fac = best(h)
    ev = e['emis_t'] / 1e6 if e else 0
    cv = fac[0]['co2_t'] / 1e6 if fac else 0
    rows.append((h, ev, cv))
rows.sort(key=lambda r: -max(r[1], r[2]))
mx = max(max(r[1], r[2]) for r in rows)

# ---- ranking chart (SVG, two bars per site: EDGAR cluster, Climate TRACE top facility)
bar_h, gap, top, lw, cw = 11, 9, 26, 196, 560
n = len(rows)
H_svg = top + n * (2 * bar_h + 2 + gap) + 24
svg = [f'<svg viewBox="0 0 {lw + cw + 70} {H_svg}" role="img" aria-label="Hotspot emissions ranking" class="rank">']
for t in range(0, 14, 2):
    x = lw + cw * t / 13
    svg.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top - 6}" y2="{H_svg - 22}" class="grid"/>'
               f'<text x="{x:.1f}" y="{H_svg - 6}" class="tick" text-anchor="middle">{t}</text>')
svg.append(f'<text x="{lw + cw + 4}" y="{H_svg - 6}" class="tick">Mt CO₂/yr</text>')
y = top
for h, ev, cv in rows:
    svg.append(f'<text x="{lw - 10}" y="{y + bar_h + 4}" class="lab" text-anchor="end">{h["id"]} · {html.escape(h["name"].split(",")[0].split(" – ")[0][:30])}</text>')
    for k, (v, cls, src) in enumerate(((ev, 's1', 'EDGAR 1 km cluster, 2024'), (cv, 's2', 'Climate TRACE largest facility, 2024'))):
        yy = y + k * (bar_h + 2)
        w = cw * v / 13
        if v > 0:
            svg.append(f'<g class="bar"><title>{h["id"]} — {src}: {v:.2f} Mt</title><rect x="{lw}" y="{yy}" width="{max(w, 2):.1f}" height="{bar_h}" rx="2" class="{cls}"/>'
                       f'<rect x="{lw}" y="{yy - 2}" width="{cw}" height="{bar_h + 4}" fill="transparent"/>'
                       f'<text x="{lw + w + 6:.1f}" y="{yy + bar_h - 2}" class="val">{v:.2f}</text></g>')
        else:
            svg.append(f'<text x="{lw + 4}" y="{yy + bar_h - 2}" class="val muted">not in grid</text>' if k == 0 else f'<text x="{lw + 4}" y="{yy + bar_h - 2}" class="val muted">no facility listed</text>')
    y += 2 * bar_h + 2 + gap
svg.append('</svg>')
rank_svg = '\n'.join(svg)

# ---- hotspot cards
cards = []
for h in H:
    i = h['id']; s = S[i]
    e, fac = best(h)
    no2r = s['no2_2025'] / BG
    no2c = s['no2_2025'] / s['no2_2019'] - 1
    excess = no2c - BG_TREND
    rej = i == 'H16'
    facts = []
    if e:
        facts.append(('EDGAR cluster 2024', f"{e['emis_t']/1e6:.2f} Mt · {e['area_km2']} km²"))
        t = e['trend_Mt']
        facts.append(('EDGAR 0.1° 2005 → 2015 → 2025', f"{t['2005']:.1f} → {t['2015']:.1f} → {t['2025']:.1f} Mt"))
    if fac:
        facts.append(('Climate TRACE 2024', '<br>'.join(f"{html.escape(f['name'])}: {f['co2_t']/1e6:.2f} Mt" for f in fac[:2])))
    if i in FL:
        pdays, px, mxd = FL[i]
        facts.append(('MODIS persistent fire 2024–25', f"{px} km² · max {mxd} of 730 days"))
    facts.append(('NO₂ 2025 vs national median', f"×{no2r:.2f}"))
    facts.append(('NO₂ change 2019 → 2025', f"{no2c:+.0%} <span class='muted'>({excess:+.0%} vs background)</span>"))
    facts.append(('Surface changed 2017 → 2024', f"{s['frac_changed_2017_2024']:.1%} of 2 km radius"))
    dl = ''.join(f'<div class="fact"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in facts)
    imgs = ''.join(
        f'<figure><img src="img/{i}_{f}.jpg" alt="{h["id"]} {cap}" loading="lazy" width="640" height="640"><figcaption>{cap}</figcaption></figure>'
        for f, cap in (('l7_2000-02', 'Landsat 7 · 2000–02'), ('s2_2016-17', 'Sentinel-2 · 2016–17'), ('s2_2025-26', 'Sentinel-2 · 2025–26 (latest)'),
                       ('emb_k8_2024', 'AlphaEarth k-means (k=8) · 2024'), ('emb_change_2017-2024', 'AlphaEarth change 2017→2024 (red = changed)')))
    tag = 'Rejected' if rej else h['type']
    cards.append(f'''<article class="spot{' rejected' if rej else ''}" id="{i.lower()}">
  <header><span class="hid">{i}</span><div><h3>{html.escape(h['name'])}</h3>
  <p class="where">{h['state']} · {h['lat']:.3f}° N, {h['lon']:.3f}° E · <span class="pill{' bad' if rej else ''}">{html.escape(tag)}</span></p></div></header>
  <p class="story">{STORY[i]}</p>
  <div class="strip">{imgs}</div>
  <dl class="facts">{dl}</dl>
</article>''')

# EDGAR top-20 table
trs = ''.join(
    f"<tr><td>{k}</td><td>{r['state']}</td><td class='num'>{r['lat']:.3f}, {r['lon']:.3f}</td><td class='num'>{r['emis_t']/1e6:.2f}</td><td class='num'>{r['share']:.1%}</td><td class='num'>{r['area_km2']}</td><td>{r['dominant']}</td>"
    f"<td class='num'>{r['trend_Mt']['2005']:.1f} / {r['trend_Mt']['2015']:.1f} / {r['trend_Mt']['2025']:.1f}</td><td>{html.escape(r['facilities'][0]['name'][:44]) if r['facilities'] else '—'}</td></tr>"
    for k, r in enumerate(HS['hotspots'], 1))

nat = HS['coarse_Mt']
page = open('scripts/page_template.html').read()
page = (page.replace('{{RANK}}', rank_svg).replace('{{CARDS}}', '\n'.join(cards)).replace('{{TABLE}}', trs)
        .replace('{{NAT2025}}', f"{nat['2025']:.1f}").replace('{{NAT2005}}', f"{nat['2005']:.1f}")
        .replace('{{GROWTH}}', f"{nat['2025']/nat['2005']-1:.0%}").replace('{{K50}}', f"{HS['k50']:,}")
        .replace('{{LANDPCT}}', f"{HS['k50']/HS['land_km2']:.2%}"))
open('site/index.html', 'w').write(page)
print('ok', len(page))
