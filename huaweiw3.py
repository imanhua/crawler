import random
import time
import os
import requests
from bs4 import BeautifulSoup as BS
import configparser
from PIL import Image  # 打开图片
import re
import json

import sys


def loginw3(redirect_url, configuration):
    # print(configuration['password'],configuration['user_name'])
    login_url = 'https://login.huawei.com/login/login.do'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    param = {'actionFlag': 'loginAuthenticate',
             'lang': 'en',
             'loginMethod': 'login',
             'loginPageType': 'mix',
             'password': configuration['password'],
             'redirect': 'http://3ms.huawei.com/hi/home?3ms_type=menu',
             'redirect_local': '',
             'uid': configuration['user_name']}

    r = requests.post(login_url, headers=headers, params=param)  # 登录, 获取cookie
    print(r.status_code)  # 返回状态值

    s = requests.get(redirect_url, cookies=r.cookies)  # 访问目标网页
    # print(s.status_code, s.content)  # 打印返回状态码和内容

    soup = BS(s.content, 'html.parser')
    return soup, r.cookies


def get_pic(url_index, url, cookie):

    detail_info = requests.get(url, cookies=cookie)
    soup = BS(detail_info.content, 'html.parser')
    pic_all = soup.find_all('div', class_='img_resize')
    url_index = str(url_index)

    if len(pic_all) > 0:
        v_pic_name = url_index + '.jpg'
        pic_num = 0
        # v_pic_name = url_index + '_' + pic_num + '.jpg'

        for item in pic_all:
            # pic_links = item.find_all('a', href=True, title=True)
            pic_links = item.find_all('img', class_='imgShow')
            pictures = pic_links[0]['data-ks-lazyload']
            print('')
            # print(pic_links)
            print(pictures)
            # pic_download = requests.get(pic_links[0]['href'], cookies=cookie)
            pic_download = requests.get(pictures)

            # download pictures
            with open(v_pic_name, 'wb') as file:
                file.write(pic_download.content)
            pic_num += 1
            v_pic_name = url_index + '_' + str(pic_num) + '.jpg'
            print('%s downloaded' %(v_pic_name))

    # wait = input('按任意键继续')
    # print(wait)
    # print(pic_all)


def reg_expression(folder_num, html_info,cookies):

    v_path = 'pic/' + str(folder_num)
    v_link_file = v_path + '/links.txt'
    v_tmp_file = ''
    v_link_index = 1

    if os.path.exists(v_path):
        pass
    else:
        print('not exists')
        os.mkdir(v_path, mode=0o777)

    if os.path.exists(v_link_file):
        os.remove(v_link_file)

    html_links = html_info.find_all('div', class_='title')  # find links

    for items in html_links:
        # print(items)
        # write into file every 3 records

        if items.find('img', src=True):
            link_title = items.find_all('a', href=True)
            link = link_title[0]['href']
            title = link_title[0].string

            v_tmp_file += str(v_link_index) + ' ' + link + '\n'
            print(title)
            print(link)

            get_pic(v_path + '/' + str(v_link_index), link, cookies)

            if v_link_index % 3 == 0:
                with open(v_link_file, 'a') as file:
                    file.write(v_tmp_file)
                file.close()
                v_tmp_file = ''

            v_link_index += 1
            time.sleep(2)

    with open(v_link_file, 'a') as file:
        file.write(v_tmp_file)
    file.close()

    # return html_links


def read_config(config_file):
    configs = {}
    cf = configparser.ConfigParser()
    cf.read(config_file)
    configs['user_name'] = cf.get('info', 'user_name')
    configs['password'] = cf.get('info', 'password')
    configs['start_page'] = cf.get('settings', 'start_page')
    configs['end_page'] = cf.get('settings', 'end_page')
    # print(configs)
    return configs


def main():

    if __name__ == '__main__':

        v_config_file = 'config.ini'

        configuration = read_config(v_config_file)
        start_page = int(configuration['start_page'])
        end_page = int(configuration['end_page']) + 1

        for i in range(start_page, end_page):

            folder_num = i
            redirect_url = "http://xinsheng.huawei.com/cn/index.php?app=forum&mod=List&act=index&class=919&cate=44"

            if i == 1:
                pass
            else:
                redirect_url = redirect_url + '&p=' + str(i)

            # log to w3 and get cookies
            html_info, cookies = loginw3(redirect_url, configuration)
            # redirect_page = i
            reg_expression(folder_num, html_info, cookies)


main()