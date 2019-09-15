import json, os, re, shutil, sys
import requests
from tqdm import tqdm
from collections import defaultdict, OrderedDict
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import utc, timeformat, echoimage, clean

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

def userplotwithparam(saveloc='temp/lol.jpg'):
    def userplot(func):
        def inner(user, d = 30):
            bigbro = os.getenv('OWNNAME', '')

            table, df = func(user, d)
            fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(10,10))

            SMALL_SIZE = 6
            MEDIUM_SIZE = 8
            BIGGER_SIZE = 10

            plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
            plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
            plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
            plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
            plt.rc('figure', titlesize=MEDIUM_SIZE)
            df.sort_values(['subscore'],ascending = False).head(10)[['subscore']].plot.barh(legend = False, ax = axes[0,0])
            axes[0,0].set_title('total posts score')
            df.sort_values(['comscore'],ascending = False).head(10)[['comscore']].plot.barh(legend = False, ax = axes[0,1])
            axes[0,1].set_title('total comments score')

            df.sort_values(['subcount'],ascending = False).head(10)[['subcount']].plot.barh(legend = False, ax = axes[1,0])
            axes[1,0].set_title('total posts count')
            df.sort_values(['comcount'],ascending = False).head(10)[['comcount']].plot.barh(legend = False, ax = axes[1,1])
            axes[1,1].set_title('total comments count')

            df.sort_values(['recentsub'],ascending = False).head(10)[['recentsub']].plot.barh(legend = False, ax = axes[2,0])
            axes[2,0].set_title('last ' + str(d) + ' days posts count')
            df.sort_values(['recentcom'],ascending = False).head(10)[['recentcom']].plot.barh(legend = False, ax = axes[2,1])
            axes[2,1].set_title('last ' + str(d) + ' days comments count')

            sns.heatmap(table, cmap = sns.cm.rocket_r, ax = axes[3, 0])
            axes[3, 0].set_title('last ' + str(d) + ' days activity')

            plt.tight_layout()
            plt.savefig(saveloc, dpi = 100)
            return bigbro + saveloc, str(sum(df['subscore'])), str(sum(df['comscore']))
        return inner
    return userplot


@userplotwithparam('temp/spam.png')
def useranalysis(user, trend = 30):
    user = user.split('/')[-1]
    address = 'https://api.pushshift.io//reddit/search/'

   # r = requests.get(address+'submission/?'+'author='+ user)
    r = requests.get(address+'submission/?'+'author='+ user +'&fields=subreddit,score,created_utc&size=500')
    js = r.json()['data']
    dummy = []
    score = defaultdict(lambda : [0, 0])
    count = defaultdict(lambda : [0, 0])
    thirty = defaultdict(lambda : [0, 0])
    rawdf = defaultdict(lambda : [0, 0, 0, 0, 0, 0])
    while len(js) != 0:
        dummy.extend(js)
        bef = utc(js[-1]['created_utc'])
        r = requests.get(address+'submission/?'+'author='+user+'&fields=subreddit,score,created_utc&size=500&before='+bef)
        js = r.json()['data']
    for x in dummy:
        rawdf[x['subreddit']][0] += x['score']
    r = requests.get(address+'submission/?'+'author='+ user +'&aggs=subreddit&size=0')
    cs = r.json()['aggs']['subreddit']
    for x in cs:
        rawdf[x['key']][2] = x['doc_count']
    r = requests.get(address+'comment/?'+'author='+ user +'&aggs=subreddit:score:sum&size=0')
    cs = r.json()['aggs']['author:score']
    for x in cs:
        rawdf[x['key']][3] = x['doc_count']
        rawdf[x['key']][1] = int(x['score'])
    r = requests.get(address+'comment/?'+'author='+ user +'&aggs=subreddit&size=0&after='+str(trend)+'d')
    cs = r.json()['aggs']['subreddit']
    for x in cs:
        rawdf[x['key']][5] = x['doc_count']
    r = requests.get(address+'submission/?'+'author='+ user +'&aggs=subreddit&size=0&after='+str(trend)+'d')
    cs = r.json()['aggs']['subreddit']
    for x in cs:
        rawdf[x['key']][4] = x['doc_count']
    l = list(rawdf.items())
    columns = ['subscore', 'comscore', 'subcount', 'comcount', 'recentsub', 'recentcom']
    r = requests.get(address+'submission/?'+'author='+ user +'&aggs=created_utc&size=0&frequency=hour&after='+str(trend)+'d')
    cs = r.json()['aggs']['created_utc']
    m = defaultdict(lambda : 0)
    for item in cs:
        m[utc(item['key'], format = '%m-%d %H')] += item['doc_count']
    r = requests.get(address+'comment/?'+'author='+ user +'&aggs=created_utc&size=0&frequency=hour&after='+str(trend)+'d')
    cs = r.json()['aggs']['created_utc']
    for item in cs:
        m[utc(item['key'], format = '%m-%d %H')] += item['doc_count']
    my_df  = pd.DataFrame(columns = ['date', 'hour', 'hits'])
    for item in m.items():
        v = item[0].split()
        my_df.loc[len(my_df)] = [v[0], v[1], item[1]]
    table = pd.pivot_table(my_df, values = 'hits', aggfunc = np.sum, columns = ['date'], index = ['hour'])
    table = table.fillna(0)
    return table, pd.DataFrame([x[1] for x in l], index = [x[0] for x in l], columns = columns)

