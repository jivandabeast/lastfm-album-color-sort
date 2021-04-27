import requests
import json
import config

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def lastfm_get(method, data):
    headers = {}
    payload = {}
    url = 'https://ws.audioscrobbler.com/2.0/'

    payload['api_key'] = config.lastfmAPI
    payload['format'] = 'json'
    payload['method'] = method
    if method[:4] == 'user':
        payload['user'] = data
    elif method[:5] == 'album':
        payload['artist'] = data['artist']['name']
        payload['album'] = data['name']

    request = requests.get(url, headers=headers, params=payload)
    return request

def itunes_get(term):
    doEntity = False

    headers={}
    payload={}
    url = 'https://itunes.apple.com/search?'

    payload['term'] = term
    payload['country'] = 'US'
    payload['media'] = 'music'
    if doEntity:
        payload['entity'] = 'album'

    request = requests.get(url, headers=headers, params=payload)
    return request

lastAlbums = lastfm_get('user.gettopalbums', config.lastfmUser).json()
coverURL = []

count = 0
for album in lastAlbums['topalbums']['album']:
    # Temporary counter to limit the amount of API requests during testing
    count += 1
    
    # print rank, album title, and artist & generate itunes search terms
    print(album['@attr']['rank'], album['name'], album['artist']['name'], album['mbid'])
    search = album['name'] + " " + album['artist']['name']

    # Temporary check to only do the first few entries in the request
    if count <= 5:
        # Get last.fm album information
        lastInfo = lastfm_get('album.getInfo', album).json()
        # Get iTunes song information
        itunesInfo = itunes_get(search).json()
        
        # Iterate over iTunes search results to find matching track number & titles (for additional verification)
        # When a match is found, store the artwork URL in the coverURL list
        for result in itunesInfo['results']:
            if str(result['trackNumber']) == str(lastInfo['album']['tracks']['track'][0]['@attr']['rank']):
                if str(result['trackName']) == str(lastInfo['album']['tracks']['track'][0]['name']):
                    print("They're the same")
                    coverURL.append(result['artworkUrl100'])
                    break
    else:
        break

print(coverURL)