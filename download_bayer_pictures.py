import csv
import os
import urllib.request
import os, errno
import pandas as pd
import multiprocessing
from multiprocessing import cpu_count, Pool
from time import sleep

def list_maker(csv_file):
    df = pd.read_csv(csv_file)
    list_of_values = df.values.tolist()
    return list_of_values

def get_images(row):
    #sadly kept getting a typeerror which I will attach in the read me
    name = multiprocessing.current_process().name
    img_link = row[0].strip()
    issue = str(row[1].strip().encode("utf-8").decode("utf-8"))
    print(issue)

    date = row[4].split('.all')[0]
    date = date.split('/')[-1]

    page = str(row[3]).strip()

    try:
        os.makedirs("Bayern_Articles/{}/{}".format(issue,date))
    except OSError as e:
        if e.errno == errno.EEXIST:
            print('{}: same article'.format(name))

    if not os.path.isfile("Bayern_Articles/{}/{}/{}_page{}.jpeg".format(issue,date,date,page)):
        urllib.request.urlretrieve(img_link,"Bayern_Articles/{}/{}/{}_page{}.jpeg".format(issue,date,date,page))
    else:
        print('{}: we already got this file'.format(name))




if __name__ == '__main__':
    for csv_file in os.listdir('.'):
        if csv_file.startswith('bayer_img_links'):
            image_list = list_maker(csv_file)
            iteration_list = [row for row in image_list]
            with Pool(cpu_count()) as p:
                try:
                    p.map(get_images, iteration_list, chunksize = 1000)
                except TypeError:
                    print('pesky TypeError')
                    continue
            p.close()
            p.join()
