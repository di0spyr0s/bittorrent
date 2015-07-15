
from peer import Peer
from tracker import Tracker
from requests import get
from asyncio import get_event_loop
from json import loads

class Torrent_Downloader():
	''' Manages download logic:
		- Creation and removal of peers. 
		- Book keeping of pieces downloaded and in progress.
		- Checking completed pieces and writing to file.
	'''
	def __init__(self, torrent, start_listener_callback):
		self.torrent = torrent
		self.start_listener_callback = start_listener_callback
		self.ip = self.get_IP_address()
		self.tracker = Tracker(self.torrent.announce, self.torrent.get_params())
		self.peers = self.create_peers()
		self.io_loop = get_event_loop()
		self.index = 0
		self.callback_dict = {
			'check_piece' : self.torrent.check_piece_callback,
			'pieces_changed' : self.pieces_changed_callback,
			'start_listener' : self.start_listener_callback,
		}
		self.pieces_needed = []


	def get_IP_address(self):
		response = get('http://api.ipify.org?format=json')
		ip_object = loads(response.text)
		return ip_object["ip"]

	def create_peers(self):
		peers = []
		for p in self.tracker.parse_peer_address():
			if p[0] == self.ip:
				continue
			peers.append(Peer(p[0], p[1], self))
		return peers


	def pieces_changed_callback(self, peer):
		'''	Check if connected peer has pieces I need. Send interested message.
			Call choose_piece.
			If peer has no pieces I need, disconnect and remove from peers list.
		'''
		self.torrent.update_pieces_needed()
		for i in self.torrent.pieces_needed:
			if peer.has_pieces[i]:
				self.io_loop.create_task(peer.send_message(2))
				self.choose_piece(peer)	
				break
			else:
				self.peers.remove(peer)


	def choose_piece(self, peer):
		'''	Finds the next needed piece, updates self.have and self.pieces_needed.
			calls construct_request_payload.
		'''
		piece_index = self.torrent.pieces_needed[0]
		self.torrent.have[piece_index] = True
		self.torrent.update_pieces_needed()
		self.construct_request_payload(piece_index, peer)


	def construct_request_payload(self, piece_index, peer):
		'''	Constructs the payload of a request message for piece_index.
			Calls peer.send_message to finish construction and send.
		'''
		piece_index_bytes = (piece_index).to_bytes(4, byteorder='big')
		piece_begin = (0).to_bytes(4, byteorder='big')
		piece_length = (16384).to_bytes(4, byteorder='big')
		payload = b''.join([piece_index_bytes, piece_begin, piece_length])
		self.io_loop.create_task(peer.send_message(6, payload))	


	