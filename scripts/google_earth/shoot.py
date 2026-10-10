import json, sys, time, subprocess, os
import numpy as np
from PIL import Image
sys.path.insert(0,'.'); from cam import write
V=json.load(open('views.json')); when=sys.argv[1]; tag=sys.argv[2]; ids=sys.argv[3:] or list(V)
os.makedirs('raw',exist_ok=True); import tempfile; tmp=os.path.join(tempfile.gettempdir(),'_ge.png')
WIN=os.environ.get('EARTH_WINDOW_ID','')  # Earth Pro CGWindowID (e.g. from an AppleScript/Quartz window list)
def grab(p):
    for _ in range(60):
        if os.path.exists(p): os.remove(p)
        subprocess.run(['screencapture','-x','-o','-l',WIN,p],capture_output=True)
        if os.path.exists(p) and os.path.getsize(p)>0: return
        print('  capture failed (screen locked?) - retrying', flush=True); time.sleep(10)
    raise SystemExit('capture kept failing')
def small(p): return np.asarray(Image.open(p).convert('L').crop((199,250,2740,1541)).resize((254,129)),dtype=float)
for i in ids:
    lat,lon,r=V[i]; write(lat,lon,r,when)
    t0=time.time(); prev=None; stable=0
    time.sleep(8)
    while time.time()-t0<120:
        grab(tmp); cur=small(tmp)
        if prev is not None:
            d=np.abs(cur-prev).mean()
            stable = stable+1 if d<0.6 else 0
            if stable>=2: break
        prev=cur; time.sleep(4)
    os.replace(tmp,f'raw/{i}_{tag}.png')
    print(i, round(time.time()-t0), 'settled' if stable>=2 else 'TIMEOUT', flush=True)
