import json, re, os, subprocess, sys
SP=sys.argv[1]; D=f'{SP}/project'; R=f'{SP}/render'
blob={'4567c2e5b255cea43f44a08ad7958715':'H01_s2_2025-26','0c09899831e433b7a43b4a197378cf6e':'H02_emb_change_2017-2024','df052ee4ebe681262d2939ab8d87868e':'H02_emb_k8_2024','39f0d3e17240005dbd39ac5085ef605d':'H02_l7_2000-02','d4a82148ddf88e14be177163b56c595a':'H02_s2_2016-17','b819520769ff673e72ec3cbbfcec3b05':'H02_s2_2025-26','9a4915ffad3f2862093449ed550c1e39':'H03_s2_2025-26','ecf5dd82e8eaa90c296fd63f01534e47':'H04_s2_2025-26','92cf8d43c5b2e932eca049ef0095507a':'H05_l7_2000-02','a8d0e406cb7a06cdc2cc87da6763ae95':'H05_s2_2016-17','d87883ed1c7d245cedca8fd4e0fb30cd':'H05_s2_2025-26','d1f6ff81112dfb98f752ac82b42a0ac1':'H06_emb_change_2017-2024','035f79f41a01116b769c750915287638':'H06_l7_2000-02','5aaf555e9ceabe526719f3df07377d7d':'H06_s2_2025-26','345f964ff9c6a83c71802a5639cd3de5':'H07_s2_2025-26','a5bca336a1ee5bff0ad1d69be6069bb7':'H08_s2_2025-26','6c1350cdff31ae2ceb5efca8f972c584':'H10_s2_2025-26','43578f8b9a40698d7aa213c78ab1e925':'H11_l7_2000-02','7dfd332767b1b7d053a4b450836d7fe4':'H11_s2_2025-26','086728ce30597a73f474e1fcbd342b64':'H12_s2_2025-26','d8f34ed0e299d98b84ba52561a4cd276':'H13_l7_2000-02','accbfd3c9fbf42d0bbcf7b23669a3440':'H13_s2_2025-26','c733d5b860bc8e1b2c47693e281d8b3d':'H16_s2_2025-26','f479c68266fa260d532020b4733e5cfb':'map_national','332f63388a940da489279b64304dac13':'map_niger_delta_flares'}
blob.update({'69605a77955ad813b5b7412a12137dfc': 'ge_H01_hist2013', '61e44f77d6a59158cafd89cb203b983e': 'ge_H01_latest', '819af348481d3984322abe4e70593e38': 'ge_H02_hist2013', '2d6dc429e88aed6174309cdbf1a96192': 'ge_H02_latest', '13b114481420d8a47676eb73c6a1faf3': 'ge_H03_hist2013', '94a82df072162c01f5cac2976d145a61': 'ge_H03_latest', 'e9bbc9e6699e1151eaa803af6a5913d2': 'ge_H04_hist2013', '8d9c4cf6f9a795392f1433b7cd1befce': 'ge_H04_latest', '9bf8e417070c5bae05df7f26e3ca506d': 'ge_H05_hist2013', 'd1d7321942dfb91f133e53881fd6a830': 'ge_H05_latest', '6d189252553b139a8d139f4ecd435d54': 'ge_H06_hist2013', 'efd21552b63ee75152f32785759a2ab3': 'ge_H06_latest', '38c10336ad300968b8c9c392098b44cf': 'ge_H07_hist2013', 'c5cec88a4c4a2ba8d997637f95c18f6f': 'ge_H07_latest', 'c1ae168484628a566b17821051740147': 'ge_H08_hist2013', 'c536d325fe9c049aaefa194d0c9472bd': 'ge_H08_latest', 'fd29656b1a94d8af57c6d106d8b58c7e': 'ge_H09_latest', '26cc8b2208ada55c2e16eb8881377ad0': 'ge_H10_hist2013', '94bac5ffa76a423dd52c6490f1f74296': 'ge_H10_latest', '6c935d671620877ff96de07bbda5764c': 'ge_H11_hist2013', '80c01a557a7f3b2d36bd9e1fb63bf68b': 'ge_H11_latest', '871b2d9f24844882f5fa4861fa4a3658': 'ge_H12_hist2013', '3381d2dc9da5b0fb8794069f9d57d75a': 'ge_H12_latest', 'bd2ddbc7ec8bbac8cf65fcfb5389edf8': 'ge_H13_latest', '47a831672c607bcb91647655ed050e13': 'ge_H14_latest', '67517a9c07059bee07ddd29c528dd59c': 'ge_H15_latest', 'fd5aee7ddd6d57451da89ea44f55158a': 'ge_H16_hist2013', '6507247a6a8a9e2f7ba80ddd8ca4cb0c': 'ge_H16_latest'})
ICON={  # simple stroke glyphs standing in for the deck's x-icon set
 'Database':'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
 'Tool':'<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
 'Lightning':'<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 'Search':'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>'}
deck=json.load(open(f'{D}/deck.json'))
fonts='https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap'
notes={}
for i,sid in enumerate(deck['order'],1):
    h=open(f'{D}/slides/{sid}.html').read()
    m=re.search(r'<aside>(.*?)</aside>',h,re.S); notes[sid]=m.group(1).strip() if m else ''
    h=re.sub(r'<aside>.*?</aside>','',h,flags=re.S)
    h=re.sub(r'/_blob/([0-9a-f]{32})',lambda m:f'../assets/{blob[m.group(1)]}.jpg',h)
    def icon(m):
        st=m.group(2); col=re.search(r'color:([^;"]+)',st).group(1)
        return f'<svg viewBox="0 0 24 24" style="width:64px;height:64px;flex:none" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[m.group(1)]}</svg>'
    h=re.sub(r'<x-icon name="(\w+)" style="([^"]*)"></x-icon>',icon,h)
    page=f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts}">
<style>*{{margin:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden}}
section{{width:1920px;height:1080px;position:relative;overflow:hidden}}h1,h2,h3{{font-weight:600}}section>*:not([style*="position:absolute"]){{position:relative}}p,h1,h2,h3{{text-wrap:balance}}</style></head>
<body>{h}<script>document.fonts.ready.then(()=>document.body.dataset.ready=1)</script></body></html>'''
    open(f'{R}/{i:02d}_{sid}.html','w').write(page)
json.dump({'order':deck['order'],'notes':notes},open(f'{R}/notes.json','w'))
print('pages',len(deck['order']))
