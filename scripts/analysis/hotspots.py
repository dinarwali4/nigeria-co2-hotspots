"""Nigeria fossil-CO2 hotspots from EDGAR 2025 1 km (year 2024) + 0.1 deg trend + Climate TRACE attribution."""
import json, numpy as np, rasterio, geopandas as gpd, xarray as xr
from rasterio.windows import from_bounds
from rasterio.features import geometry_mask
from scipy import ndimage
from shapely.geometry import Point

E='data/edgar/'
SECT=['Energy','Industry','Transport','Residential','Agriculture','Waste']
nga=gpd.read_file('data/nga_country.geojson'); states=gpd.read_file('data/nga_states.geojson')
geom=nga.union_all().buffer(0.05)
W,S,Ea,N=2.6,4.2,14.8,14.0
grids={}
for s in SECT:
    with rasterio.open(f'{E}EDGAR_2025_1km_CO2_2024/CO2_2024_{s}.tif') as r:
        win=from_bounds(W,S,Ea,N,r.transform); a=r.read(1,window=win).astype('f8'); tr=r.window_transform(win)
    grids[s]=np.nan_to_num(a)
mask=~geometry_mask([geom],out_shape=grids['Energy'].shape,transform=tr)
for s in SECT: grids[s]*=mask
tot=sum(grids.values())
H,Wd=tot.shape
lats=N-0.005-0.01*np.arange(H); lons=W+0.005+0.01*np.arange(Wd)
nat=tot.sum()
print('1km national sum (raw units):',f'{nat:,.0f}', {s:f'{grids[s].sum()/nat:.1%}' for s in SECT})

# 0.1 deg check
def nc(y,sec='TOTALS'):
    d=xr.open_dataset(f'{E}EDGAR_2026_GHG_CO2_{y}_{sec}_emi_nc/EDGAR_2026_GHG_CO2_{y}_{sec}_emi.nc')['emissions'].sel(lat=slice(S,N),lon=slice(W,Ea)).values
    return d
la=np.arange(S+0.05,N,0.1); lo=np.arange(W+0.05,Ea,0.1)
la=xr.open_dataset(f'{E}EDGAR_2026_GHG_CO2_2025_TOTALS_emi_nc/EDGAR_2026_GHG_CO2_2025_TOTALS_emi.nc').sel(lat=slice(S,N),lon=slice(W,Ea))
LA,LO=np.meshgrid(la.lat.values,la.lon.values,indexing='ij')
from shapely import contains_xy
m01=contains_xy(geom,LO,LA)
coarse={y:nc(y)*m01 for y in (2005,2015,2025)}
for y in coarse: print(y,'0.1deg Nigeria total Mt:',round(coarse[y].sum()/1e6,1))

# hotspot threshold: smallest set of pixels holding 50% of national emissions
v=np.sort(tot[tot>0])[::-1]; cs=np.cumsum(v)
T=v[np.searchsorted(cs,0.5*nat)]
k50=np.searchsorted(cs,0.5*nat)+1
print(f'50% of emissions from {k50} px (km2) = {k50/mask.sum():.3%} of land; threshold {T:,.0f} t/km2')
hot=tot>=T
lab,n=ndimage.label(ndimage.binary_dilation(hot,iterations=2),structure=np.ones((3,3)))
lab=lab*hot
rows=[]
for i in range(1,n+1):
    m=lab==i
    if not m.any(): continue
    e=tot[m].sum(); w=tot*m
    cy=(w.sum(1)@lats)/e; cx=(w.sum(0)@lons)/e
    yy,xx=np.where(m)
    sec={s:grids[s][m].sum()/e for s in SECT}
    rows.append(dict(id=i,emis_t=e,area_km2=int(m.sum()),lat=cy,lon=cx,
        bbox=[lons[xx.min()]-.005,lats[yy.max()]-.005,lons[xx.max()]+.005,lats[yy.min()]+.005],
        peak_t=tot[m].max(),dominant=max(sec,key=sec.get),sectors=sec))
rows.sort(key=lambda r:-r['emis_t'])
rows=rows[:20]
# state names
for r in rows:
    p=Point(r['lon'],r['lat']); st=states[states.contains(p)]
    r['state']=st.iloc[0]['ADM1_NAME'] if len(st) else states.iloc[states.distance(p).argmin()]['ADM1_NAME']
    r['share']=r['emis_t']/nat
    # 0.1deg trend inside bbox (padded)
    b=r['bbox']; sel=(LO>=b[0]-.05)&(LO<=b[2]+.05)&(LA>=b[1]-.05)&(LA<=b[3]+.05)
    r['trend_Mt']={y:float(coarse[y][sel].sum()/1e6) for y in coarse}
# Climate TRACE facilities (non-land sectors) for attribution
ct=json.load(open('data/climatetrace_nga_2024.json'))
LAND={'cropland-fires','forest-land-fires','shrubgrass-fires','forest-land-degradation','net-forest-land','removals','net-soil-organic-carbon','net-shrubgrass','manure-applied-to-soils','enteric-fermentation-cattle-pasture','manure-left-on-pasture-cattle','synthetic-fertilizer-application','rice-cultivation','crop-residues','net-wetland','forest-land-clearing','wetland-fires','road-transportation','residential-onsite-fuel-usage','non-residential-onsite-fuel-usage'}
fac=[]
for a in ct:
    if a['Sector'] in LAND: continue
    c=a.get('Centroid') or {}
    g=c.get('Geometry') if isinstance(c,dict) else None
    q=sum(x.get('EmissionsQuantity') or 0 for x in a.get('EmissionsSummary',[]) if x.get('Gas') in ('co2','co2e_100yr'))
    if g: fac.append(dict(name=a['Name'],sector=a['Sector'],lon=g[0],lat=g[1],co2_t=q))
json.dump(fac,open('data/ct_facilities.json','w'),indent=1)
for r in rows:
    b=r['bbox']; near=[f for f in fac if b[0]-.08<=f['lon']<=b[2]+.08 and b[1]-.08<=f['lat']<=b[3]+.08]
    near.sort(key=lambda f:-f['co2_t']); r['facilities']=near[:6]
json.dump(dict(national_t=nat,threshold_t=float(T),k50=int(k50),land_km2=int(mask.sum()),
    sector_share={s:grids[s].sum()/nat for s in SECT},coarse_Mt={y:float(coarse[y].sum()/1e6) for y in coarse},hotspots=rows),
    open('out/hotspots.json','w'),indent=1,default=float)
np.save('data/tot1km.npy',tot.astype('f4')); json.dump(dict(W=W,N=N,res=0.01),open('data/tot1km_meta.json','w'))
for k,r in enumerate(rows,1):
    print(f"{k:2d} {r['state']:<12} {r['lat']:.3f},{r['lon']:.3f} {r['emis_t']/1e6:6.2f} Mt {r['share']:5.1%} {r['area_km2']:5d}km2 {r['dominant']:<11} trend {r['trend_Mt'][2005]:.1f}/{r['trend_Mt'][2015]:.1f}/{r['trend_Mt'][2025]:.1f}  | "+'; '.join(f"{f['name'][:28]}({f['sector'][:10]},{f['co2_t']/1e6:.2f})" for f in r['facilities'][:3]))
