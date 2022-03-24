def DeleteCache():
    import os.path
    mypath = "cache"
    for root, dirs, files in os.walk(mypath):
        for file in files:
            os.remove(os.path.join(root, file))
