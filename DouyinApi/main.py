import requests
import json
import re
import os
import sys
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}


# 下载类
class Download(object):
    """docstring for Download"""

    def __init__(self, path, info):
        super(Download, self).__init__()
        self.path = path
        self.FileInfo = info
        # 对文件和路径名进行校验--在用户api中会出错，因为里面拼接了用户文件夹的路径，这里不能用来校验路径，参见210行
        waring = ['\\', '/', ":", '*', '?', "\"", '<', '>', '|']
        self.Dict = {}
        for fname in self.FileInfo:
            fkey = fname
            for i in waring:
                fname = fname.replace(i, '')
            # 对路径的校验
            # self.path = self.path.replace(i, '')
            self.Dict.update({fname: self.FileInfo[fkey]})
        self.FileInfo = self.Dict

    def mkdir(self, path):
        folder = os.path.exists(path)
        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径

    def downloadFile(self):
        self.mkdir('File/%s' % self.path)
        for fname in self.FileInfo:
            r = requests.get(self.FileInfo[fname], headers=headers)
            newpath = 'File/%s' % self.path + '/%s' % fname
            fileSize = r.headers['Content-Length']
            print('文件大小：%.2fMB' % (int(fileSize) / 1048576))
            with open(newpath, 'wb') as f:
                f.write(r.content)
            f.close
            print('下载完成')


# Api类
class viApi:
    """docstring for viApi"""
    """获取下载地址"""

    def __init__(self, url):
        super(viApi, self).__init__()
        self.FileNames = set()
        self.FileInfo = {}
        self.FilePath = ''
        self.downPath = ''
        self.url = url

    # self.urlType = urlType
    # self.userEnd = False

    # 下载视频和相册
    def video_imagesAPI(self, url, downPath):
        itemApi = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
        regex = r"/video/([\d]*)[/|?]"
        matches = re.search(regex, url)  # 获取视频id，拼接api
        match = matches.group(1)
        itemApi = itemApi + match
        # print(itemApi)
        # 访问api获取数据
        # html = requests.get(itemApi, headers=headers).content.decode('unicode_escape').encode('latin1').decode()
        html = requests.get(itemApi, headers=headers).content
        jsondata = json.loads(html)
        aweme_type = jsondata['item_list'][0]['aweme_type']

        if aweme_type == 2:
            images = jsondata['item_list'][0]['images']  # 相册地址
            fname = jsondata['item_list'][0]['desc']
            for num in range(len(images)):
                fn = fname + str(num + 1) + '.jpg'
                self.FileNames.add(fn)
            n = 0
            for image in images:
                # print(image['url_list'][0])
                fn = fname + '_' + str(n + 1) + '.jpg'
                self.FileInfo.update({fn: image['url_list'][0]})
                n += 1
            musicName = jsondata['item_list'][0]['music']['title'] + '-' + jsondata['item_list'][0]['music'][
                'author'] + '.mp3'
            musicUrl = jsondata['item_list'][0]['music']['play_url']['url_list'][0]
            self.FileInfo.update({musicName: musicUrl})
            self.FilePath = downPath + '%s' % fname

        elif aweme_type == 4:
            fileUrl = jsondata['item_list'][0]['video']['play_addr']['url_list'][0]  # 视频地址
            fileUrl = fileUrl.replace('/playwm/', '/play/')  # 去掉水印
            # 如果是空文案，用时间戳
            if jsondata['item_list'][0]['desc'] == '':
                fileName = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.mp4'
            else:
                fileName = jsondata['item_list'][0]['desc'] + '.mp4'
            self.FileNames.add(fileName)
            self.FileInfo = {fileName: fileUrl}
            self.FilePath = downPath + ''


