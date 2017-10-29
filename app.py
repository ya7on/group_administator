#Накидал за вечер/два такой интересный скрипт
#Можно еще сделать проверку новых групп через личку в ВК, но мне лень этим заниматься 
#Здесь работает vk.com/NeuralMemes

#Я в телеграме @ya7on

import time
import parsing
import db
import posting
from datetime import datetime

while True:
	date = datetime.strftime(datetime.now(), "%H:%M")
	url = db.group_db_polling()
	if url:
		print("== Паблик ==")
		parsing.vk_group_parsing(url)
		time.sleep(5)
		print(date + "\n")
	url = db.post_db_polling()
	if url:
		print("== Обновляем посты ==")
		parsing.vk_post_parsing(url)
		time.sleep(5)
		print(date + "\n")
	url = db.queue_db_polling()
	if url:
		print("== Очередь ==")
		parsing.vk_group_parsing(url)
		time.sleep(5)
		print(date + "\n")
	url = db.datecheck_db_post()
	if url:
		print("== Устаревший пост ==")
		db.delete_db_post(url)
		time.sleep(5)
		print(date + "\n")
	url = db.check_db_post()
	if url:
		db.post_queue_db(url)
		time.sleep(5)
		print(date + "\n")
	url = db.posting_queue_db()
	if url:
		print("== Постинг ==")
		try:
			posting.post(url)
		except:
			print("не удалось загрузить")
		print(date + "\n")
	time.sleep(5)
