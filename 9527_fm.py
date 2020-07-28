from __future__ import print_function

import json
import logging
import ssl
import requests
from lxml import etree
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http
# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

logging.getLogger('googleapicliet.discovery_cache').setLevel("WARNING")
SCOPES = 'https://www.googleapis.com/auth/drive'  # 设置Google权限API范围
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))
sheet_service = build('sheets', 'v4', http=creds.authorize(Http()))

sheet_id = '1ggThOJ7dq6CrWOsdch5FFT_iUVqVfMpC1O3JX0vnLDw'  # sheet表格ID
sheet_name = 'movie'
range_name = ('{}!A2:D'.format(sheet_name))


def set_values(values):
    set_values = [values]
    body = {'values': set_values, 'majorDimension': 'ROWS'}
    sheet_service.spreadsheets().values().append(spreadsheetId=sheet_id, range=range_name, valueInputOption="RAW",
                                                 insertDataOption="INSERT_ROWS", body=body).execute()


def my_requests(url):
    try:
        response = requests.get(url, verify=False)
    except:
        print("网络请求异常，正在重试！")
        response = requests.get(url, verify=False)
    response.encoding = 'gb2312'
    selector = etree.HTML(response.text)
    return selector


def write_to_file(content):
    with open(path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False))


def get_info(url, num):
    print('开始处理网页：', url)
    host = 'https://www.9527.fm'
    html_sel = my_requests(url)
    html = html_sel.xpath('/html/body/div[3]/div/div[4]/div[1]/div/div/ul/li/a/@href')
    values = []
    # 判断是否有播放源
    if len(html) != 0:
        html = html_sel.xpath('/html/body/div[3]/div/div[4]/div[1]/div/div/ul/li/a/@href')
        title = html_sel.xpath('/html/body/div[3]/div/div[1]/div[2]/ul/li[1]/h1/text()')[0]
        logo = html_sel.xpath('/html/body/div[3]/div/div[1]/div[1]/img/@src')[0]
        # m3u_num = html_sel.xpath('/html/body/div[3]/div/div[4]/div[1]/div/div/ul/li/a/text()')
        # m3u_html = host + html[0]
        # m3u_sel = my_requests(m3u_html)
        # m3u_url = m3u_sel.xpath('//*/div/video/source/@src')[0]
        # m3u_name = m3u_sel.xpath('//*/div[@class="movie_play"]/ul/li/a/text()')[0]
        #dic = {"name": title,"logo": logo, "url": m3u_url,"urls": {m3u_name: m3u_url}}
        # if len(m3u_num) == 1:
            #write_to_file(dic)
        # elif len(m3u_num) > 1:
        #     urls = {}
        urls = ""
        for i in range(len(html)):
                m3u_html = host + html[i]
                m3u_sel = my_requests(m3u_html)
                m3u_url = m3u_sel.xpath('//*/div/video/source/@src')[0]
                m3u_name = m3u_sel.xpath('//*/div[@class="movie_play"]/ul/li/a/text()')[i]
                url = '{}#{}'.format(m3u_name, m3u_url)
                urls+='{}&'.format(url)
                # urls[m3u_name] = m3u_url
            # dic['urls'] = urls
            # write_to_file(dic)
        # with open(path, 'a+') as f:
        #     f.write(',' + '\n')
        values.append(num)
        values.append(title)
        values.append(logo)
        values.append(urls)
        set_values(values)
    else:
        print('当前页面无播放地址！')


path = '1.txt'

for i in range(25000, 55755):
    url = 'https://www.9527.fm/movie/{}.html'.format(i)
    get_info(url, num=i)
