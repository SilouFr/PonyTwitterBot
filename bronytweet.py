import urllib2
from urllib import urlretrieve
import sys
import os
import random
import string
import re
import HTMLParser
import json
from BeautifulSoup import BeautifulSoup, SoupStrainer
from twython import Twython

twitter = Twython("", "",
                  "", "")

img_folder = "images/"
root_folder = os.path.dirname(os.path.abspath(__file__)) + "/"
first_post = False
debug = False


def get_post(post_url, post_id, post_title, post_media, author):
	global twitter
	global img_folder
	global first_post
	global debug

	message_tweet = post_title+"\n"+"By "+author+"\n"+post_url+"\n#CheezPics"

	if debug is True:
		print "\nURL du post : "+post_url

	if ".png" or ".jpg" or ".gif" in post_media: #picture, not a video

		imageName = post_media.split("/")[-1]
		outpath = os.path.join(root_folder+img_folder, imageName)

		try:
			print "retrieving the media .."
			urlretrieve(post_media, outpath)

			if debug is True:
				print(imageName+extension+" saved")

		except:
			print "error on opening the image at url :: ", post_media
			pass

		if debug is True:
			print 'MEDIA : '+img_folder+imageName+' || STATUS : '+message_tweet

		size_img = os.stat(outpath).st_size

		if size_img < 3000000 :
			media_up = open(root_folder+img_folder+imageName, 'rb')
			media_response = twitter.upload_media(media=media_up)
			twitter.update_status(status=message_tweet, media_ids=[media_response['media_id']])

		else:
			twitter.update_status(status=message_tweet)

	else:
		twitter.update_status(status=message_tweet)

	posted_ids = open(root_folder+'posted_ids.txt', 'a')
	posted_ids.write("\n"+post_url)
	posted_ids.close()



def main():
	global debug
	global root_folder

	url = "https://geek.cheezburger.com/bronies/"
	posted_ids = open(root_folder+'posted_ids.txt', 'r')

	log_posts = posted_ids.read().splitlines() #get last line

	try:
		url_open = urllib2.urlopen(url)

	except urllib2.HTTPError, e:
		print("Error on opening url")
		sys.exit()

	content = BeautifulSoup(url_open.read())
	posts = content.findAll("div",{"class":"content-card"})

	for line in posts:
		if "KymTrending" not in str(line):
			description = line.find("div",{"class":"nw-post js-post"})['data-model']
			description_array = json.loads(description)
		
			post_id = description_array['AssetId']
			post_url = description_array['CanonicalUrl']
			post_media = description_array['Url']
			post_title = description_array['Title']

			author_bloc = line.find("span",{"class":"nw-attribution-clip"})
			author = author_bloc.find("a",{"class":"sourceattribution alt"}).getText()
		
			present = False
			for i in range(len(log_posts)):
				if(log_posts[i] == post_url):
					present = True

			if present is False:
				if debug is True:
					print "post url : ", post_url
					print "post id : ", post_id
					print "post title : ", post_title
					print "post media : ", post_media
					print "author : ", author
	
				get_post(post_url, post_id, post_title, post_media, author)
				break;

	posted_ids.close()

main()
