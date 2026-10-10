import subprocess, glob, os, sys, time
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; R=sys.argv[1]
for i,f in enumerate(sorted(glob.glob(f'{R}/[0-9]*.html'))):
    out=f'{R}/png/'+os.path.basename(f)[:-5]+'.png'
    p=subprocess.Popen([C,'--headless=new','--disable-gpu','--hide-scrollbars',f'--user-data-dir={R}/chrome-prof{i}','--force-device-scale-factor=1','--window-size=1920,1080','--virtual-time-budget=8000','--allow-file-access-from-files',f'--screenshot={out}','file://'+f],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    t=time.time()
    while time.time()-t<40:
        if os.path.exists(out) and os.path.getsize(out)>0: time.sleep(1); break
        time.sleep(0.5)
    p.kill(); p.wait()
    print(os.path.basename(out), os.path.exists(out), flush=True)
