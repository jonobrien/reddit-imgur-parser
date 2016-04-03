import requests # has built-in json!
import time     # for rate-limiting

# doing this now because: 
# I thought of it
# the reddit api limit of 1000 posts is apparently (probably circumvented by querying...)
# the massive amount of reddit posts per day and reaching that limit fast
# the lack of knowledge of refining reddit query further for generic image urls/lack of interest in learning advanced reddit searches

# I limited this to just imgur searches, but could/SHOULD be further extended as needed. Obviously just the url request...

# hastily written by: https://github.com/jonobrien

# you can change any post on reddit to json by adding '.json' to the search query (see below)
# https://github.com/reddit/reddit/wiki/JSON#listing
# get newest posts to the subreddit, has NULL 'before' so can verify newest posts
queryStr = 'http://www.reddit.com/r/Eve/search.json?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all' #newest
# query for older posts with the 'after' parameter in the request, has 'before' and 'after'
strr = 'https://www.reddit.com/r/Eve/search?q=site%3Aimgur.com&restrict_sr=on&sort=new&t=all&count=100&after='#['after'] for more posts 
pageCount = 1 # the count of which page of the reddit search is currently being parsed

# reddit api needs a custom user-agent header
hdr = {
    'User-Agent': 'reddit-imgur-parser 1.0',
	'Connection':'close'
}
jsonBackup = {}
sess = requests.Session()


print('\ngetting recent /r/eve imgur posts\n')

# GET last 40 pages queried on the subreddit that have imgur links
while pageCount < 3:
	time.sleep(.2) # reddit ratelimit 60 req/min...
	queryMe = queryStr+str(pageCount)
	# TODO -- need to account for 'after' parameter
	# TODO -- query imgur and download the images, maybe folders by date...
	resp = sess.get(queryMe, headers=hdr).json()
	jsonBackup[pageCount] = resp
	page = resp['data']['children']
	#print(page)
	for post in page:
		print(post['data']['url'])
	print('\n' + str(pageCount) + ' page(s) done\n')
	pageCount+=1
	
print()
	
