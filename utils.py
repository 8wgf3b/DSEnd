import os, shutil
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
    clean()
