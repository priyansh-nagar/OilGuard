"""Test explanation text through Vite proxy"""
import requests

with open(r'C:\Users\amit nagar\Projects\oilguard\data\CSIRO\S1SAR_UnBalanced_400by400_Class_1\1\0_0_0_img_0bBRglmdLdC6cFxF_JAV_cls_1.jpg', 'rb') as f:
    files = {'image': ('test_class1.jpg', f, 'image/jpeg')}
    r = requests.post('http://localhost:5173/api/analyze', files=files)

data = r.json()
for c in data.get('candidates', []):
    print(f'=== {c["name"]} ===')
    print(c['explanation'])
    print()