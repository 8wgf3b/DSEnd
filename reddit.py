import os, shutil
import requests
from utils import zipit, clean, timeformat, utc
import urllib
from sys import argv
import calendar
from datetime import datetime, date

def timeformat(x=datetime.now(), typ='DATE'):
    if type(x) != type(datetime.now()):
        x = datetime(x)
    if typ == 'DATE':
        return x.strftime('%Y-%m-%d')
    elif typ =='HOUR':
        return x.strftime('%H:%M:%S')
    elif typ=='BOTH':
        return x.strftime('%Y-%m-%d')+'%20'+x.strftime('%H:%M:%S')

def utc(x, totimestamp=False):
    if totimestamp == False:
        return timeformat(datetime.utcfromtimestamp(x))
    else:
        d = datetime(*x)
        epoch = datetime(1970,1,1)
        return int((d - epoch).total_seconds())


def zipit(path):
    try:
        shutil.make_archive(path, 'zip', path)
        return path + '.zip'
    except Exception as e:
        print(e)

def clean(path = 'temp/', log = False):
    for file in os.listdir(path):
        if file == '.gitkeep':
            continue
        file_path = os.path.join(path, file)
#        print(file_path)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    if log == True:
        return '\n'.join(os.listdir(path))

def redditusermedia(user):
    address = os.getenv('REDDITAPI', 'https://api.pushshift.io/reddit/search/')
    bigbro = os.getenv('OWNNAME', '')
#    address = 'https://api.pushshift.io/reddit/search/'
#    bigbro = ''
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
                urllib.request.urlretrieve('http://zippy.gfycat.com/' + name, directory+'/'+dic[x].encode('ascii', 'ignore').decode('ascii')+'.mp4')
            else:
                ext = x.split('.')[-1]
                urllib.request.urlretrieve(x, directory +'/' + dic[x].encode('ascii', 'ignore').decode('ascii') + '.' + ext)
        except Exception as e:
            print(x)
            print(e)
            continue
    path = zipit(directory).split('/')[-1]
    shutil.rmtree(directory)
    mainbody = user + '\n\n' + 'ziploc\n' + bigbro + 'temp/' + path + '\n\n'
    return mainbody


if __name__ == '__main__':
    #print(redditusermedia('opiumzxq'))
    for item in argv[1:]:
        print(redditusermedia(item))
    print('\n\nThe zipped files are stored in temp folder')
