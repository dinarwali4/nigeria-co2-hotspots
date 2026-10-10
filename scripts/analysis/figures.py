import json, numpy as np, geopandas as gpd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
H=json.load(open('data/hotspots_final.json')); fl=json.load(open('data/flare_pixels.json'))
st=gpd.read_file('data/nga_states.geojson'); from shapely.ops import unary_union
st['geometry']=st.geometry.apply(lambda g: unary_union([q for q in getattr(g,'geoms',[g]) if q.geom_type in ('Polygon','MultiPolygon')]))
st=st[~st.geometry.is_empty]; ct=gpd.GeoDataFrame(geometry=[st.union_all().buffer(0.002)],crs=st.crs)
tot=np.load('data/tot1km.npy'); m=json.load(open('data/tot1km_meta.json'))
ramp=['#f2f6fc','#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b']
cmap=LinearSegmentedColormap.from_list('b',ramp); cmap.set_bad('#fcfcfb')
ext=[m['W'],m['W']+tot.shape[1]*0.01,m['N']-tot.shape[0]*0.01,m['N']]
plt.rcParams.update({'font.family':'Helvetica','font.size':10,'text.color':'#0b0b0b'})
def base(ax,xl,yl):
    a=np.where(tot>0,tot,np.nan)
    im=ax.imshow(a,extent=ext,cmap=cmap,norm=LogNorm(100,3e5),interpolation='nearest')
    st.boundary.plot(ax=ax,lw=0.4,color='#8a8984'); ct.boundary.plot(ax=ax,lw=0.9,color='#52514e')
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect('equal')
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(colors='#52514e',labelsize=8); return im
# National
fig,ax=plt.subplots(figsize=(10,8.6),dpi=200); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
im=base(ax,(2.6,14.8),(4.2,14.0))
for lab,c,s in (('2014_15','#e87ba4',6),('2024_25','#eb6834',9)):
    P=np.array([f['geometry']['coordinates'] for f in fl[lab]]); ax.scatter(P[:,0],P[:,1],s=s,c=c,lw=0,zorder=4,label=('Persistent fires (gas flares) 2014–15' if lab=='2014_15' else 'Persistent fires (gas flares) 2024–25'))
for h in H:
    ax.scatter(h['lon'],h['lat'],s=70,facecolor='none',edgecolor='#0b0b0b',lw=1.3,zorder=5)
    dx,dy={'H01':(-.55,.25),'H02':(.15,-.35),'H07':(-.6,0),'H03':(.25,-.12),'H04':(.15,-.32),'H14':(-.15,.27),'H15':(-.55,.2),'H10':(-.6,-.15),'H11':(.15,.12),'H13':(.18,-.1)}.get(h['id'],(.15,.08))
    ax.text(h['lon']+dx,h['lat']+dy,h['id'],fontsize=8.5,weight='bold',zorder=6,color='#0b0b0b',bbox=dict(fc='#fcfcfb',ec='none',alpha=.8,pad=.6))
cb=fig.colorbar(im,ax=ax,shrink=.55,pad=.01); cb.set_label('Fossil CO₂, t / km² / yr (EDGAR 2025, year 2024)',color='#52514e'); cb.outline.set_visible(False)
ax.legend(loc='lower right',frameon=False,fontsize=8.5,markerscale=2)
ax.set_title('Nigeria fossil-CO₂ hotspots',loc='left',fontsize=14,weight='bold',color='#0b0b0b')
fig.tight_layout(); fig.savefig('out/map_national.png',facecolor=fig.get_facecolor(),bbox_inches='tight',pad_inches=0.15)
# Niger Delta flare zoom
fig,ax=plt.subplots(figsize=(10,7),dpi=200); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
base(ax,(4.9,8.2),(4.15,6.4))
for lab,c,s,nm in (('2014_15','#e87ba4',40,'2014–15'),('2024_25','#eb6834',22,'2024–25')):
    P=np.array([f['geometry']['coordinates'] for f in fl[lab]]); D=np.array([f['properties']['days'] for f in fl[lab]])
    ax.scatter(P[:,0],P[:,1],s=D/4,facecolor='none' if lab=='2014_15' else c,edgecolor=c,lw=1.2,zorder=4,label=f'Fire ≥60 of 730 days, {nm} (size = days)')
for h in H:
    if 4.15<h['lat']<6.4 and 4.9<h['lon']<8.2:
        ax.scatter(h['lon'],h['lat'],s=90,facecolor='none',edgecolor='#0b0b0b',lw=1.3,zorder=5); ax.text(h['lon']+.05,h['lat']+.05,h['id'],fontsize=9,weight='bold',zorder=6,bbox=dict(fc='#fcfcfb',ec='none',alpha=.8,pad=.6))
ax.legend(loc='lower left',frameon=False,fontsize=9)
ax.set_title('Niger Delta — gas-flare sites from MODIS fire persistence',loc='left',fontsize=13,weight='bold')
fig.tight_layout(); fig.savefig('out/map_niger_delta_flares.png',facecolor=fig.get_facecolor(),bbox_inches='tight',pad_inches=0.15)
print('ok')
