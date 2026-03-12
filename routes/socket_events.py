from extensions import socketio
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from flask import request

# Track connections: sid -> {username, rooms: []}
sid_metadata = {}
# Track room population: room_id -> {username: count_of_connections}
room_memberships = {}

@socketio.on('connect')
def handle_connect():
    sid_metadata[request.sid] = {'username': current_user.username, 'rooms': []}

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in sid_metadata:
        username = sid_metadata[sid]['username']
        rooms = sid_metadata[sid]['rooms']
        
        for room in rooms:
            if room in room_memberships and username in room_memberships[room]:
                room_memberships[room][username] -= 1
                if room_memberships[room][username] <= 0:
                    del room_memberships[room][username]
                    emit('message', {'user': 'System', 'message': f'{username} has left the room.'}, room=room)
                
                # Update everyone in the room
                emit('user_list', {'users': list(room_memberships[room].keys())}, room=room)
        
        del sid_metadata[sid]

@socketio.on('join')
def on_join(data):
    room = data['room']
    sid = request.sid
    username = current_user.username
    
    join_room(room)
    
    # Track metadata
    if sid in sid_metadata:
        if room not in sid_metadata[sid]['rooms']:
            sid_metadata[sid]['rooms'].append(room)
    
    # Track room membership
    if room not in room_memberships:
        room_memberships[room] = {}
    
    if username not in room_memberships[room]:
        room_memberships[room][username] = 1
        emit('message', {'user': 'System', 'message': f'{username} has joined the room.'}, room=room)
    else:
        room_memberships[room][username] += 1
    
    emit('user_list', {'users': list(room_memberships[room].keys())}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    sid = request.sid
    username = current_user.username
    
    leave_room(room)
    
    if sid in sid_metadata and room in sid_metadata[sid]['rooms']:
        sid_metadata[sid]['rooms'].remove(room)
        
    if room in room_memberships and username in room_memberships[room]:
        room_memberships[room][username] -= 1
        if room_memberships[room][username] <= 0:
            del room_memberships[room][username]
            emit('message', {'user': 'System', 'message': f'{username} has left the room.'}, room=room)
    
    if room in room_memberships:
        emit('user_list', {'users': list(room_memberships[room].keys())}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    emit('message', {'user': current_user.username, 'message': message}, room=room)
