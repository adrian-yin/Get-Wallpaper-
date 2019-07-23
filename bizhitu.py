#!/usr/bin/python3
##########################################################################
# File Name: bizhitu.py
# Author: Adrian
# mail: adrianyin@yeah.net
# Created Time(UTC): 2019年07月23日 星期二 04时57分20秒
# 爬取zol壁纸图
#########################################################################

import requests
from bs4 import BeautifulSoup
import os
import time
import threading
import re


def get_html(url):
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = requests.get(url, headers = headers)
    r.encoding = "gbk"
    return r.text


def get_pic_lists(html):
    
    soup = BeautifulSoup(html, "html.parser")
    pic_lists = soup.find_all("ul", class_ = "pic-list2")[0].find_all("a", class_ = "pic")
    return pic_lists


def get_pics(pic_lists):
    
    for pic_list in pic_lists:
        pic_list_name = pic_list.find("em").string
        pic_list_link = "http://desk.zol.com.cn" + pic_list.get("href")
        download_pics(pic_list_link, pic_list_name)


def download_pics(link, name):

    html = get_html(link)
    soup = BeautifulSoup(html, "html.parser")
    pics = soup.find_all("li", attrs = {"class": re.compile(r"show\d\d?")})
    
    global group 

    n = 1
    for pic in pics:
        pic_page_link = "http://desk.zol.com.cn" + pic.find("a").get("href")
        html = get_html(pic_page_link)
        soup = BeautifulSoup(html, "html.parser")
        real_page = soup.find("a", id = "1920x1080")
        if real_page is not None:
            real_page_link = "http://desk.zol.com.cn" + real_page.get("href")
        else:
            continue

        html = get_html(real_page_link)
        soup = BeautifulSoup(html, "html.parser")
        pic_link = soup.find("img").get("src")

        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
        r = requests.get(pic_link, headers = headers)

        create_dir("pic/{}/{}".format(group, name))
        with open("pic/{}/{}/{}.jpg".format(group, name, str(n)), "wb") as f:
            f.write(r.content)
            time.sleep(1)

        n = n + 1


def get_page_max_num(url):
    
    url = url + "1000.html"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    page_max_num = int(soup.find("span", class_ = "active").string)
    return page_max_num
            

def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def execute(url):
    html = get_html(url)
    pic_lists = get_pic_lists(html)
    get_pics(pic_lists)


def main():
   
    create_dir("pic")

    global group
    group = input("请输入要爬取的分组（拼音）：")
    create_dir("pic/{}".format(group))
    
    url = "http://desk.zol.com.cn/{}/1920x1080/".format(group)
    queue = [i for i in range(1, get_page_max_num(url))]
    threads = []
    while len(queue) > 0:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < 8 and len(queue) > 0:
            page_num = queue.pop(0)
            url = "http://desk.zol.com.cn/{}/1920x1080/".format(group) + "{}.html".format(page_num)
            thread = threading.Thread(target = execute, args = (url,))
            thread.setDaemon(True)
            thread.start()
            print("{}正在下载第{}页".format(thread.name, page_num))
            threads.append(thread)

if __name__ == "__main__":
    main()
