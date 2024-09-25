from flask import Flask, request, jsonify

app = Flask(__name__)

# Linked List implementation for songs in the playlist
class SongNode:
    def __init__(self, song_id, name, artist, genre):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.genre = genre
        self.next = None
        self.prev = None

class Playlist:
    def __init__(self, name):
        self.name = name
        self.head = None
        self.tail = None
        self.size = 0

    def add_song(self, song_id, name, artist, genre):
        new_song = SongNode(song_id, name, artist, genre)
        if self.head is None:
            self.head = self.tail = new_song
        else:
            self.tail.next = new_song
            new_song.prev = self.tail
            self.tail = new_song
        self.size += 1

    def remove_song(self, song_id):
        current = self.head
        while current:
            if current.song_id == song_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next  # If it's the head song

                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev  # If it's the tail song

                self.size -= 1
                return True
            current = current.next
        return False

    def search_song(self, search_key, search_type='name'):
        results = []
        current = self.head
        while current:
            if search_type == 'name' and current.name == search_key:
                results.append(current)
            elif search_type == 'artist' and current.artist == search_key:
                results.append(current)
            elif search_type == 'genre' and current.genre == search_key:
                results.append(current)
            current = current.next
        return results

    def sort_playlist(self, key='name'):
        if not self.head:
            return

        sorted_list = Playlist(self.name)
        current = self.head

        while current:
            next_song = current.next
            insert_sorted(sorted_list, current, key)
            current = next_song

        self.head = sorted_list.head
        self.tail = sorted_list.tail

# Helper function to insert songs in sorted order
def insert_sorted(playlist, new_song, key):
    new_song.next = new_song.prev = None
    if not playlist.head:
        playlist.head = playlist.tail = new_song
        return

    current = playlist.head
    while current:
        if ((key == 'name' and new_song.name < current.name) or 
            (key == 'artist' and new_song.artist < current.artist) or 
            (key == 'genre' and new_song.genre < current.genre)):
            # Insert before current
            new_song.next = current
            new_song.prev = current.prev
            if current.prev:
                current.prev.next = new_song
            else:
                playlist.head = new_song  # Inserted at the head
            current.prev = new_song
            return
        
        current = current.next
    
    # If not inserted, insert at the end (tail)
    playlist.tail.next = new_song
    new_song.prev = playlist.tail
    playlist.tail = new_song

# In-memory storage for playlists and songs
playlists = {}
song_id_counter = 1

# API Routes

# Create a new playlist
@app.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.json
    playlist_name = data.get('name')
    playlist_id = len(playlists) + 1
    playlists[playlist_id] = Playlist(playlist_name)
    return jsonify({'message': 'Playlist created', 'id': playlist_id}), 201

# Get a playlist
@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = playlists.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    # Traverse playlist and list songs
    current = playlist.head
    songs = []
    while current:
        songs.append({
            'song_id': current.song_id,
            'name': current.name,
            'artist': current.artist,
            'genre': current.genre
        })
        current = current.next
    
    return jsonify({'playlist': playlist.name, 'songs': songs})

# Add a song to a playlist
@app.route('/playlists/<int:playlist_id>/add_song', methods=['POST'])
def add_song_to_playlist(playlist_id):
    global song_id_counter
    playlist = playlists.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    data = request.json
    song_name = data.get('name')
    artist = data.get('artist')
    genre = data.get('genre')
    song_id = song_id_counter
    song_id_counter += 1

    playlist.add_song(song_id, song_name, artist, genre)
    return jsonify({'message': 'Song added to playlist', 'song_id': song_id}), 201

# Remove a song from a playlist
@app.route('/playlists/<int:playlist_id>/remove_song', methods=['DELETE'])
def remove_song_from_playlist(playlist_id):
    playlist = playlists.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    data = request.json
    song_id = data.get('song_id')
    if playlist.remove_song(song_id):
        return jsonify({'message': 'Song removed from playlist'})
    else:
        return jsonify({'error': 'Song not found in playlist'}), 404

# Search songs in a playlist
@app.route('/playlists/<int:playlist_id>/search', methods=['GET'])
def search_song_in_playlist(playlist_id):
    playlist = playlists.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    search_key = request.args.get('key')
    search_type = request.args.get('type', 'name')  # Search by name by default
    search_results = playlist.search_song(search_key, search_type)

    if not search_results:
        return jsonify({'error': 'No songs found matching the search criteria'}), 404

    results = []
    for song in search_results:
        results.append({
            'song_id': song.song_id,
            'name': song.name,
            'artist': song.artist,
            'genre': song.genre
        })

    return jsonify({'results': results})

# Sort songs in a playlist
@app.route('/playlists/<int:playlist_id>/sort', methods=['GET'])
def sort_playlist(playlist_id):
    playlist = playlists.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    sort_key = request.args.get('key', 'name')  # Sort by name by default
    playlist.sort_playlist(sort_key)

    # Traverse playlist and list songs in sorted order
    current = playlist.head
    sorted_songs = []
    while current:
        sorted_songs.append({
            'song_id': current.song_id,
            'name': current.name,
            'artist': current.artist,
            'genre': current.genre
        })
        current = current.next

    return jsonify({'message': f'Playlist sorted by {sort_key}', 'songs': sorted_songs})

if __name__ == '__main__':
    app.run(debug=True)
