import requests             # has built-in json!
from urllib import request  # query imgur
import time                 # for rate-limiting?
import os.path              # write files locally

# hastily written by: https://github.com/jonobrien
# doing this now because: 
# I thought of it
# the reddit api limit of 1000 posts is apparently (probably circumvented by querying...)
# the massive amount of reddit posts per day and reaching that limit fast
# the lack of knowledge of refining reddit query further for generic image urls/lack of interest in learning advanced reddit searches

# I limited this to just imgur searches, but could/SHOULD be further extended as needed. Obviously just the url request...
# you can change any post on reddit to json by adding '.json' to the search query (see below)
# https://github.com/reddit/reddit/wiki/JSON#listing


# get newest posts to the subreddit, has NULL 'before' so can verify newest posts
baseQuery = 'http://www.reddit.com/r/Eve/search.json?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all' #newest
# query for older posts with the 'after' parameter in the request, has 'before' and 'after'
olderPosts = 'https://www.reddit.com/r/Eve/search.json?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all&after='#['after'] for more posts 
pageCount = 1 # the count of which page of the reddit search is currently being parsed

# reddit api needs a custom user-agent header
redHdr = {
    'User-Agent': 'reddit-imgur-parser 1.0',
	'Connection':'close'
}

# register an application with imgur and get the client ID and secret:
imgurID = 'registered id here'
imgurSecret = 'registered secret here'

# TODO -- query imgur and download the images, maybe folders by date...imgur albums?
# new session to get all imgur links dynamically from retrieved reddit posts
imgHdr = {
	'Authorization: Client-ID ' + imgurID

}




jsonBackup = {}
imgurUrls = {}
galleryUrls = {}
albumUrls = {}
sess = requests.Session()
afterParam = '&after='
beforeTs = None
afterTs = None

print('\ngetting recent /r/eve imgur posts\n')

# GET last 40 pages queried on the subreddit that have imgur links
while pageCount < 40:
	resp = None
	time.sleep(.2) # reddit ratelimit 60 req/min...
	if afterTs: # sequential posts after initial GET
		##### print(beforeTs) # assuming successful GET this works fine
		resp = sess.get(olderPosts + afterParam + afterTs, headers=redHdr).json()['data']
	else: # initial GET for newest posts
		resp = sess.get(baseQuery, headers=redHdr).json()['data']
		
	# every post has:
	jsonBackup[pageCount] = resp
	page = resp['children']
	beforeTs = resp['before']
	afterTs = resp['after']
	#### print(afterTs)
	for post in page:
		#time.sleep(.1)
		#####print(post['data']['url'])
		# get each image from imgur directly and save it locally
		# f = open('stripped-down-id.jpg', 'wb')
		# f.write(sess.urlopen("imgur-link.jpg").read())
		# f.close()
		
		# ensure no duplicate links
		imgurUrls[post['data']['url']] = post['data']['url']
	pageCount+=1
sess.close()
print(str(pageCount) + ' pages retrieved and stored')


print(imgurUrls)
print()
print('parsing urls\n')
# move this into the while loop
for url in imgurUrls.values():
	urlFixed = url
	if 'gallery' in url:
		print('ignored gallery: ' + url)
		galleryUrls[url] = url
		continue
	elif '/a/' in url:
		print('ignored album: ' + url)
		albumUrls[url] = url
		# get api list of all images
		continue
	else:
		imageName = url.replace('http://','').replace('https://','').replace('i.imgur.com/','').replace('imgur.com/','').replace('m.imgur.com/','').replace('?','')
		if '.' in imageName: # yay hacky - has extension already, can be downloaded properly, mostly
				imageName = imageName[:11]
		else:
			imageName = imageName[:7]
			imageName += '.gif' # static gif is still a png/jpg anyway...safest to guess on type of gif
			urlFixed += '.gif'
		print('retrieved: ' + imageName)
		try:
			path = os.path.join('./imgurEVE', imageName)
			f = open(path, 'wb')
			f.write(request.urlopen(urlFixed).read())
			f.close()
		except Exception:
			print('\n[!!] exception 404 most likely')
			print(imageName)
			print(urlFixed)
			print()

print('\ndone')
print('image urls total: ' + str(len(imgurUrls)))
print('galleries skipped: ' + str(len(galleryUrls)))
print('albums skipped: ' + str(len(albumUrls)))
print('individual images saved: ' + str(len(imgurUrls)-len(galleryUrls)-len(albumUrls)))
