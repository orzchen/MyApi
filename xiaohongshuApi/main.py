import requests
import re
import time
import json
import hashlib
import os

downHeaders = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
	'Accept-Encoding': 'gzip, deflate',
	'Connection': 'close',
	'Upgrade-Insecure-Requests': '1',
	'Pragma': 'no-cache',
	'Cache-Control': 'no-cache'
}
def getHeaders(api):
	regex = r'/fe_api/(.*)'
	matches = re.search(regex, api)
	match = matches.group(0)
	# 生成 X_Sign
	x_sign = "X"
	m = hashlib.md5()
	m.update((match+"WSUDD").encode())
	X_Sign = x_sign + m.hexdigest()

	headers = {
		'Host': 'www.xiaohongshu.com',
		'Connection': 'keep-alive',
		'Authorization': '你自己的',
		'Device-Fingerprint': '你自己的',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
		'X-Sign': X_Sign,
		'content-type': 'application/json',
		'Accept-Encoding': 'gzip, deflate, br'
	}
	return headers


# 下载类
class Download(object):
	"""docstring for Download"""

	def __init__(self, path, info):
		super(Download, self).__init__()
		self.path = path
		self.FileInfo = info
		# 对文件和路径名进行校验--在用户api中会出错，因为里面拼接了用户文件夹的路径，这里不能用来校验路径，参见210行
		waring = ['\\', '/', ":" , '*', '?', "\"", '<', '>', '|']
		self.Dict = {}
		for fname in self.FileInfo:
			fkey = fname
			for i in waring :
				fname = fname.replace(i, '')
				# 对路径的校验
				# self.path = self.path.replace(i, '')
			self.Dict.update({fname: self.FileInfo[fkey]})
		self.FileInfo = self.Dict

	def mkdir(self,path):
		folder = os.path.exists(path)
		if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
			os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

	def downloadFile(self):
		self.mkdir('File/%s'%self.path)
		for fname in self.FileInfo:
			r = requests.get(self.FileInfo[fname], headers=downHeaders)
			newpath = 'File/%s'%self.path + '/%s'%fname
			fileSize = r.headers['Content-Length']
			print('文件大小：%.2fMB' % (int(fileSize) / 1048576))
			with open(newpath, 'wb') as f:
				f.write(r.content)
			f.close
			print('下载完成')

# Url类
class Url(object):
	"""docstring for Url"""
	def __init__(self, arg):
		super(Url, self).__init__()
		self.arg = arg
		self.hd = {
			'Host':	'xhslink.com',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'close',
			'Upgrade-Insecure-Requests': '1',
			'Pragma': 'no-cache',
			'Cache-Control': 'no-cache'
		}
		url = self.Regular_match(self.arg)
		newUrl = self.getNewUrl(url)
		self.res = self.judgeUrl(newUrl)

	# 对输入的数据进行处理，正则匹配URL
	def Regular_match(self, text):
		regex = r"(http|https)(://)(.*)(\.com/[a-zA-Z0-9\/]*)"
		matches = re.search(regex, text)
		match = matches.group()
		# print(match)
		return match
		
	def getNewUrl(self, url):
		res = requests.get(url, headers=self.hd)
		newUrl = res.url
		# print(newUrl)
		return newUrl

	def judgeUrl(self, url):
		if 'user/profile/' in url:
			regex = r"user/profile/(.*)"
			matches = re.search(regex, url)
			match = matches.group(1)
			user_id = match
			return {'user_id': user_id, 'type': '1'}

		elif 'discovery/item/' in url:
			regex = r"discovery/item/(.*)"
			matches = re.search(regex, url)
			match = matches.group(1)
			item_id = match
			return {'item_id': item_id, 'type': '2'}

		else:
			return {'type': '-1'}