def subplotwithparam(saveloc='temp/lol.jpg'):
    def userplot(func):
        def inner(user, d = 30):
            bigbro = os.getenv('OWNNAME', '')

            rdf, table, rank = func(user, d)
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,5))

            SMALL_SIZE = 6
            MEDIUM_SIZE = 8
            BIGGER_SIZE = 10

            plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
            plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
            plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
            plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
            plt.rc('figure', titlesize=MEDIUM_SIZE)
            rdf.plot.barh(legend = False, ax = axes[0], x='subreddit')
            axes[0].set_title('trending subs by karma in last hour')

            sns.heatmap(table, cmap = sns.cm.rocket_r, ax = axes[1])
            axes[1].set_title('last ' + str(d) + ' days activity')

            plt.tight_layout()
            plt.savefig(saveloc, dpi = 100)
            return bigbro + saveloc, rank
        return inner
    return userplot

@subplotwithparam('temp/spam.png')
def subredditanalysis(sub, d = 30):
    sub = sub.lower()
    r = requests.get('https://api.pushshift.io/reddit/comment/search/?aggs=subreddit:score:sum&after=1h&agg_size=2000&size=0')
    cs = r.json()['aggs']['author:score']
    m = []
    for i in range(10):
        m.append((cs[i]['key'].lower(), cs[i]['score']))
    rdf = pd.DataFrame(m, columns =['subreddit', 'karma'])
    rank = -1
    for ind, item in enumerate(cs):
        if sub == item['key'].lower():
            rank = ind + 1
    if rank == -1:
        rank = '>2000'
    rank = str(rank)
    r = requests.get('https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub + '&aggs=created_utc&size=0&frequency=hour&after=' + str(d) + 'd')
    cs = r.json()['aggs']['created_utc']
    m = defaultdict(lambda : 0)
    for item in cs:
        m[utc(item['key'], format = '%m-%d %H')] += item['doc_count']
    r = requests.get('https://api.pushshift.io/reddit/search/comment/?subreddit=' + sub + '&aggs=created_utc&size=0&frequency=hour&after=' + str(d) + 'd')
    cs = r.json()['aggs']['created_utc']
    for item in cs:
        m[utc(item['key'], format = '%m-%d %H')] += item['doc_count']
    my_df  = pd.DataFrame(columns = ['date', 'hour', 'hits'])
    for item in m.items():
        v = item[0].split()
        my_df.loc[len(my_df)] = [v[0], v[1], item[1]]
    table = pd.pivot_table(my_df, values = 'hits', aggfunc = np.sum, columns = ['date'], index = ['hour'])
    table = table.fillna(0)
    return rdf, table, rank

if __name__ == '__main__':
    #_, rank = subredditanalysis('aww')
    a, b, c = useranalysis('achelois17', 14)
    #print(rank)
