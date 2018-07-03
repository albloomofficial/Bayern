import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

import multiprocessing
from multiprocessing import Pool, cpu_count
import os
import sys
from time import time
from datetime import timedelta

#Making the original list of links to each individual day on the calender
def search_years():
    result = requests.get("http://digipress-beta.digitale-sammlungen.de/de/fs1/calendar-all/select.html")
    homepage = result.content
    soup = BeautifulSoup(homepage, "html.parser")
    samples = soup.find_all("td", "selected")
    alevels = [sample.a for sample in samples[0:108]]
    links = [["http://digipress-beta.digitale-sammlungen.de/{}".format(alevel.attrs['href']) for alevel in alevels],[alevel.text for alevel in alevels]]
    links = [[links[0][i], links[1][i]] for i in range(len(links[0]))]
    return links

def search_months(link):
    result = requests.get(link)
    second_page = result.content
    soup = BeautifulSoup(second_page, 'html.parser')
    samples = soup.find_all("td", "selected")
    alevels = [sample.a for sample in samples]
    monthly = ["http://digipress-beta.digitale-sammlungen.de/{}".format(alevel.attrs['href']) for alevel in alevels]
    return monthly

def search_days(month, year):
    relevant_links = [[day for day in month], [year for day in month]]
    relevant_links = [[relevant_links[0][i], relevant_links[1][i]] for i in range(len(relevant_links[0]))]
    return relevant_links

def csv_generator(link):
    name = f'driver {str(multiprocessing.current_process().name.split("-")[1])}'
    year = link[1]
    month = search_months(link[0])
    days = search_days(month, year)
    df = pd.DataFrame(days)
    print('{}: working on {}'.format(name,year))
    df.to_csv(f'{year}.csv', index=False, header=None)

