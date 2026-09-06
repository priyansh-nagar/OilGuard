"""Test deterministic proximity values through Vite proxy"""
import requests
import math

with open(r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg', 'rb') as f:
    files = {'image': ('test_class1.jpg', f, 'image/jpeg')}
    r = requests.post('http://localhost:5173/api/analyze', files=files)

data = r.json()
SPILL_LAT, SPILL_LON = 18.95, 71.85

for c in data.get('candidates', []):
    lat = c['coordinates']['lat']
    lon = c['coordinates']['lon']
    R = 6371.0
    dLat = (lat - SPILL_LAT) * math.pi / 180
    dLon = (lon - SPILL_LON) * math.pi / 180
    a = math.sin(dLat/2)**2 + math.cos(SPILL_LAT*math.pi/180)*math.cos(lat*math.pi/180)*math.sin(dLon/2)**2
    dist = 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))
    y = math.sin(dLon)*math.cos(lat*math.pi/180)
    x = math.cos(SPILL_LAT*math.pi/180)*math.sin(lat*math.pi/180) - math.sin(SPILL_LAT*math.pi/180)*math.cos(lat*math.pi/180)*math.cos(dLon)
    bearing = (math.atan2(y,x)*180/math.pi + 360) % 360
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    direction = dirs[round(bearing/45)%8]
    print(f'{c["name"]}: {dist:.1f} km {direction}')