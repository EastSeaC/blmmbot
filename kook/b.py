import json

import requests

if __name__ == '__main__':
    k = {'player_id': '2.0.0.76561199044372880', 'AttackValue1': 0.0, 'TKValue1': 0.0, 'TKTimes1': 0.0, 'TKPlayerNumbers1': 0.0, 'AttackHorse1': 0, 'TKHorse1': 0, 'KillNum1': 0, 'DeadNum1': 0}

    t = requests.post('http://localhost:14725/UploadMatchData', json.dumps(k))
    print(t.text)
