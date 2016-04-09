import requests             # has built-in json!
from urllib import request  # query imgur
import time                 # for rate-limiting?
import os.path              # write files locally
import json                 # wanted to do this manually because dependency but too much work with url ':'

# hastily written by: https://github.com/jonobrien
# doing this now because: 
# I thought of it
# reddit api queries for subreddit posts limits the 'listing' to max size of 1000
# the lack of interest in learning advanced reddit searches
# not sure if reddit has a hardcoded limit on amount of data you can see previously
#     reached via scrolling/retrieving searched posts

# I limited this to just imgur searches
# but could/SHOULD be further extended/properly implemented for usability as needed
# Obviously just the subreddit url requested for...

# you can change any post on reddit to json by adding '.json' to the search query (see below)
# https://github.com/reddit/reddit/wiki/JSON#listing

# get newest posts to the subreddit, has NULL 'before' 
# so can verify newest posts with 'after' key/val
# 'before' tag is irrelevant here as we get the newest posts first anyway
baseQuery = 'http://www.reddit.com/r/Eve/search.json?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all' #newest
# query for older posts with the 'after' parameter in the request, has 'before' and 'after'
olderPosts = 'https://www.reddit.com/r/Eve/search.json?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all&after='#['after'] for more posts 
# reddit api needs a custom user-agent header
redHdr = {
    'User-Agent': 'reddit-imgur-parser 1.0',
	'Connection':'close'
}
# register an application with imgur and get the client ID and secret:
imgurID = 'registered id here'
imgurSecret = 'registered secret here'
# TODO -- query imgur properly and download the images, maybe folders by date...imgur albums and gallery pics
# should make new session to get all imgur links dynamically from the reddit posts
imgHdr = {
	'Authorization: Client-ID ' + imgurID
}
# TODO -- clean up all these variables
jsonBackup = {}               # all the data retrieved, save it, why not
jsonBackup['allUrls'] = {}    # a separated dictionary for ease of use, why not
newUrls = {}                  # all the urls for debugging and comparison
errorUrls = []                # these urls caused 404 errors or could not be saved
albumUrls = {}                # TODO -- use imgur api to get all album images
sess = requests.Session()     # session used to query reddit for json
pageCount = 1                 # the reddit page being parsed
afterParam = '&after='        # query string for searching
beforeTs = None               # previous post
afterTs = None                # next post
resp = None                   # the json from that reddit query


# cleaned up all the replacements for reuse
def cleanUrl(url):
	return(url.replace('http://','').replace('https://','').replace('i.imgur.com/','').replace('imgur.com/','').replace('m.imgur.com/','').replace('gallery/','').replace('?','').replace('/new',''))


# get previously run data and use it to save new links posted to the subreddit
print('parsing any previous data')
previousRunData = None
with open("prevRun.txt",mode='a+', encoding='utf-8') as f:
	f.seek(0)
	try: # has been run before
		previousRunData = json.loads(f.read())
		print('has previous data')
	except json.decoder.JSONDecodeError: # setup the obj
		previousRunData = {}
		previousRunData['allUrls'] = {}
		print('created initial data for first use')
print('done')
#### print(str(previousRunData))



print('\ngetting recent /r/eve imgur posts\n')
# GET last pages on /r/eve that have imgur links
# TODO -- add input args, eliminate all the hardcoding
while pageCount <= 300:
	time.sleep(.2) # reddit rate-limit 60 req/min, didn't want to risk problems here
	if afterTs: # sequential posts after initial GET
		##### print(beforeTs) # assuming successful GET this works fine
		resp = sess.get(olderPosts + afterParam + afterTs, headers=redHdr).json()['data']
	else: # initial GET for newest posts
		resp = sess.get(baseQuery, headers=redHdr).json()['data']
	# parse all the things
	jsonBackup[str(pageCount)] = {}
	jsonBackup[str(pageCount)]['resp'] = resp
	#### print(str(resp).encode('utf-8'))
	page = resp['children']
	beforeTs = resp['before'] # don't actually need it, as previously thought
	afterTs = resp['after']
	#### print(afterTs)
	for post in page:
		##### print(post['data']['url'])
		# TODO - refactor and get each image from imgur directly via authed api calls
		# f = open('stripped-down-id.jpg', 'wb')
		# f.write(sess.urlopen("imgur-link.jpg").read())
		# f.close()

		# ensure no duplicate links and tie url and reddit post together for sanity
		jsonBackup['allUrls'][post['data']['url']] = post['data']['title'] # {'url':'title'}
		newUrls[post['data']['url']] = post['data']['url']
	pageCount+=1

sess.close() # done getting that pesky info
print(str(pageCount) + ' pages retrieved and stored')


######print(jsonBackup['allUrls'])
print()
print('parsing urls')
"""   delete when cleaned up and verified more
savedUrls = {}
with open("urlsSaved.txt", encoding='utf-8') as f:
	savedUrls['saved'] = f.read()
# convert file str to dict with no dependencies...
for kv in savedUrls['saved'].split(','):
	print(kv.split(':'))
"""


# move this into the while loop
# get all the images from imgur
for url in newUrls.values():
	if url in previousRunData['allUrls']: # checks for key existence in the dict
		print('already downloaded: ' + str(url))
		continue # go to next url, skip the parsing
	# else unnecessary
	urlFixed = url
	imageName = None
	if '/a/' in url:
		print('ignored album: ' + url)
		albumUrls[url] = url
		# get api list of all images
		continue
	else:
		imageName = cleanUrl(url)
		if '.' in imageName: # has extension already, can be downloaded properly, mostly
			imageName = imageName[:11]
		else:
			imageName = imageName[:7]
			imageName += '.gif' # static gif is still a png/jpg anyway...safest to guess on type of gif
			urlFixed = urlFixed.replace('/gallery/','').replace('/new','') # gallery in url breaks it too
			urlFixed += '.gif'
			print('retrieving: ' + imageName)
		try:
			path = os.path.join('./imgurEVE', imageName)
			f = open(path, mode='wb+')
			f.write(request.urlopen(urlFixed).read())
			f.close()
		except Exception as e:
			print('\n[!!] exception usually 404')
			print('imageName, urlFixed, url')
			print(imageName)
			print(urlFixed)
			print(url)
			errorUrls.append(url)
			print(e)
			print()

print('\ndone saving images')
print('     new image urls total: ' + str(len(newUrls)))
print('the num of albums skipped: ' + str(len(albumUrls)))
print('  individual images saved: ' + str(len(newUrls)-len(albumUrls)))

# overwrite previous run data with new data
print('writing this run to prevRun.txt')
with open("prevRun.txt", mode='w', encoding='utf-8') as f:
	f.write(json.dumps(jsonBackup))
print('done')
print('manually save these albums:')
for url in albumUrls:
	print(url)
print('\nthese urls broke and should be looked into and downloaded manually')
for url in errorUrls:
	print(url)
print('done for real')
