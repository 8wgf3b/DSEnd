import os, shutil
import calendar
import time
from datetime import datetime, date
import pyimgur

def utc(x = time.time(), totimestamp=False, format = 'BOTH'):
    if totimestamp == False:
        return timeformat(datetime.utcfromtimestamp(x), format)
    else:
        d = datetime(*x)
        epoch = datetime(1970,1,1)
        return int((d - epoch).total_seconds())

def timeformat(x=datetime.now(), typ='DATE'):
    if type(x) != type(datetime.now()):
        x = datetime(x)
    if typ == 'DATE':
        return x.strftime('%Y-%m-%d')
    elif typ =='HOUR':
        return x.strftime('%H:%M:%S')
    elif typ=='BOTH':
        return x.strftime('%Y-%m-%d')+'%20'+x.strftime('%H:%M:%S')
    else:
        return x.strftime(typ)

def echoimage(URL, file=False):
    im = pyimgur.Imgur(os.environ['IMGUR_CID'])
    #url can be sent directly but i wanted to test the temp directory's usage
    if file == False:
        response = requests.get(URL)
        if response.status_code == 200:
            with open("temp/echoim.jpg", 'wb') as f:
                f.write(response.content)
        uploaded_image = im.upload_image("temp/echoim.jpg", title="twilwhatbot")
    else:
        uploaded_image = im.upload_image(URL, title="twilwhatbot")
    return uploaded_image.link

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

if __name__ == '__main__':
    print(utc(1546300800))
