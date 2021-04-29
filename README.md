# Last.fm Top Album Color Sorting

## About
This script is aimed squarely at iterating over a users last.fm top albums for the purposes of downloading the cover art (in high quality), then sorting them based on the dominant color. I'm using this to create a color sorted mosaic of album covers. 

(add picture for reference)

## How to Use

The script is relatively easy to use, it shouldn't take too much time to set up. The longest part is waiting for it to complete (damn you rate limits!). The steps to using the script are as follows:

1. [Get a last.fm API key](https://www.last.fm/api/account/create)
2. Put your API key into `config.py`.
    * Ex. `lastfmAPI = 'YOUR_API_KEY'`
3. Add the username that you would like to analyze to `config.py`
    * Ex. `lastfmUser = 'jivandabeast'`
4. Set your desired time period, you can choose any of the options in the comment
    * Ex. `timePeriod = 'overall'`
5. Input the number of covers you want
    * Ex. `count = 200`
6. Install the dependencies
    * `pip install -r requirements.txt`
    * *I recommend using a Python virtual environment for this*
7. Run, and wait.
    * `python3 main.py`

## Credits
I'd like to give a shoutout to [Ben Dodson](https://github.com/bendodson/) for some inspiration on using iTunes for getting high quality versions of the album covers.

I'd also like to give a massive shoutout to [Sam Pom](https://github.com/SamPom100), the code that I use for sorting the albums based on their dominant colors is pretty much entirely from his work. 