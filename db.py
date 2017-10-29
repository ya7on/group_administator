import sqlite3
import re
from datetime import date, datetime, timedelta
import posting

def add_post(link, post):#Добавляет или обновляет пост в базе данных
	today = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM `posts` WHERE `url` = ?", (post['id'],))
	result = cursor.fetchall()
	if result:
		cursor.execute("UPDATE `posts` SET `likes`=?, `shares`=?, `views`=?, `time`=? WHERE `url`=?", (post['likes'], post['shares'], post['views'], today, post['id'],))
	else:
		cursor.execute("INSERT INTO `posts` (`url`, `text`, `author`, `images`, `likes`, `shares`, `views`, `time`, `added`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (post['id'], post['text'], post['author'], post['images'], post['likes'], post['shares'], post['views'], today, today,))
		print(link+" добавлен")
	conn.commit()
	conn.close()

def add_group(group):#Добавляет или обновляет группу в базе данных
	today = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM `groups` WHERE `url` = ?", (group['url'],))
	average = get_average_group(group['url'])
	result = cursor.fetchall()
	if result:
		cursor.execute("UPDATE groups SET `name`=?, `subs`=?, `time`=?, `average`=? WHERE `url`=?", (group['name'], group['subs'], today, average, group['url'],))
	else:
		cursor.execute("INSERT INTO `groups` (`url`, `name`, `subs`, `time`, `average`) VALUES (?, ?, ?, ?, ?)", (group['url'], group['name'], group['subs'], today, average,))
	conn.commit()
	conn.close()

def add_to_queue(post, link):
	print("Репост "+link, end="")
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM `groups` WHERE `url` = ?", (link,))
	result = cursor.fetchall()
	average = get_average_group(link)
	check = post['likes'] + post['shares']*5
	if int(check) < int(average)*3:
		print(" недостаточно лайков на репосте")
		conn.close()
		return False
	if result:
		print(" уже есть в списке групп")
	else:
		cursor.execute("SELECT * FROM `queue` WHERE `url` = ?", (link,))
		result = cursor.fetchall()
		if result:
			print(" уже стоит в очереди")
		else:
			cursor.execute("INSERT INTO `queue` (`url`) VALUES (?)", (link,))
			print (" добавлена в очередь;")
	conn.commit()
	conn.close()

def check_wordlist_group(group):#Ищет слова из черного списка в паблике
	status = group['status'].lower()
	name = group['name'].lower()
	myfile = open("blacklist.txt", "r")
	text = myfile.readlines()[0].replace(" \n","").split(", ")
	az09 = list("абвгдеёжзийклмнопрстуфхцчшщьыъэюяabcdefghijklmnopqrstuvwxyz1234567890,-@:/ '.?!#$%^&*()_-+=[]<>`~")
	if set(name).difference(az09):
		print("Недопустимые символы в названии")
		myfile.close()
		return False
	for s in text:
		'''
		#проверка статуса
		if status.find(s)>=0:
			print("Найдены слова из черного списка: "+s)
			myfile.close()
			return False
		'''
		#проверка названия
		if name.find(s)>=0:
			print("Найдены слова из черного списка: "+s)
			myfile.close()
			return False
	myfile.close()
	return True

def group_db_polling():
	today = datetime.now() - timedelta(minutes=30)
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	for result in cursor.execute("SELECT * FROM `groups`"):
		date = string_to_date(result[4])
		if today > date:#если последняя проверка была больше часа назад
			conn.close()
			return result[2]
		else:
			continue
	conn.close()
	return False

def post_db_polling():
	today = datetime.now() - timedelta(minutes=30)
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	for result in cursor.execute("SELECT * FROM `posts`"):
		date = string_to_date(result[4])
		if today > date:#если последняя проверка была больше часа назад
			conn.close()
			return result[1]
		else:
			continue
	conn.close()
	return False

def queue_db_polling():
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	for result in cursor.execute("SELECT * FROM `queue`"):
		if result:
			cursor.execute("DELETE FROM `queue` WHERE `url`=?", (result[2],))
			conn.commit()
			conn.close()
			return result[2]
		else:
			conn.commit()
			conn.close()
			return False

def datecheck_db_post():
	today = datetime.now() - timedelta(hours=12)
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	for result in cursor.execute("SELECT * FROM `posts`"):
		date = string_to_date(result[10])
		if date < today:
			conn.close()
			return result[1]
	conn.close()
	return False

def check_db_post():#проверяем по среднему арифм. нормальный ли пост
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	for result in cursor.execute("SELECT * FROM `posts`"):
		author = result[2]
		average = get_average_group(author)
		likes = result[6]
		shares = result[7]
		views = result[8]
		check = likes + shares * 5
		if check >= average * 2.5:
			conn.close()
			print("== Хороший пост ==")
			print("Пост: "+str(check)+" Средний: "+str(average))
			print(result[1])
			return result[1]
	conn.close()

def post_queue_db(link):
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM `post_queue` WHERE `url` = ?", (link,))
	result = cursor.fetchall()
	if result:
		print("Уже есть в очереди записей")
		cursor.execute("DELETE FROM `posts` WHERE `url` = ?", (link,))
		conn.commit()
		return False
	cursor.execute("SELECT * FROM `posts` WHERE `url` = ?", (link,))
	result = cursor.fetchall()
	cursor.execute("DELETE FROM `posts` WHERE `url` = ?", (link,))
	if result[0][5]:#################################МОЖЕТ РАБОТАТЬ ЧЕРЕЗ ЖОПУ теги
		cursor.execute("SELECT * FROM `groups` WHERE `url`=?", (result[0][2],))
		print(result[0][2])
		desc = cursor.fetchall()[0][6]
		print(desc)
		if desc:
			text = str(desc)
		else:
			text = result[0][3]
		cursor.execute("INSERT INTO `post_queue` (`url`, `text`, `images`, `author`) VALUES (?, ?, ?, ?)", (result[0][1], text, result[0][5], result[0][2],))
		print(link+" добавлен в очередь записей")
		posting.send_message(result[0][1])
	conn.commit()
	conn.close()

def posting_queue_db():#####################################################ПЕРЕПИШИ
	today = datetime.now() - timedelta(minutes=30)
	now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT `date` FROM `memes` ORDER BY `id` DESC LIMIT 1")
	date = cursor.fetchall()[0][0]
	date = string_to_date(date)
	if date > today:
		conn.close()
		return False
	for result in cursor.execute("SELECT * FROM `post_queue`"):
		cursor.execute("SELECT * FROM `memes` WHERE `oldurl`=?", (result[1],))
		in_db = cursor.fetchall()
		if in_db or not result[3]:
			print("Пост не подходит")
			cursor.execute("DELETE FROM `post_queue` WHERE `url`=?", (result[1],))
			conn.commit()
			continue
		cursor.execute("DELETE FROM `post_queue` WHERE `url`=?", (result[1],))
		cursor.execute("INSERT INTO `memes` (`date`, `author`, `oldurl`) VALUES (?, ?, ?)", (now, result[4], result[1]))
		#cursor.execute("UPDATE `memes` SET `date`=?", (now,))
		conn.commit()
		conn.close()

		return result
	conn.close()
	return False

def delete_db_post(link):#Удаляет пост из базы данных
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM `posts` WHERE `url` = ?", (link,))
	result = cursor.fetchall()
	if result:
		cursor.execute("DELETE FROM `posts` WHERE `url` = ?", (link,))
		print(link+" удален")
	conn.commit()
	conn.close()

def string_to_date(string):#переводит строку в datetime формат
	year, month, date = string.split("-")
	day = date.split(" ")[0]
	hour, minute, second = date.split(" ")[1].split(":")
	date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
	return date

def get_average_group(url):
	conn = sqlite3.connect("database.db", check_same_thread=False)
	cursor = conn.cursor()
	i=1
	numerator = 0
	for result in cursor.execute("SELECT * FROM `posts` WHERE `author`=?", (url,)):
		numerator += int(result[6]) + int(result[7])*5
		i += 1
	if i<=2:
		conn.close()
		return 1488
	average = numerator / i
	conn.close()
	return average
