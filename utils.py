import os, shutil
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

if __name__ == '__main__':
    print(utc(1546300800))
