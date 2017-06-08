# The class to cache cookie

def load_cookie(file_path = './cookie'):
    loaded = {}
    f = open(file_path, 'r')
    for line in f.read().split(';'):
        name, value = line.strip().split('=', 1)
        loaded[name] = value
    f.close()
    print 'Load the cookie'
    return loaded
