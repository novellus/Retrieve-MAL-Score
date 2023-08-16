import os
import requests
import tabulate
import time
import yaml
from collections import defaultdict

# local imports, these files are not commited to the repo
from IDs import IDs  # simple list of strings
import auth  # contains auth for MAL, see usage below


API_BASE = 'https://api.myanimelist.net/v2/anime'
cache_folder = 'cache'

data = []
os.makedirs(cache_folder, exist_ok=True)


# acquire data
for i_ID, ID in enumerate(IDs):
    cache_file = os.path.join(cache_folder, ID)

    # load exisxting cache file if it exists, other wise query the API
    if os.path.exists(cache_file):
        print(f'Using cache for {i_ID+1}/{len(IDs)}')
        f = open(cache_file)
        response = yaml.load(f.read(), Loader=yaml.FullLoader)
        f.close()

    else:
        print(f'Querying API for {i_ID+1}/{len(IDs)}')
        time.sleep(2)  # rate limit API access

        fields = ['title',
                  'mean',
                  'rank',
                  'num_scoring_users',
                 ]

        URL = f'{API_BASE}/{ID}?fields={",".join(fields)}'
        headers = {'X-MAL-CLIENT-ID': auth.Client_ID}

        response = requests.get(URL, headers=headers)
        response = response.json()

        # cache response
        f = open(cache_file, 'w')
        f.write(yaml.dump(response))
        f.close()

    data.append(response)


# process data
# remove incomplete entries (usually haven't aired yet)
_data = []
for r in data:
    if ('mean' in r
        and 'rank' in r
        and 'title' in r
       ):
        _data.append(r)
data = _data

# add URL links
for r in data:
    r['URL'] = f'https://myanimelist.net/anime/{r["id"]}'

data.sort(key = lambda r: (-r['mean'], -r['rank']))


# display data
headers = ['mean', 'rank','title', 'URL']
disp_data = [(r['mean'], r['rank'], r['title'], r['URL']) for r in data]
print(tabulate.tabulate(disp_data, headers=headers, tablefmt="github"))
