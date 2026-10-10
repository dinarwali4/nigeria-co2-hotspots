import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
P='/Library/Frameworks/Python.framework/Versions/3.13/bin/python3'
ids=sys.argv[1:]
def run(i):
    r=subprocess.run([P,'-W','ignore','scripts/ee_imagery.py',i],capture_output=True,text=True)
    return i, r.returncode, (r.stdout+r.stderr).strip().splitlines()[-1:]
with ThreadPoolExecutor(5) as ex:
    for i,rc,tail in ex.map(run,ids): print(i,rc,tail,flush=True)
