import requests
import json
import re
import shutil
import time
import math
import process
import config

def clean_string(string):
    string = re.sub(r'[^A-Za-z0-9 ]+', '', string)
    return string

def lastfm_get(method, data, page=None):
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
    if page is not None:
        payload['page'] = page

    request = requests.get(url, headers=headers, params=payload)
    return request

def itunes_get(term):
    doEntity = False
    # term = clean_string(term)

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

def fix_url(url):
    partOne = re.search(r'(^.*\/)(100x100bb)(.jpg$)', url).group(1)
    partTwo = re.search(r'(^.*\/)(100x100bb)(.jpg$)', url).group(3)
    url = partOne + "100000x100000-999" + partTwo
    return url

def reject_types(result):
    if result['kind'] == 'song':
        return True
    elif result['kind'] == 'collection':
        return True
    elif result['kind'] == 'music-video':
        return False
    else:
        return False

def force_url(iInfo):
    for result in iInfo['results']:
        if reject_types(result):
            return result['artworkUrl100']
        else:
            pass

def get_url(lastAlbums):
    count = 0
    coverURL = []
    for album in lastAlbums['topalbums']['album']:
        # print rank, album title, and artist & generate itunes search terms
        print(album['@attr']['rank'], album['name'], album['artist']['name'])
        search = album['name'] + " " + album['artist']['name']

        # Temporary check to only do the first few entries in the request
        # if str(album['@attr']['rank']) == str(40) or str(album['@attr']['rank']) == str(45):
        if int(count) < int(config.count):
            # Get last.fm album information
            lastInfo = lastfm_get('album.getInfo', album).json()
            # Get iTunes song information
            itunesInfo = itunes_get(search).json()

            # Sometimes no results are returned, make a note of it and continue
            # Unsure if it's best to decrement the counter or not, may be helpful in debugging
            if itunesInfo['resultCount'] == 0:
                print('Error, no results returned -- continuing')
                count -= 1
            else:
                # Iterate over iTunes search results to find matching track number & titles (for additional verification)
                # When a match is found, store the artwork URL in the coverURL list
                pointer = 1
                for result in itunesInfo['results']:
                    # print('Trying result %d/%d' % (pointer, itunesInfo['resultCount']))
                    try:
                        if str(result['trackNumber']) == str(lastInfo['album']['tracks']['track'][0]['@attr']['rank']):
                            if str(result['trackName']) == str(lastInfo['album']['tracks']['track'][0]['name']):
                                print("Match found")
                                coverURL.append(result['artworkUrl100'])
                                break
                        if itunesInfo['resultCount'] == pointer:
                            print('Error, no more entries -- forcing value')
                            coverURL.append(force_url(itunesInfo))
                            break
                    except IndexError:
                        # For some reason, some albums don't return a tracklist on last.fm
                        # As a result, we will resort to matching artist name and album title instead (not perfect)
                        if str(result['artistName']).lower() == str(lastInfo['album']['artist']).lower():
                            if str(result['collectionName']).lower() == str(lastInfo['album']['name']).lower():
                                print("Match found")
                                coverURL.append(result['artworkUrl100'])
                                break
                            if str(result['trackName']).lower() == str(lastInfo['album']['name']).lower():
                                print("Close match found, working with it")
                                coverURL.append(result['artworkUrl100'])
                                break
                        if itunesInfo['resultCount'] == pointer:
                            print('Index Error, no more entries -- forcing value')
                            coverURL.append(force_url(itunesInfo))
                            break
                    except KeyError:
                        # Some entries will show up as singles, not tracks in an album
                        # Skip these usually, unless there are no more results to check or it was the only one
                        if itunesInfo['resultCount'] == pointer:
                            print('Key Error, no more entries -- forcing value')
                            coverURL.append(force_url(itunesInfo))
                            break
                        else:
                            pass
                    except Exception as e:
                        # If all else fails, spit out the error and keep it moving
                        print('---')
                        print('Error:', e)
                        print('---')
                        print(result)
                        print('---')
                        print(lastInfo)

                        # Decrement the counter since we won't be appending
                        count -= 1
                    pointer += 1
            print('---')
        else:
            break
            # pass

        # Temporary counter to limit the amount of API requests during testing
        count += 1

        # Help with the rate limiting, 20/minute
        time.sleep(4)
    return coverURL

def download_covers(coverURL):
    # Putting loop for downloading covers into here
    count = 0
    for url in coverURL:
        url = fix_url(url)
        response = requests.get(url, stream=True)
        fileName = "input/" + str(count) + ".jpg"
        with open(fileName, 'wb') as outFile:
            shutil.copyfileobj(response.raw, outFile)
        del response
        count += 1
    return None

# This is the main functionality of the script

# Set up global variables
pageCount = math.ceil(float(config.count) / 50)
urlList = []

# Verify that the file structure is accurate
process.verify_dirs()

# Populate the urlList with the amount of urls specified in the config file
i=0
while i < pageCount:
    page = i + 1
    lastAlbumList = lastfm_get('user.gettopalbums', config.lastfmUser, page).json()
    urlList.extend(get_url(lastAlbumList))
    i += 1

print('Generated', len(urlList), 'urls.')

# Download all the covers from the urlList
download_covers(urlList)

# Sort the colors
print(process.sort_colors())