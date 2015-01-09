import urllib.request
import urllib.parse
import bdecoder as bdecoder
import hashlib as hashlib

'''
Generate working url request
It should look like:
http://thomasballinger.com:6969/announce?uploaded=0&compact=1&info_hash=%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09&event=started&downloaded=0&peer_id=1406230005.05tom+cli&port=6881&left=1277987
'''
def get_peer_info():
	with open('flagfromserver.torrent', 'rb') as f:
	# sha1 hash bencoded info dictionary
	# url encoded hash should match: %2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09
		dictionary = bdecoder.bdecoder(f.read())
		info = dictionary[b'info']
		ben_string = info['ben_string']
		info_hash = hashlib.sha1(ben_string)
		params = {
			'info_hash' : '%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09',
			'event' : "started",	# event- default "started"
			'downloaded' : '0',		# number of bytes downloaded
			'peer_id' : '-TZ-0000-00000000000',
			'port' : '6881',
			'left' : info[b'length'].decode('utf-8'),	# number of bytes left to download, default number of bytes in file
			}

		tracker_url = dictionary[b'announce'].decode('utf-8') + '?'
		url_elems = []
		for key in params:
			url_elems.append(key + '=' + params[key])
		url_add = '&'.join(url_elems)	
		tracker_url += url_add
		
		return bdecoder.bdecoder(urllib.request.urlopen(tracker_url).read())

peer_info = get_peer_info()
raw_peer_info = [i for i in peer_info[b'peers']]
peers = [raw_peer_info[i:i+6] for i in range(0,len(raw_peer_info), 6)]
for peer in peers:
	for i in range(4):
		 peer[i] = str(peer[i])
peer_dict = {('.'.join(peer[:4])):peer[4]*256+peer[5] for peer in peers}
print(peer_dict)