class user_pageApi(object):
    """docstring for user_ageApi"""

    def __init__(self, arg):
        super(user_pageApi, self).__init__()
        self.arg = arg
        self.userEnd = False

    # 下载用户的作品
    def userAPI(self, userUrl):
        # print(userUrl)
        regex = r"/user/(.*)"
        matches = re.search(regex, userUrl)
        match = matches.group(1)
        userSecID = match[0:55]
        # print(userSecID)
        count = 35
        max_cursor = 0
        signature = 'mFxbIwAA-VAm1vvOdtn5U5hcWz&dytk='
        # post/?sec_uid={用户id}&count={count}&max_cursor={max_cursor}&aid=1128&_signature={signature}
        userApi = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=%s' % (
        userSecID, str(count), max_cursor, signature)
        print(userApi)
        jsondata = requests.get(userApi, headers=headers).content
        data = json.loads(jsondata)

        # 用户名
        nickname = data['aweme_list'][0]['author']['nickname']
        self.getData(userApi, userSecID, count, max_cursor, signature, nickname)

    # pass
    # 第一页/第一次访问
    def getData(self, userApi, userSecID, count, max_cursor, signature, nickname):
        # 尝试次数
        index = 0
        # 存储api数据
        result = []
        while result == []:
            index += 1
            print('------------正在进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(userApi, headers=headers)
            html = json.loads(response.content.decode())
            if self.userEnd == False:
                # 下一页值
                print('[ 用户 ]: ' + str(nickname) + '\r')
                max_cursor = html['max_cursor']
                # print(max_cursor)
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------抓获数据成功------------\r')
                # 处理第一页视频信息
                self.aPageInfo(result, userSecID, count, max_cursor, signature, nickname)
            else:
                max_cursor = html['max_cursor']
                self.nexData(userSecID, count, max_cursor, signature, nickname)
                # end = True
                print('------------此页无数据，为您跳过------------\r')
        return result, max_cursor

    # 下一页
    def nexData(self, userSecID, count, max_cursor, signature, nickname):
        userApi = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=%s' % (
        userSecID, str(count), max_cursor, signature)
        index = 0
        result = []
        while self.userEnd == False:
            # 回到首页，则结束
            if max_cursor == 0:
                self.userEnd = True
                return
            index += 1
            print('------------正在对', max_cursor, '页进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(userApi, headers=headers)
            html = json.loads(response.content.decode())
            if self.userEnd == False:
                # 下一页值
                max_cursor = html['max_cursor']
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------', max_cursor, '页抓获数据成功------------\r')
                # 处理下一页视频信息
                self.aPageInfo(result, userSecID, count, max_cursor, signature, nickname)
            else:
                self.userEnd == True
                print('------------', max_cursor, '页抓获数据失败------------\r')
                sys.exit()

    # 每页信息
    def aPageInfo(self, result, userSecID, count, max_cursor, signature, nickname):

        for i in result:
            itemApi = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
            itemApi = itemApi + i['aweme_id']
            r = requests.get(itemApi, headers=headers).content
            html = json.loads(r)

            print(i['desc'] + '---' + str(i['aweme_type']) + '---' + str(i['aweme_id']))
            # print(html['item_list'][0]['share_url']+'\n'+'--------------------')
            awemeShareUrl = html['item_list'][0]['share_url']
            # 这里对路径，也就是用户名进行校验
            waring = ['\\', '/', ":", '*', '?', "\"", '<', '>', '|']
            for i in waring:
                nickname = nickname.replace(i, '')
            downPath = nickname + '/'
            vi1 = viApi(self.arg)
            vi1.video_imagesAPI(awemeShareUrl, downPath)
            d1 = Download(vi1.FilePath, vi1.FileInfo)
            d1.downloadFile()
            time.sleep(0.3)

        self.nexData(userSecID, count, max_cursor, signature, nickname)


class collectionApi(object):
    """docstring for collectionApi"""

    def __init__(self, arg):
        super(collectionApi, self).__init__()
        self.arg = arg
        self.mixEnd = False
        self.mixNum = 1
        self.mixUpNum = None

    def mixAPI(self, url):
        regex = r"(/collection/|/mix/detail/)([\d]*)"
        matches = re.search(regex, url)
        match = matches.group(2)
        count = 10  # 如果抓取的数据有问题的话，可将该值调小
        cursor = 0  # 第一次访问
        mix_id = match
        # 合集列表api和合集信息api
        mix_list_api = 'https://www.iesdouyin.com/web/api/mix/item/list/?mix_id=%s&count=%s&cursor=%s' % (
        mix_id, str(count), str(cursor))
        mix_info_api = 'https://www.iesdouyin.com/web/api/mix/detail/?mix_id=%s' % mix_id

        print('list : ' + mix_list_api)
        print('info : ' + mix_info_api)

        r1 = requests.get(mix_list_api, headers=headers).content
        r2 = requests.get(mix_info_api, headers=headers).content
        html1 = json.loads(r1)
        html2 = json.loads(r2)
        # 合集中作品数目
        self.mixUpNum = html2['mix_info']['statis']['updated_to_episode']
        mix_name = html2['mix_info']['mix_name'] + '--' + html2['mix_info']['author']['nickname']
        self.getMixData(mix_list_api, mix_id, count, cursor, mix_name)

    # 第一页/第一次访问
    def getMixData(self, mix_list_api, mix_id, count, cursor, mix_name):
        # 尝试次数
        index = 0
        # 存储api数据
        result = []
        while result == []:
            index += 1
            print('------------正在进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(mix_list_api, headers=headers)
            html = json.loads(response.content.decode())
            if self.mixEnd == False:
                # 下一页值
                print('[ 合集 ]: ' + str(mix_name) + '\r')
                cursor = html['cursor']
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------抓获数据成功------------\r')
                # 处理第一页视频信息
                self.aPageMixInfo(result, mix_id, count, cursor, mix_name)
            else:
                cursor = html['cursor']
                self.nexMixData(mix_id, count, cursor, mix_name)
                # end = True
                print('------------此页无数据，为您跳过------------\r')
        return result, cursor

    # 下一页
    def nexMixData(self, mix_id, count, cursor, mix_name):
        mix_list_api = 'https://www.iesdouyin.com/web/api/mix/item/list/?mix_id=%s&count=%s&cursor=%s' % (
        mix_id, str(count), str(cursor))
        index = 0
        result = []
        while self.mixEnd == False:
            # 回到首页，则结束
            if cursor == 0 or self.mixNum > int(self.mixUpNum):
                self.mixEnd = True
                return
            index += 1
            print('------------正在对', cursor, '页进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(mix_list_api, headers=headers)
            html = json.loads(response.content.decode())
            if self.mixEnd == False:
                # 下一页值
                cursor = html['cursor']
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------', cursor, '页抓获数据成功------------\r')
                # 处理下一页视频信息
                self.aPageMixInfo(result, mix_id, count, cursor, mix_name)
            else:
                self.mixEnd == True
                print('------------', cursor, '页抓获数据失败------------\r')
                sys.exit()

    # 每页信息
    def aPageMixInfo(self, result, mix_id, count, cursor, mix_name):
        for i in result:
            # aweme_id = i['aweme_id']
            # print(i['desc'])
            # 下载地址
            downUrl = i['video']['play_addr']['url_list'][0]
            # 这里对路径，也就是合集名进行校验
            waring = ['\\', '/', ":", '*', '?', "\"", '<', '>', '|']
            for i in waring:
                mix_name = mix_name.replace(i, '')
            downPath = mix_name
            fileName = '第%s集-' % self.mixNum + i['desc'] + '.mp4'
            fileInfo = {fileName: downUrl}
            print(fileName)
            d = Download(downPath, fileInfo)
            d.downloadFile()
            self.mixNum += 1
            time.sleep(0.3)

        self.nexMixData(mix_id, count, cursor, mix_name)


class challengeApi(object):
    """docstring for challengeApi"""

    def __init__(self, arg):
        super(challengeApi, self).__init__()
        self.arg = arg
        # 相关话题视频的下载数量
        self.downNum = 100  # 最多下载
        self.chaNum = 0  # 下载计数
        self.chaEnd = False

    def chAPI(self, url):
        regex = r"(/challenge/)(.*)(\/\?)"
        matches = re.search(regex, url)
        match = matches.group(2)
        # 话题id
        ch_id = match
        count = 9
        cursor = 0
        # _signature
        # result = os.popen('node signature.js')
        # context = result.read()
        # _signature = str(context)
        _signature = 'Af1mUwAAYOj-ApmsAY3k5wH9Zk'
        # 话题作品列表api和话题信息api
        ch_aweme_api = 'https://www.iesdouyin.com/web/api/v2/challenge/aweme/?ch_id=%s&count=%s&cursor=%s&aid=1128&screen_Limit=3&download_click_limit=0&_signature=%s' % (
        ch_id, str(count), str(cursor), _signature)
        ch_info_api = 'https://www.iesdouyin.com/web/api/v2/challenge/info/?ch_id=%s' % ch_id
        r1 = requests.get(ch_aweme_api, headers=headers).content
        r2 = requests.get(ch_info_api, headers=headers).content
        d1 = json.loads(r1)
        d2 = json.loads(r2)
        # 话题名
        cha_name = '#' + d2['ch_info']['cha_name']
        print(cha_name)
        self.getChaData(ch_aweme_api, ch_id, count, cursor, cha_name, _signature)

    # 第一页/第一次访问
    def getChaData(self, ch_aweme_api, ch_id, count, cursor, cha_name, _signature):
        # 尝试次数
        index = 0
        # 存储api数据
        result = []
        while result == []:
            index += 1
            print('------------正在进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(ch_aweme_api, headers=headers)
            html = json.loads(response.content.decode())
            if self.chaEnd == False:
                # 下一页值
                print('[ 合集 ]: ' + str(cha_name) + '\r')
                # cursor = html['cursor']
                cursor += 9
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------抓获数据成功------------\r')
                # 处理第一页视频信息
                self.aPageChaInfo(result, ch_id, count, cursor, cha_name, _signature)
            else:
                cursor = html['cursor']
                self.nexChaData(ch_id, count, cursor, cha_name, _signature)
                # end = True
                print('------------此页无数据，为您跳过------------\r')
        return result, cursor

    def nexChaData(self, ch_id, count, cursor, cha_name, _signature):
        ch_aweme_api = 'https://www.iesdouyin.com/web/api/v2/challenge/aweme/?ch_id=%s&count=%s&cursor=%s&aid=1128&screen_Limit=3&download_click_limit=0&_signature=%s' % (
        ch_id, str(count), str(cursor), _signature)
        index = 0
        result = []
        while self.chaEnd == False:
            # 回到首页，则结束
            if cursor == 0 or self.chaNum > self.downNum:
                self.chaEnd = True
                return
            index += 1
            print('------------正在对', cursor, '页进行第 %d 次尝试------------\r' % index)
            time.sleep(0.3)
            response = requests.get(ch_aweme_api, headers=headers)
            html = json.loads(response.content.decode())
            if self.chaEnd == False:
                # 下一页值
                # cursor = html['cursor']
                cursor += 9
                result = html['aweme_list']
                print(len(html['aweme_list']))
                print('------------', cursor, '页抓获数据成功------------\r')
                # 处理下一页视频信息
                self.aPageChaInfo(result, ch_id, count, cursor, cha_name, _signature)
            else:
                self.chaEnd == True
                print('------------', cursor, '页抓获数据失败------------\r')
                sys.exit()

    def aPageChaInfo(self, result, ch_id, count, cursor, cha_name, _signature):
        for i in result:
            fileName = i['author']['nickname'] + '-' + i['desc'] + '.mp4'
            downUrl = i['video']['play_addr']['url_list'][0]
            downUrl = downUrl.replace('/playwm', '/play')
            # 这里对路径，也就是话题名进行校验
            waring = ['\\', '/', ":", '*', '?', "\"", '<', '>', '|']
            for i in waring:
                cha_name = cha_name.replace(i, '')
            downPath = cha_name
            fileInfo = {fileName: downUrl}
            print(fileName)
            d = Download(downPath, fileInfo)
            d.downloadFile()
            self.chaNum += 1
            time.sleep(0.3)

        self.nexChaData(ch_id, count, cursor, cha_name, _signature)


# Url类
class Url:
    """docstring for Url"""

    def __init__(self, arg):
        super(Url, self).__init__()
        self.urlType = None
        self.text = arg
        self.url = self.Regular_match(self.text)
        self.newUrl = self.getNewUrl(self.url)
        self.judgeUrl()

    # 对输入的数据进行处理，正则匹配URL
    def Regular_match(self, text):
        regex = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’]))"
        matches = re.search(regex, text)
        match = matches.group()
        return match

    # 访问匹配出来的url，判断302跳转等等，获取真正的url
    def getNewUrl(self, url):
        r = requests.get(url, headers=headers)
        newUrl = r.url
        return newUrl

    # 对newUrl进行判断，是单个视频，相册，话题，合集，用户，短剧
    def judgeUrl(self):
        # 单个视频或相册 self.newUrl.find("iesdouyin.com/share/video")!=-1 or self.newUrl.find("douyin.com/video")!=-1
        if "iesdouyin.com/share/video" in self.newUrl or "douyin.com/video" in self.newUrl:
            self.urlType = 1
        # 话题 self.newUrl.find("iesdouyin.com/share/challenge")!=-1
        elif "iesdouyin.com/share/challenge" in self.newUrl:
            self.urlType = 2
        # 用户 self.newUrl.find("douyin.com/user")!=-1
        elif "douyin.com/user" in self.newUrl:
            self.urlType = 3
        # 合集 self.newUrl.find("iesdouyin.com/share/mix/detail")!=-1
        elif "iesdouyin.com/share/mix/detail" in self.newUrl or "douyin.com/collection" in self.newUrl:
            self.urlType = 4
        # 短剧 self.newUrl.find("iesdouyin.com/share/playlet/detail")!=-1
        elif "iesdouyin.com/share/playlet/detail" in self.newUrl:
            self.urlType = 5
        # 没有识别出来
        else:
            self.urlType = -1
        return self.urlType


def getDownloadUrl(url, urlType):
    if urlType == 1:
        vi = viApi(url)
        vi.video_imagesAPI(url, '')
        d = Download(vi.FilePath, vi.FileInfo)
        d.downloadFile()

    elif urlType == 2:
        print('话题')
        ch = challengeApi(url)
        ch.chAPI(url)

    elif urlType == 3:
        # print('用户')
        up = user_pageApi(url)
        up.userAPI(url)

    elif urlType == 4:
        print('合集')
        coll = collectionApi(url)
        coll.mixAPI(url)

    elif urlType == 5:
        print('短剧')
    else:
        print('error')


def main():
    text = input('Input:')
    u = Url(text)
    # print(u.newUrl)
    # a = video_imagesApi(u.newUrl, u.urlType)
    getDownloadUrl(u.newUrl, u.urlType)


# print(a.FileNames)
# print(a.FilePath)
# print(a.FileInfo)
# d = Download(a.FilePath, a.FileInfo)
# d.downloadFile()


if __name__ == '__main__':
    main()

