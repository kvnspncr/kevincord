import asyncio
import json
import websockets
import kevincord as k 
import time
import shlex
import requests
import os 
wsurl = "wss://gateway.discord.gg/?v=9&encoding=json"
ws = websockets.connect(wsurl)
msg_cache = {}
attach_cache = {}
with open("config.json", "r") as f:
    config = f.read()
j = json.loads(config)
token = j["token"]
prefix = j["prefix"]
webhook = j["webhook"]
kevincord = k.Bot()
if kevincord.run(token) and kevincord.on_ready():
    print(f"="*35)
    print("Bot is ready!")
    print(f"Username: {kevincord.username()}")
    print(f"User ID: {kevincord.getuid()}")
    print(f"="*35)
else:
    exit(1)

w = k.Webhook()
if w.run(webhook) and w.check():
    pass
else:
    exit(1)

c = k.Check()
if c.run(token) and c.check():
    pass
else:
    exit(1)

async def _send(ws, payload):
    wspayload = json.dumps(payload)
    await ws.send(wspayload)

async def _receive(ws):
    event = await ws.recv()
    if event:
        return json.loads(event)


class Message:
    def __init__(self, data):
        self.content = data.get("content", "")
        self.id = data["id"] if "id" in data else None
        self.author_id = data["author"]["id"] if "author" in data and "id" in data["author"] else None
        #self.author_name = data["author"]["username"] if "author" in data and "username" in data["author"] else None
        self.channel_id = data["channel_id"] if "channel_id" in data else None
        self.attachments = data.get("attachments", [])
        if self.attachments:
            self.attachment = self.attachments[0]["url"]
            self.attachment_name = self.attachments[0]["filename"]
        else:
            self.attachment = None
            self.attachment_name = None

async def on_attach_delete(event):
    msgdata = event["d"]
    message = Message(msgdata)
    message_id = message.id 
    cached_attach = attach_cache.pop(message_id, None)
    if cached_attach:
        msg_id = cached_attach["msg_id"]
        msg_auth = cached_attach["msg_auth"]
        msg_url = cached_attach["msg_url"]
        msg_nm = cached_attach["msg_nm"]
        username, userid, avatar, display = c.lookup(msg_auth)
        if msg_id == message_id:
            w.send(f"@everyone\n`Deletion log\nUser: {display}\nUser ID: {userid}\nFilename: {msg_nm}`")
            if msg_url:
                r = requests.get(msg_url)
                with open(f"{msg_nm}", "wb") as f:
                    f.write(r.content)
            w.send_file(msg_nm)
            os.remove(msg_nm)
        else:
            raise TypeError("bad")

async def on_message_delete(event):
    msgdata = event["d"]
    message = Message(msgdata)
    message_id = message.id
    cached_msg = msg_cache.pop(message_id, None)
    if cached_msg:
        msg_id = cached_msg["msg_id"]
        msg_auth = cached_msg["msg_auth"]
        msg_content = cached_msg["msg_content"]
        username, userid, avatar, display = c.lookup(msg_auth)
        if msg_id == message_id: #and msg_auth != kevincord.getuid():
            w.send(f"@everyone\n`Deletion log\nUser: {display}\nUser ID: {userid}\nMessage: {msg_content}`")
    else:
        raise TypeError("bad")

            
async def on_message(event):
    try:
        msgdata = event["d"]
        message = Message(msgdata)
        chid = message.channel_id
        if message.attachments:
            attach_cache[message.id] = {
                'msg_auth': message.author_id,
                'msg_id': message.id, 
                'msg_url': message.attachment, 
                'msg_nm': message.attachment_name
            }
        else:
            msg_cache[message.id] = {
                'msg_id': message.id,
                'msg_content': message.content,
                'msg_auth': message.author_id 
            }

        uid = kevincord.getuid()
        if message.content.startswith(f"{prefix}") and message.author_id == uid:
            command, *args = shlex.split(message.content[1:])
            #this is where you declare your commands
            uid = kevincord.getuid()
            chid = message.channel_id 
            if command == "ping":
                kevincord.send_message("pong", chid)
            
    except KeyError:
        print("Invalid message format")



async def _ping(ws):
    resp = await _receive(ws)
    heartbeat_interval = resp["d"]["heartbeat_interval"]
    interval = int(heartbeat_interval) / 1000
    payload = {
        "op" : 1, 
        "d" : "null",
    }

    await asyncio.sleep(interval)
    await _send(payload)

async def main():
    async with websockets.connect(wsurl) as ws:
        payload = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "linux",
                    "$browser": "firefox",
                    "$device": "pc"
                }
            }
        }
        
        await _send(ws, payload)
        while True:
            await _ping(ws)
            event = await _receive(ws)
            try:
                if event["op"] == 0 and event["t"] == "MESSAGE_CREATE":
                    await on_message(event)
                elif event["op"] == 0 and event["t"] == "MESSAGE_DELETE":
                    try:
                        await on_message_delete(event)
                    except TypeError as e:
                        await on_attach_delete(event)
            except Exception as e:
                pass

if __name__ == "__main__":
    asyncio.run(main())

