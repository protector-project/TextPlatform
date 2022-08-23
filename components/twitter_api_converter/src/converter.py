import argparse
import json
from datetime import datetime

def assemble_tweet(current_tweet,users_idx,retweets_idx,includes,media_idx):
	tweet = create_tweet(current_tweet,media_idx)  #create the tweet
	u_idx = users_idx[current_tweet['author_id']] #id of the author of the tweet
	tweet['user'] = create_user(includes['users'][u_idx]) # create the user of the tweet
	try:
		if current_tweet['referenced_tweets'][0]['type'] == 'retweeted': 
			r_idx = retweets_idx[current_tweet['referenced_tweets'][0]['id']] #id of the retweet contained in the tweet
			tweet['retweeted_status'] = create_tweet(includes['tweets'][r_idx],media_idx) # add the field retweeted_status
			u_r_idx = users_idx[includes['tweets'][r_idx]['author_id']] #id of the author of the retweet 
			tweet['entities']['hashtags'] = tweet['retweeted_status']['entities']['hashtags']
			tweet['retweeted_status']['user'] = create_user(includes['users'][u_r_idx]) # create the user of the retweet
			tweet['text'] = tweet['retweeted_status']['text']
		elif current_tweet['referenced_tweets'][0]['type'] == 'quoted':
			r_idx = retweets_idx[current_tweet['referenced_tweets'][0]['id']]
			tweet['quoted_status'] = create_tweet(includes['tweets'][r_idx],media_idx)
			u_r_idx = users_idx[includes['tweets'][r_idx]['author_id']]
			tweet['quoted_status']['user'] = create_user(includes['users'][u_r_idx])
		elif current_tweet['referenced_tweets'][0]['type'] == 'replied_to':
			r_idx = retweets_idx[current_tweet['referenced_tweets'][0]['id']]
			tweet['replied_to'] = create_tweet(includes['tweets'][r_idx],media_idx)
			u_r_idx = users_idx[includes['tweets'][r_idx]['author_id']]
			tweet['replied_to']['user'] = create_user(includes['users'][u_r_idx])
	except:
		pass
	return(tweet)

def create_tweet(current_tweet,media_idx):
	tweet = {'created_at':[],'id_str':[],'user':[]}
	time = datetime.strptime(current_tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
	tweet['created_at'] = time.strftime('%a %b %d %H:%M:%S +0000 %Y')#[0:19]
	tweet['date'] = time.strftime('%a %b %d')
	tweet['id_str'] = str(current_tweet['id'])
	tweet['id'] = int(current_tweet['id']) #@A
	tweet['entities'] = {'url':[],'media':{'num': 0, 'type': []}}
	tweet['text'] = current_tweet['text']
	tweet['source'] = current_tweet['source']
	tweet['conversation_id'] = current_tweet['conversation_id']
	tweet['retweet_count'] = current_tweet['public_metrics']['retweet_count']
	tweet['reply_count'] = current_tweet['public_metrics']['reply_count']
	tweet['like_count'] = current_tweet['public_metrics']['like_count']
	tweet['quote_count'] = current_tweet['public_metrics']['quote_count']
	tweet['lang'] = current_tweet['lang']

	if "entities" not in current_tweet:
		current_tweet["entities"] = {}
	if "hashtags" not in current_tweet["entities"]:
		current_tweet["entities"]["hashtags"] = []

	if 'hashtags' in current_tweet['entities']:
		tweet['entities']['hashtags'] = []
		for k in range(len(current_tweet['entities']['hashtags'])):
			tweet['entities']['hashtags'].append({'text':current_tweet['entities']['hashtags'][k]['tag'].lower()})
	if 'mentions' in current_tweet['entities']:
		tweet['entities']['user_mentions'] = []
		for k in range(len(current_tweet['entities']['mentions'])):
			tweet['entities']['user_mentions'].append({'screen_name':current_tweet['entities']['mentions'][k]['username']})
	try:
		for k in range(len(current_tweet['entities']['urls'])):
			tweet['entities']['url'].append({'expanded_url':current_tweet['entities']['urls'][k]['expanded_url']})
	except:
		pass	
	try:
		for k in range(len(current_tweet['attachments']['media_keys'])):
			tweet['entities']['media']['type'].append(media_idx[current_tweet['attachments']['media_keys'][k]])
		tweet['entities']['media']['num'] = len(tweet['entities']['media']['type'])
	except:
		pass
	return(tweet)
	
def create_user(user):
	tweet = {'id_str':[],'url':[],'verified':[],'pinned_tweet_id':[],'geo_enabled':[],'default_profile':[],'default_profile_image':[],'location':[],'lang':[],'description':[],'protected':[],'screen_name':[],'followers_count':[],'friends_count':[],'listed_counts':[],'statuses_count':[],'created_at':[]}
	tweet['id_str'] =  str(user['id'])
#	tweet['id'] =  int(user['id'])
	tweet['screen_name'] = user['username']
	tweet['name'] = user['name']
	tweet['followers_count'] = user['public_metrics']['followers_count']
	tweet['friends_count'] = user['public_metrics']['following_count']
	tweet['listed_counts'] = user['public_metrics']['listed_count']
	tweet['favourites_count'] = 0
	tweet['statuses_count'] = user['public_metrics']['tweet_count']
	time = datetime.strptime(user['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
	tweet['created_at'] = time.strftime('%a %b %d %H:%M:%S +0000 %Y')
	stufflist = ['verified','location','description','protected','lang','geo_enabled','pinned_tweet_id','profile_image_url']
	for x in stufflist:
		if x in user:
			tweet[x] = user[x]	
	try:	
		tweet['url'] = user['entities']['url']['urls'][0]['expanded_url']
	except:
		pass
	return(tweet)

def create_json(a):
	alltweets = list()
	retweets_idx = dict()
	users_idx = dict()
	media_idx=dict()
	if "includes" in a:
		if "users" in a['includes']:
			for i in range(len(a['includes']['users'])):
				users_idx[a['includes']['users'][i]['id']] = i
		if "tweets" in a['includes']:
			for i in range(len(a['includes']['tweets'])):
				retweets_idx[a['includes']['tweets'][i]['id']] = i
		if "media" in a['includes']:
			for i in range(len(a['includes']['media'])):
				media_idx[a['includes']['media'][i]['media_key']] = a['includes']['media'][i]['type']				
	if "data" in a:
		if isinstance(a['data'], list):
			for i in range(len(a['data'])):
				tweet = assemble_tweet(a['data'][i], users_idx, retweets_idx, a['includes'],media_idx)
				alltweets.append(tweet)
		else:
			tweet = assemble_tweet(a['data'], users_idx, retweets_idx, a['includes'],media_idx)
			alltweets.append(tweet)
	return(alltweets)

# parser = argparse.ArgumentParser()
# parser.add_argument("-I", "--input", default="", required=True, type=str, help="Input")
# args = parser.parse_args()

# with open(args.input, 'r') as f:
#     for line in f:
#         line = line.replace("\n","")
#         line = line.strip()
#         a = json.loads(line)
#         myjson = create_json(a)
#         for j in range(len(myjson)):
#            print(json.dumps(myjson[j]))

def convert_tweets(input_file):
    result = []
    for line in input_file:
        line = line.replace("\n","")
        line = line.strip()
        a = json.loads(line)
        myjson = create_json(a)
        for j in range(len(myjson)):
           result.append(str(json.dumps(myjson[j])))
    return result
