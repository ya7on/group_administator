import vk
import info
from urllib.request import urlopen
from urllib.request import urlretrieve
import requests

session = vk.Session(access_token=info.token)
vk_api = vk.API(session)

def vk_upload_photo(src_big):
	data = vk_api.photos.getWallUploadServer(gid="IDГРУППЫ")######
	url = data['upload_url']
	urlretrieve(src_big, 'tmp.jpg')
	img = {'photo': ('img.jpg', open(r'tmp.jpg', 'rb'))}
	r = requests.post(url, files=img)
	photo_ = r.json()['photo']
	server_ = r.json()['server']
	hash_ = r.json()['hash']
	photodata = {'photo': photo_, 'hash': hash_, 'server': server_}
	wallphoto = vk_api.photos.saveWallPhoto(**photodata, gid="IDГРУППЫ")#######
	return wallphoto[0]

def repost(link):
	link = link.replace("/", "")
	a = vk_api.wall.repost(object=link, group_id=info.gid)
	print(a)

def images_to_string(imgs):
	string = ""
	imgs = imgs.replace("\n", "").replace(" ", "")
	imgs = imgs.split(",")
	i=0
	while i<len(imgs):
		if imgs[i]:
			vk_data = vk_upload_photo(imgs[i])
			string = string + vk_data['id'] + ","
		i+=1
	return string

def send_message(wall):####КИДАЕТ ВАМ ВСЕ, ЧТО ДОБАВЛЕНО В ОЧЕРЕДЬ
    wall = wall.split("/")[1]
    vk_api.messages.send(user_id=ВАШID, attachment=wall)
vk_api.messages.send(user_id=ВАШID, message="script started")

def post(post):
	attach = images_to_string(post[3])
	text = post[2]
	ans = vk_api.wall.post(owner_id=info.public_id, from_group="1", message=text, attachments=attach)
#vk_api.wall.post(owner_id=public_id, from_group=1, message="хуй")
