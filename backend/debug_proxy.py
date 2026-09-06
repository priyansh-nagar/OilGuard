"""Test Class 0 image through Vite proxy"""
import requests

with open('C:/Users/amit nagar/Projects/oilguard/data/CSIRO/S1SAR_UnBalanced_400by400_Class_0/0/0_0_0_img_01RNDdyOUhULo97s_SFr_cls_0.jpg', 'rb') as f:
    files = {'image': ('test_class0.jpg', f, 'image/jpeg')}
    r = requests.post('http://localhost:5173/api/analyze', files=files)
    print('Status:', r.status_code)
    data = r.json()
    spill = data.get('spill', {})
    print('detected:', spill.get('detected'))
    print('confidence:', spill.get('confidence'))
    print('Full spill:', spill)