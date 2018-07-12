
#Issues
```
Traceback (most recent call last):
  File "download_bayer_pictures.py", line 43, in <module>
    p.map(get_images, iteration_list, chunksize = 1000)
  File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/pool.py", line 260, in map
    return self._map_async(func, iterable, mapstar, chunksize).get()
  File "/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/multiprocessing/pool.py", line 608, in get
    raise self._value
multiprocessing.pool.MaybeEncodingError: Error sending result: '<multiprocessing.pool.ExceptionWithTraceback object at 0x109a0df98>'. Reason: 'TypeError("cannot serialize '_io.BufferedReader' object",)'
```

Most likely has something to do with the multiprocessing module. I don't
fully understand what the problem is but I think it's having problems passing
information between the processes and the pool. This needs looking into but
for now I sort of did an inelegant workaround with a try function