#Creating a list of all newspapers from the links to each individual day on the calender
def get_newspapers(csv_file):
    name = f'driver {str(multiprocessing.current_process().name.split("-")[1])}'
    print('{}: working on {}'.format(name, csv_file))
    df = pd.read_csv(csv_file, header=None)
    list_of_values = df.values.tolist()
    for row in list_of_values:
        result = requests.get(row[0])
        third_page = result.content
        soup = BeautifulSoup(third_page, "html.parser")
        samples = soup.find_all("div", "thumbnail")
        alevels = [sample.a for sample in samples]
        newspapers = ["http://digipress-beta.digitale-sammlungen.de/{}{}".format(alevel.attrs['href'], "?zoom=1.5") for alevel in alevels]
        for newspaper in newspapers:
            with open("all_newspapers_{}".format(csv_file), 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([newspaper])
    print('{}: done with {}'.format(name, csv_file))

def merge_all_newspapers():
    csv_file_list = []
    for csv_file in os.listdir('.'):
        if csv_file.startswith('all_newspapers') == False:
            os.remove(csv_file)
        if csv_file.startswith('all_newspapers') == True:
                df = pd.read_csv(csv_file,
                index_col=None,
                header=None)
                csv_file_list.append(df)
                os.remove(csv_file)
    frame = pd.concat(csv_file_list)
    frame.to_csv('all_newspapers_bayern.csv', header=None, index=False)

def img_search(link):
    try:
        name = f'driver {str(multiprocessing.current_process().name.split("-")[1])}'
        name = name.replace(' ','')
        page = 1
        result = requests.get(link)
        homepage = result.content
        soup = BeautifulSoup(homepage, "html.parser")
        next_buttons = soup.find("div", "blaetternNav")
        header = soup.find("h1")
        next_page_header = header
        href_links = next_buttons.find_all("a")[1::]
        while_text = [href_link.text for href_link in href_links]
        while_link = ["http://digipress-beta.digitale-sammlungen.de{}".format(href_link.attrs['href']) for href_link in href_links]
        dictionary = dict(zip(while_text, while_link))
        image_file = soup.find("img")
        final_link = "http://digipress-beta.digitale-sammlungen.de{}".format(image_file.attrs['src'])
        issue = header.text.split("|")[0]
        date = header.text.split("|")[1]

        with open("bayer_img_links_{}.csv".format(name), 'a') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow([final_link, issue, date, page, link])
            myfile.close()

        while next_page_header == header and "+1" in dictionary:
            page += 1
            results = requests.get(dictionary.get("+1"))
            homepage = results.content
            soup = BeautifulSoup(homepage, "html.parser")
            next_buttons = soup.find("div", "blaetternNav")
            next_page_header = soup.find("h1")
            href_links = next_buttons.find_all("a")[1::]
            while_text = [href_link.text for href_link in href_links]
            while_link = ["http://digipress-beta.digitale-sammlungen.de{}".format(href_link.attrs['href']) for href_link in href_links]
            dictionary = dict(zip(while_text, while_link))
            image_file = soup.find("img")
            final_link = "http://digipress-beta.digitale-sammlungen.de{}".format(image_file.attrs['src'])
            issue = header.text.split("|")[0]
            date = header.text.split("|")[1]


            with open("bayer_img_links_{}.csv".format(name), 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow([final_link, issue, date, page, link])
                myfile.close()
        # print('{}: finished a newspaper'.format(str(name.split(' ')[1])))
    except AttributeError as error:
        print('{}: Attribute error moving to next newspaper'.format(name))



#Running the script
if __name__ == '__main__':
    # list_of_links = search_years()
    # with Pool(cpu_count()-1) as p:
    #     p.map(csv_generator, [link for link in list_of_links])
    # p.close()
    # p.join()
    #
    #
    # with Pool(cpu_count()-1) as p:
    #     p.map(get_newspapers, [csv_file for csv_file in os.listdir('.') if csv_file.endswith('.csv')])
    # p.close()
    # p.join()
    #
    # merge_all_newspapers()

    start_time = time()

    df = pd.read_csv('all_newspapers_bayern.csv', header=None)
    list_of_links = df.values.tolist()
    procs = [row[0] for row in list_of_links]
    for i in range(cpu_count()-1):
        with open("bayer_img_links_driver{}.csv".format(str(i+1)), 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            myfile.close()
    with Pool(cpu_count()-1) as p:
        for i, _ in enumerate(p.imap_unordered(img_search, procs, chunksize = 10), 1):
            end_time = time()
            elapsed_time = end_time - start_time
            sys.stderr.write

            completed = str(
            round(
            (i/len(procs)*100),2)
            )

            print('\rdone {}% in {}'.format(completed,
            str(timedelta(seconds=elapsed_time))))

    p.close()
    p.join()










#
    # with open('all_newspapers_bayern.csv', 'r') as f:
    #     reader = csv.reader(f)
    #     your_list = list(reader)
    #
    # with open("bayer_img_links.csv", 'a') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    #     wr.writerow(['link', 'issue','date', 'page', 'first page link'])
    #
    # newspaper_links = [i for x in your_list for i in x]
    # # print(newspaper_links)
    # for i in your_list:
    #     print(i[0])
#
# for i in newspaper_links:
#     page = 1
#     result = requests.get(i)
#     homepage = result.content
#     soup = BeautifulSoup(homepage, "html.parser")
#     next_buttons = soup.find("div", "blaetternNav")
#     header = soup.find("h1")
#     next_page_header = header
#     href_links = next_buttons.find_all("a")[1::]
#     while_text = [href_link.text for href_link in href_links]
#     while_link = ["http://digipress-beta.digitale-sammlungen.de{}".format(href_link.attrs['href']) for href_link in href_links]
#     dictionary = dict(zip(while_text, while_link))
#     image_file = soup.find("img")
#     final_link = "http://digipress-beta.digitale-sammlungen.de{}".format(image_file.attrs['src'])
#     issue = header.text.split("|")[0]
#     date = header.text.split("|")[1]
#
#     with open("bayer_img_links.csv", 'a') as myfile:
#         wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#         wr.writerow([final_link, issue, date, page, i])
#
#     while next_page_header == header and "+1" in dictionary:
#         page += 1
#         results = requests.get(dictionary.get("+1"))
#         homepage = results.content
#         soup = BeautifulSoup(homepage, "html.parser")
#         next_buttons = soup.find("div", "blaetternNav")
#         next_page_header = soup.find("h1")
#         href_links = next_buttons.find_all("a")[1::]
#         while_text = [href_link.text for href_link in href_links]
#         while_link = ["http://digipress-beta.digitale-sammlungen.de{}".format(href_link.attrs['href']) for href_link in href_links]
#         dictionary = dict(zip(while_text, while_link))
#         image_file = soup.find("img")
#         final_link = "http://digipress-beta.digitale-sammlungen.de{}".format(image_file.attrs['src'])
#         issue = header.text.split("|")[0]
#         date = header.text.split("|")[1]
#
#
#         with open("bayer_img_links.csv", 'a') as myfile:
#             wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#             wr.writerow([final_link, issue, date, page, i])
