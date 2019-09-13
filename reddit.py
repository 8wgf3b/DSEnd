import json, os, re, shutil, sys
import requests
from tqdm import tqdm

def download_file(url: str, outputFile: str) -> None:
    with requests.get(url, stream=True) as r:
        with open(outputFile, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def reddit_user_media(user: str) -> None:
    bigbro = os.getenv('OWNNAME', '')
    iteration = 1
    posts = dict()
    while True:
        params = {
            'author': user,
            'fields': ('url', 'title', 'created_utc'),
            'size': 500,
        }
        if iteration > 1:
            params.update({'before': r[-1]['created_utc']})
        r = requests.get('https://api.pushshift.io/reddit/submission/search', params=params).json()['data']
        if len(r) == 0:
            break
        for post in r:
          posts[post['title']] = post['url']
        iteration = iteration + 1

    directory = 'temp/' + user
    if not os.path.exists(directory):
        os.makedirs(directory)

    for (rawTitle, rawUrl) in tqdm(posts.items()):
        urls = dict()
        try:
            title = rawTitle.encode('ascii', 'ignore').decode('ascii').rstrip('.')
            rawExt = rawUrl.split('.')[-1]
            if 'reddit.com' in rawUrl and '/comments/' in rawUrl:
                pass
            elif 'youtube.com' in rawUrl:
                pass
            elif 'gfycat' in rawUrl:
                name =  rawUrl.split('/')[-1]
                g = requests.get('https://api.gfycat.com/v1/gfycats/' + name)
                urls[g.json()['gfyItem']['mp4Url']] = 'mp4'
            elif 'imgur.com/a/' in rawUrl:
                g = requests.get(rawUrl)
                # Imgur API requires auth, however albums embed json in the html
                # to avoid auth restriction.
                j = json.loads(re.findall('(?<=image               : ).*', g.text)[0].rstrip(','))
                c = 1
                for i in j['album_images']['images']:
                    urls['https://i.imgur.com/' + i['hash'] + i['ext']] =  str(c) + i['ext']
                    c = c + 1
            elif 'imgur.com' in rawUrl and 'gifv' in rawUrl:
                # Prevent trying downloading invalid formats, could also download gif
                urls[rawUrl.replace('gifv', 'mp4')] = 'mp4'
            elif rawUrl[-1] == '/':
                continue
            else:
                urls[rawUrl] = rawExt
            for (url, ext) in urls.items():
                if ext.lower() not in ['mp4', 'webm', 'jpg', 'jpeg', 'png', 'gif']:
                    xl = rawUrl.lower()
                    if ext[0].isdigit():
                        ext = ext
                    elif 'mp4' in xl:
                        ext = 'mp4'
                    elif 'webm' in xl:
                        ext = 'webm'
                    elif 'jpg' in xl or 'jpeg' in xl:
                        ext = 'jpg'
                    elif 'png' in xl:
                        ext = 'png'
                    elif 'gif' in xl:
                        ext = 'gif'
                    else:
                        print('FIXME: {}'.format(rawUrl))
                        pass
                download_file(url, directory + '/' + title + '.' + ext)
        except Exception as e:
            print(e)
            continue
    shutil.make_archive(directory, 'zip', directory)
    shutil.rmtree(directory)
    path = directory + '.zip'
    return bigbro + 'temp/' + path

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        reddit_user_media(arg)
