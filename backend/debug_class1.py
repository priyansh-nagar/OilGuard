"""Test Class 1 image"""
import requests
import json

image_path = r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg'

with open(image_path, 'rb') as f:
    files = {'image': ('test_class1.jpg', f, 'image/jpeg')}
    r = requests.post('http://127.0.0.1:8000/api/analyze', files=files)

print('Status:', r.status_code)

data = r.json()
spill = data.get('spill', {})
print('detected:', spill.get('detected'))
print('confidence:', spill.get('confidence'))

candidates = data.get('candidates', [])
print('candidates:', len(candidates))

for c in candidates:
    print(f'  {c["name"]}: score={c["attribution_score"]}, spatial={c["spatial_consistency"]}, temporal={c["temporal_consistency"]}, trajectory={c["trajectory_consistency"]}, traj_len={len(c.get("trajectory", []))}')