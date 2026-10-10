"""Write state.kml (camera + optional calibration markers / timestamp) for the NetworkLink."""
import sys, json, math, os
def write(lat, lon, rng, when=None, calib=False):
    ts=f'<gx:TimeStamp><when>{when}</when></gx:TimeStamp>' if when else ''
    marks=''
    if calib:
        d=0.01; s=0.0006
        for i,(a,b) in enumerate([(lat,lon),(lat,lon+d),(lat+d,lon)]):
            marks+=f'<Placemark><Style><PolyStyle><color>ffff00ff</color><outline>0</outline></PolyStyle></Style><Polygon><outerBoundaryIs><LinearRing><coordinates>{b-s},{a-s},0 {b+s},{a-s},0 {b+s},{a+s},0 {b-s},{a+s},0 {b-s},{a-s},0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'state.kml'),'w').write(f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document><name>v {lat} {lon} {when}</name><LookAt>{ts}<longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>0</altitude><heading>0</heading><tilt>0</tilt><range>{rng}</range><altitudeMode>relativeToGround</altitudeMode></LookAt>{marks}</Document></kml>')
if __name__=='__main__':
    a=sys.argv; write(float(a[1]),float(a[2]),float(a[3]),a[4] if len(a)>4 and a[4]!='-' else None, len(a)>5)
