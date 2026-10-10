import sys, glob, os, tempfile
from PIL import Image, ImageDraw
tag=sys.argv[1]; fs=sorted(glob.glob(f'raw/*_{tag}.png'))
W,H=560,285
for part in (0,1):
    sub=fs[part*8:(part+1)*8]
    c=Image.new('RGB',(2*W+10,4*(H+10)),'white'); d=ImageDraw.Draw(c)
    for k,f in enumerate(sub):
        im=Image.open(f).convert('RGB').crop((199,250,2740,1541)).resize((W,H))
        x,y=(k%2)*(W+10),(k//2)*(H+10); c.paste(im,(x,y)); d.rectangle((x,y,x+60,y+18),fill='white'); d.text((x+3,y+3),f.split('/')[-1][:3],fill='black')
    c.save(os.path.join(tempfile.gettempdir(),f'sheet_{tag}_{part}.jpg'),quality=85)
# status bars (imagery date) strip
s=Image.new('RGB',(1300,len(fs)*44),'white'); d=ImageDraw.Draw(s)
for k,f in enumerate(fs):
    im=Image.open(f).convert('RGB').crop((1700,1636,2940,1684)); s.paste(im,(60,k*44)); d.text((3,k*44+15),f.split('/')[-1][:3],fill='black')
s.save(os.path.join(tempfile.gettempdir(),f'dates_{tag}.png'))
