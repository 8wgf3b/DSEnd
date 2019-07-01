import praw
import os
import requests
from utils import zipit, clean, timeformat, utc

def redditusermedia(user):
    address = os.environ['REDDITAPI']
    bigbro = os.environ['OWNNAME']
    user = user.split('/')[-1]
    r = requests.get(address+'submission/?'+'author='+ user +'&fields=url,title,created_utc&size=500')
    js = r.json()['data']
    dummy = []
    while len(js) != 0:
        dummy.extend(js)
        bef = utc(js[-1]['created_utc'])
        r = requests.get(address+'submission/?'+'author=bbypocahontas&fields=url,title,created_utc&size=500&before='+bef)
        js = r.json()['data']
    dic = {x['url']:x['title'] for x in dummy}
    mainbody = ''
    for x in dic:
        mainbody += dic[x] + '\n' + x+ '\n\n'
    directory = 'temp/' + user
    if not os.path.exists(directory):
        os.makedirs(directory)
    for x in dic:
        try:
            if 'gfycat' in x:
                name =  x.split('/')[-1] + '.mp4'
                urllib.request.urlretrieve('http://zippy.gfycat.com/' + name, directory+'/'+dic[x]+'.mp4')
            else:
                ext = x.split('.')[-1]
                urllib.request.urlretrieve(x, directory +'/' + dic[x] + '.' + ext)
        except Exception as e:
            continue
    path = zipit(directory).split('/')[-1]
    mainbody = user + '\n\n' + 'ziploc\n' + bigbro + 'temp/' + path + '\n\n' + mainbody
    return mainbody


if __name__ == '__main__':
    print(redditusermedia('bbypocahontas'))
