"""Per-hotspot satellite evidence: Sentinel-5P NO2 (independent combustion tracer) + AlphaEarth embedding change 2017->2024."""
import os, certifi, json; os.environ["SSL_CERT_FILE"]=certifi.where()
import ee; ee.Initialize(project=os.environ['GOOGLE_CLOUD_PROJECT'])
H=json.load(open('data/hotspots_final.json'))
nga=ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_na','Nigeria')).geometry()
no2=lambda a,b: ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2').filterDate(a,b).select('tropospheric_NO2_column_number_density').mean()
n25=no2('2025-01-01','2026-01-01'); n19=no2('2019-01-01','2020-01-01')
bg=n25.reduceRegion(ee.Reducer.median(),nga,5000,maxPixels=1e10).getInfo()
emb=ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
e=lambda y: emb.filterDate(f'{y}-01-01',f'{y+1}-01-01').mosaic()
# AlphaEarth vectors are unit-length; dot product = cosine similarity; low similarity = surface changed
sim=e(2017).multiply(e(2024)).reduce(ee.Reducer.sum()).rename('sim')
fc=ee.FeatureCollection([ee.Feature(ee.Geometry.Point([h['lon'],h['lat']]).buffer(5000),{'id':h['id']}) for h in H])
r1=ee.Image.cat(n25.rename('no2_2025'),n19.rename('no2_2019')).reduceRegions(fc,ee.Reducer.mean(),1113).getInfo()
fc2=ee.FeatureCollection([ee.Feature(ee.Geometry.Point([h['lon'],h['lat']]).buffer(2000),{'id':h['id']}) for h in H])
r2=sim.lt(0.7).rename('changed').reduceRegions(fc2,ee.Reducer.mean(),10).getInfo()
out={'no2_background_2025':list(bg.values())[0]}
for f in r1['features']: out.setdefault(f['properties']['id'],{}).update({k:f['properties'][k] for k in ('no2_2025','no2_2019')})
for f in r2['features']: out[f['properties']['id']]['frac_changed_2017_2024']=f['properties']['mean']
json.dump(out,open('out/hotspot_satellite_stats.json','w'),indent=1)
for h in H:
    o=out[h['id']]; print(h['id'],f"NO2 x{o['no2_2025']/out['no2_background_2025']:.2f} bg  2019->2025 {o['no2_2025']/o['no2_2019']-1:+.0%}  surface changed {o['frac_changed_2017_2024']:.1%}  {h['name']}")
