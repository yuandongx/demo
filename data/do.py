import json

data = {}
with open('schedule_params_00030019_202311011602407094.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    data['zy'] = d['person_config']['自有']
    data['zb'] = d['person_config']['众包']

with open('damand_params_00030019_202311011602407094json', 'r', encoding='utf-8') as f:
    dd = json.load(f)
    data.update(dd)

with open('demo.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
