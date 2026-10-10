import os, certifi, json; os.environ["SSL_CERT_FILE"]=certifi.where()
import ee; ee.Initialize(project=os.environ['GOOGLE_CLOUD_PROJECT'])
nga=ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_na','Nigeria')).geometry().buffer(30000)
# --- Persistent thermal anomalies (gas flares): FIRMS days-with-fire per 1 km pixel
def days(y0,y1):
    c=ee.ImageCollection('FIRMS').filterDate(y0,y1).filterBounds(nga).select('T21')
    return c.map(lambda i:i.gt(0).unmask(0).toByte()).sum().rename('days').clip(nga)
out={}
for lab,(a,b) in {'2024_25':('2024-01-01','2026-01-01'),'2014_15':('2014-01-01','2016-01-01')}.items():
    d=days(a,b)
    v=d.updateMask(d.gte(60)).toInt().reduceToVectors(geometry=nga,scale=1000,geometryType='centroid',
        eightConnected=False,labelProperty='days',maxPixels=1e10,bestEffort=True)
    out[lab]=v.getInfo()['features']; print(lab,len(out[lab]))
json.dump(out,open('data/flare_pixels.json','w'))
