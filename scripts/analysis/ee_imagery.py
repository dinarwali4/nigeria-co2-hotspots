"""Latest vs historical imagery chips per hotspot + AlphaEarth k-means (the original script's method) — Earth Engine."""
import os, certifi, json, urllib.request, urllib.error, ssl, sys; os.environ["SSL_CERT_FILE"]=certifi.where()
import ee; ee.Initialize(project=os.environ['GOOGLE_CLOUD_PROJECT'])
ctx=ssl.create_default_context(cafile=certifi.where())
H=json.load(open('data/hotspots_final.json'))
HALF={'H01':9000,'H03':9000,'H09':9000}  # metro views wider (m half-width); default 3500
def box(h):
    d=HALF.get(h['id'],3500); return ee.Geometry.Point([h['lon'],h['lat']]).buffer(d).bounds()
cs=ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED')
def s2(a,b,g,coll='COPERNICUS/S2_SR_HARMONIZED'):
    c=ee.ImageCollection(coll).filterBounds(g).filterDate(a,b).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',60)).sort('CLOUDY_PIXEL_PERCENTAGE').limit(20).linkCollection(cs,['cs_cdf'])
    c=c.map(lambda i:i.updateMask(i.select('cs_cdf').gte(0.65)))
    return c.select(['B4','B3','B2']).median().clip(g), c.size()
def l7(g):
    c=ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').filterBounds(g).filterDate('1999-07-01','2003-05-30').filter(ee.Filter.lt('CLOUD_COVER',40)).sort('CLOUD_COVER').limit(15)
    c=c.map(lambda i:i.updateMask(i.select('QA_PIXEL').bitwiseAnd(0b11000).eq(0)).select(['SR_B3','SR_B2','SR_B1']).multiply(0.0000275).add(-0.2))
    return c.median(), c.size()
def save(img,vis,g,path):
    u=img.visualize(**vis).getThumbURL({'region':g,'dimensions':1024,'format':'png'})
    if os.path.exists(path) and os.path.getsize(path)>1000: return
    for t in range(3):
        try:
            open(path,'wb').write(urllib.request.urlopen(u,context=ctx,timeout=300).read()); return
        except urllib.error.HTTPError as ex:
            print('  ',path,ex.code,ex.read()[:300],flush=True)
    raise SystemExit('failed '+path)
emb=ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL')
meta={}
only=sys.argv[1:]
for h in H:
    if only and h['id'] not in only: continue
    g=box(h); i=h['id']; m={}
    img,n=s2('2025-01-01','2026-10-01',g); save(img,{'min':0,'max':2500,'gamma':1.2},g,f'out/img/{i}_s2_2025-26.png'); m['s2_latest_n']=n.getInfo()
    img,n=s2('2016-01-01','2017-12-31',g,'COPERNICUS/S2_HARMONIZED'); save(img,{'min':0,'max':2800,'gamma':1.2},g,f'out/img/{i}_s2_2016-17.png'); m['s2_hist_n']=n.getInfo()
    img,n=l7(g); save(img,{'min':0,'max':0.25,'gamma':1.2},g,f'out/img/{i}_l7_2000-02.png'); m['l7_n']=n.getInfo()
    # AlphaEarth k-means, exactly the linked script's workflow (sample -> wekaKMeans -> cluster), k=8
    for y in (2017,2024):
        e=emb.filterDate(f'{y}-01-01',f'{y+1}-01-01').filterBounds(g).mosaic()
        tr=e.sample(region=g,scale=10,numPixels=500,seed=1,geometries=False)
        cl=e.cluster(ee.Clusterer.wekaKMeans(8).train(tr)) if y==2017 else e.cluster(km)
        if y==2017: km=ee.Clusterer.wekaKMeans(8).train(tr)  # same clusterer applied to both years
        if y==2017: cl=e.cluster(km)
        save(cl,{'min':0,'max':7,'palette':['1b9e77','d95f02','7570b3','e7298a','66a61e','e6ab02','a6761d','666666']},g,f'out/img/{i}_emb_k8_{y}.png')
    e17=emb.filterDate('2017-01-01','2018-01-01').filterBounds(g).mosaic(); e24=emb.filterDate('2024-01-01','2025-01-01').filterBounds(g).mosaic()
    sim=e17.multiply(e24).reduce(ee.Reducer.sum())
    save(sim,{'min':0.3,'max':1,'palette':['b2182b','ef8a62','fddbc7','f7f7f7']},g,f'out/img/{i}_emb_change_2017-2024.png')
    m['bbox']=g.coordinates().getInfo()
    meta[i]=m; json.dump(m,open(f'out/meta/{i}.json','w')); print(i,m['s2_latest_n'],m['s2_hist_n'],m['l7_n'],flush=True)
