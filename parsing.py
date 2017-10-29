from bs4 import BeautifulSoup
import requests
import db

def vk_group_parsing(link):#парсит паблик вк, отделяя посты
	print(link)
	r = requests.get("https://m.vk.com"+str(link)+"?own=1#wall")
	soup = BeautifulSoup(str(r.text), "html.parser")
	if link == "/neuralmemes":
		print("Нихуя наш паблик")
		return None
	if soup.title.text == "404 Not Found":
		print(link+" не найдено")
		return None
	try:#Ищем название, если его нет по этому классу, то скорее всего это не паблик
		name = soup.find("h2", class_="basisGroup__groupTitle op_header").string.replace("\n","")
	except:
		print("Не удалось распознать страницу")
		return False
	if soup.find("div", class_="group_closed_text"):
		print("Закрытая группа")
		return False
	subs = soup.find("em", class_="pm_counter").text.replace(" ", "").replace(",","")
	try:
		status = soup.find("div", class_="pp_status").text
	except:
		status = ""
	if (int(subs)<10000):#если мало подписчиков, заканчиваем парсинг
		print("Мало подписчиков")
		return None
	group = {"url": link, "name": name, "subs": subs, "status": status}
	if not db.check_wordlist_group(group):
		return False
	db.add_group(group)#добавляем группу в базу данных или обновляем
	for posts in soup.findAll("div", class_="wall_item"):
		inpost = BeautifulSoup(str(posts), "html.parser")
		post_id = inpost.find("a", class_="wi_date")['href']
		ad = inpost.find("div", class_="pi_signed ads_mark")#рекламный пост
		pin = inpost.find("span", class_="explain")#прикрепленный пост
		if pin or ad:#если реклама или прикрепленный пост
			continue
		vk_post_parsing(post_id)

def vk_self_parsing():###ХОТЕЛ ЕЩЕ СДЕЛАТЬ ФУНКЦИЮ ПРОВЕРКИ СВОЕГО ПАБЛИКА
	r = request.get("https://m.vk.com/neuralmemes")
	soup = BeautifulSoup(str(r.text), "html.parser")
	#subs = soup.find("em", class_="pm_counter").text.replace(" ", "").replace(",","")
	for posts in soup.findAll("div", class_="wall_item"):
		inpost = BeautifulSoup(str(posts), "html.parser")
		post_id = inpost.find("a", class_="wi_date")['href']
		####ТАК ЛЕНЬ ПИСАТЬ ПОТОМ ДОПИШИ####

def vk_post_parsing(link):#парсит пост в группе
	r = requests.get("https://m.vk.com"+str(link))
	soup = BeautifulSoup(str(r.text), "html.parser")
	post = soup.findAll("div", class_="wall_item")
	try:
		author = soup.find("a", class_="pi_author")['href']
	except:
		db.delete_db_post(link)
	inpost = BeautifulSoup(str(post), "html.parser")
	if soup.title.text == "Ошибка" or soup.title.text == "Error":
		print(link+" Error")
		db.delete_db_post(link)
		return None
	try:
		text = inpost.find("div", class_="pi_text").text
	except:
		text = ""
	try:
		likes = inpost.find("b", class_="v_like").string.replace("K", "000")
	except:
		likes="0"
	try:
		shares = inpost.find("b", class_="v_share").string.replace("K", "000")
	except:
		shares="0"
	try:
		views = inpost.find("b", class_="v_views").string.replace("K", "000").replace(".","")
	except:
		views="0"
	images = ""
	for img in inpost.findAll("div", class_="thumb_map_img thumb_map_img_as_div"):
		try:
			images = images + img['data-src_big'].split("|")[0] + " ,\n"
		except:
			images = images
	post = {"id": link, "author": author, "text": text, "images": images, "likes": likes, "shares": shares, "views": views}
	repost = inpost.find("div", class_="pic_header")#если репост
	if repost:#если репост отправляем паблик в очередь
		repost_link = BeautifulSoup(str(repost), "html.parser").find("a")['href']
		db.add_to_queue(post, repost_link)
		return False
	db.add_post(link, post)
