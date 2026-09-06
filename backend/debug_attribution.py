"""Test the new AIS/attribution implementation"""
import requests
import json

# Test with Class 0 image - use absolute path
image_path = r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_0\0\0_0_0_img_01RNDdyOUhULo97s_SFr_cls_0.jpg'

with open(image_path, 'rb') as f:
    files = {'image': ('test_class0.jpg', f, 'image/jpeg')}
    r = requests.post('http://127.0.0.1:8000/api/analyze', files=files)

print('Status:', r.status_code)

data = r.json()
spill = data.get('spill', {})
print('detected:', spill.get('detected'))
print('confidence:', spill.get('confidence'))
print('spill center:', spill.get('center'))
print('spill timestamp:', spill.get('detection_timestamp'))

candidates = data.get('candidates', [])
print('candidates:', len(candidates))

for c in candidates:
    print(f'  {c["name"]}: score={c["attribution_score"]}, spatial={c["spatial_consistency"]}, temporal={c["temporal_consistency"]}, trajectory={c["trajectory_consistency"]}, traj_len={len(c.get("trajectory", []))}')
    print(f'    timestamp: {c["timestamp"]}')
    print(f'    trajectory first: {c["trajectory"][0] if c.get("trajectory") else "none"}')
    print(f'    trajectory last: {c["trajectory"][-1] if c.get("trajectory") else "none"}')