# Item类
class Item(object):
	"""docstring for Item"""
	def __init__(self, arg):
		super(Item, self).__init__()
		self.item_id = arg
		self.down_path = ''
		self.file_info = {}
		# self.judgeType(self.item_id, self.down_path)

	def judgeType(self, item_id, down_path):
		note_api = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/%s/single_feed'%item_id
		headers = getHeaders(note_api)
		res = requests.get(note_api, headers=headers).content
		data = json.loads(res)
		print(data['success'])
		if data['success'] == False :
			if data['msg'] == 'note censoring':
				print('note censoring')
				return
			else:
				pritn('anthoer error')

		if data['data']['type'] == 'normal':
			self.imgs(data, down_path)
		elif data['data']['type'] == 'video':
			self.video(data, down_path)

	def imgs(self, data, down_path):
		imglist = data['data']['imageList']
		if data['data']['title'] == '':
			filename = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
		else:
			filename = data['data']['title']

		waring = ['\\', '/', ":" , '*', '?', "\"", '<', '>', '|']
		for w in waring:
			filename = filename.replace(w, '')
		count = 1
		for img in imglist:
			fname = filename + '_%s.jpg'%count
			img_id = img['fileId']
			url = 'http://ci.xiaohongshu.com/%s'%img_id
			self.file_info.update({fname: url})
			count += 1
		# print(self.file_info)
		self.down_path = down_path + filename

	def video(self, data, down_path):
		# print(data)
		if data['data']['title'] == '':
			filename = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.mp4'
		else:
			filename = data['data']['title'] + '.mp4'
		url = data['data']['video']['url']
		self.file_info.update({filename: url})
		# print(self.file_info)
		self.down_path = down_path + ''

	def down(self):
		d = Download(self.down_path, self.file_info)
		d.downloadFile()

# User类
class User(object):
	"""docstring for User"""
	def __init__(self, arg):
		super(User, self).__init__()
		self.user_id = arg
		self.Notes = None
		self.nickname = None
		self.getInfo(self.user_id)
		
	
	def getInfo(self, user_id):
		user_info_api = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/%s'%user_id
		headers = getHeaders(user_info_api)
		res = requests.get(user_info_api, headers=headers).content
		data = json.loads(res)
		self.nickname = data['data']['nickname']
		notes = data['data']['notes']
		print('[ 用户 ]: %s \n[ Notes ]: %s'%(self.nickname, notes))
		self.Notes = self.getItem(user_id, self.nickname, notes)

	def getItem(self, user_id, nickname, notes):
		page = 1
		page_size = 15
		notes = int(notes)
		data_list = []
		note_info = {}
		flag = True
		while flag:
			user_item_api = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/%s/notes?page=%s&page_size=%s'%(user_id, str(page), str(page_size))
			headers = getHeaders(user_item_api)
			print('第%s次请求开始'%page)
			res = requests.get(user_item_api, headers=headers).content
			data = json.loads(res)

			if len(data['data']) == 0 or page > notes:
				flag = False
			data_list = data_list + data['data']
			print(str(len(data['data']))+'完成')
			page += 1
			# time.sleep(2)
		print('请求结束')
		for note in data_list:
			note_info.update({note['id']: note['title']})
			# print(note['title'])
		return note_info

	def down(self):
		# print(self.nickname)
		nickname = self.nickname
		waring = ['\\', '/', ":" , '*', '?', "\"", '<', '>', '|']
		for w in waring:
			nickname = nickname.replace(w, '')

		down_path =  '%s/'%self.nickname 
		for i in self.Notes:
			downitem = Item(i)
			downitem.judgeType(downitem.item_id, down_path)
			downitem.down()
			# time.sleep(2)



def getDownload(text):
	U = Url(text)
	if U.res['type'] == '1':
		print('用户')
		user = User(U.res['user_id'])
		user.down()

	elif U.res['type'] == '2':
		print('作品')
		item = Item(U.res['item_id'])
		item.judgeType(item.item_id, item.down_path)
		item.down()
	else:
		print('Error!')

def main():
	text = input('Input: ')
	getDownload(text)


if __name__ == '__main__':
	main()