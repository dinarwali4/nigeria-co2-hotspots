import json, numpy as np, zipfile, html
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.cm as cm, matplotlib.colors as mc
H=json.load(open('data/hotspots_final.json')); S=json.load(open('out/hotspot_satellite_stats.json'))
HS=json.load(open('out/hotspots.json')); fl=json.load(open('data/flare_pixels.json')); ct=json.load(open('data/ct_facilities.json'))
bg=S['no2_background_2025']
tot=np.load('data/tot1km.npy'); meta=json.load(open('data/tot1km_meta.json'))
# EDGAR 1km overlay (log scale, transparent below 300 t/km2)
v=np.log10(np.clip(tot,1,None)); a=((v-2.5)/(5.5-2.5)).clip(0,1)
rgba=(cm.inferno(a)*255).astype('u1'); rgba[...,3]=np.where(tot>300,np.clip(80+a*175,0,255),0).astype('u1')
Image.fromarray(rgba).save('earth/edgar_co2_2024_1km.png')
Hh,Ww=tot.shape; W0,N0=meta['W'],meta['N']
def la(h,when,rng):
    ts=f'<gx:TimeStamp><when>{when}</when></gx:TimeStamp>' if when else ''
    return f'<LookAt>{ts}<longitude>{h["lon"]}</longitude><latitude>{h["lat"]}</latitude><altitude>0</altitude><heading>0</heading><tilt>0</tilt><range>{rng}</range><altitudeMode>relativeToGround</altitudeMode></LookAt>'
edg={i+1:r for i,r in enumerate(HS['hotspots'])}
k=['<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document><name>Nigeria CO2 hotspots (Dinar Wali / RegenX, Oct 2026)</name><open>1</open>',
 '<description>Open View ▸ Historical Imagery first: the "historical" views carry a gx:TimeStamp that sets the imagery date.</description>',
 '<Style id="hot"><IconStyle><scale>1.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/firedept.png</href></Icon></IconStyle><LabelStyle><scale>0.9</scale></LabelStyle></Style>',
 '<Style id="v"><IconStyle><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>',
 '<Style id="fl"><IconStyle><color>ff00a5ff</color><scale>0.5</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>',
 '<Style id="fl14"><IconStyle><color>ffff00ff</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>',
 f'<GroundOverlay><name>EDGAR 2025 fossil CO2, 1 km, year 2024 (log, t/km²/yr)</name><visibility>0</visibility><Icon><href>edgar_co2_2024_1km.png</href></Icon><LatLonBox><north>{N0}</north><south>{N0-Hh*0.01}</south><east>{W0+Ww*0.01}</east><west>{W0}</west></LatLonBox></GroundOverlay>',
 '<Folder><name>Hotspots (latest + historical views)</name><open>1</open>']
for h in H:
    s=S[h['id']]; e=edg.get(h['edgar_cluster']) if h['edgar_cluster'] else None
    rng=20000 if h['id'] in ('H01','H03','H09') else 6500
    fac=[f for f in ct if abs(f['lat']-h['lat'])<0.06 and abs(f['lon']-h['lon'])<0.06]; fac.sort(key=lambda f:-f['co2_t'])
    d=f"<b>{html.escape(h['name'])}</b> ({h['state']})<br>Type: {h['type']}<br>"
    if e: d+=f"EDGAR 2024 cluster: <b>{e['emis_t']/1e6:.2f} Mt CO₂/yr</b> ({e['share']:.1%} of Nigeria), {e['area_km2']} km², dominant {e['dominant']}<br>EDGAR 0.1° trend 2005/2015/2025: {e['trend_Mt']['2005']:.1f} / {e['trend_Mt']['2015']:.1f} / {e['trend_Mt']['2025']:.1f} Mt<br>"
    if fac: d+='Climate TRACE 2024: '+'; '.join(f"{html.escape(f['name'])} {f['co2_t']/1e6:.2f} Mt" for f in fac[:3])+'<br>'
    d+=f"Sentinel-5P NO₂ 2025: ×{s['no2_2025']/bg:.2f} national median; 2019→2025 {s['no2_2025']/s['no2_2019']-1:+.0%}<br>AlphaEarth surface change 2017→2024 (2 km radius): {s['frac_changed_2017_2024']:.1%}"
    k.append(f'<Folder><name>{h["id"]} {html.escape(h["name"])}</name>'
      f'<Placemark><name>{h["id"]} {html.escape(h["name"])}</name><description><![CDATA[{d}]]></description>{la(h,None,rng)}<styleUrl>#hot</styleUrl><Point><coordinates>{h["lon"]},{h["lat"]},0</coordinates></Point></Placemark>'
      f'<Placemark><name>Latest imagery</name>{la(h,"2026-10-09",rng)}<styleUrl>#v</styleUrl><Point><coordinates>{h["lon"]},{h["lat"]},0</coordinates></Point></Placemark>'
      f'<Placemark><name>Historical ~2015</name>{la(h,"2015-06-30",rng)}<styleUrl>#v</styleUrl><Point><coordinates>{h["lon"]},{h["lat"]},0</coordinates></Point></Placemark>'
      f'<Placemark><name>Historical ~2005</name>{la(h,"2005-06-30",rng)}<styleUrl>#v</styleUrl><Point><coordinates>{h["lon"]},{h["lat"]},0</coordinates></Point></Placemark></Folder>')
k.append('</Folder>')
for lab,sty,nm in (('2024_25','fl','Persistent fires ≥60 days, 2024–25 (MODIS) = gas flares'),('2014_15','fl14','Persistent fires ≥60 days, 2014–15 (MODIS)')):
    k.append(f'<Folder><name>{nm}</name>')
    for f in fl[lab]:
        x,y=f['geometry']['coordinates']; k.append(f'<Placemark><name>{f["properties"]["days"]} d</name><description>{f["properties"]["days"]} detection days</description><styleUrl>#{sty}</styleUrl><Point><coordinates>{x:.4f},{y:.4f},0</coordinates></Point></Placemark>')
    k.append('</Folder>')
k.append('</Document></kml>')
with zipfile.ZipFile('earth/Nigeria_CO2_Hotspots.kmz','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('doc.kml','\n'.join(k)); z.write('earth/edgar_co2_2024_1km.png','edgar_co2_2024_1km.png')
print('ok')
