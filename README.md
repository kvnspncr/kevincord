<h2>kevincord</h2>
<p>Kevincord is a simple API wrapper for Discord I originally wrote to help my selfbot work. Feel free to use it as you like</p>
<h4>Example usage</h4>
<p>This is for a simple bot</p>


<h2>Using gateway.py</h2>

```python
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
            if command == "ping":
                chid = message.channel_id
                kevincord.send_message("pong!", chid)
    except KeyError:
        print("Invalid message format")
```

<h2>Just using kevincord</h2>

```python
import kevincord as k
token = "your_token"
kevincord = k.Bot()
if kevincord.run(token) and kevincord.on_ready():
    username = kevincord.username()
    print(f"Logged in as {username}")
    kevincord.send_message("hello", "123456789")
```

<p>This is for looking up a user</p>

```python 
import kevincord as k
token = "your_token"
kevincord = k.Check()
if kevincord.run(token) and kevincord.check():
    userid = 123456789
    username, userid, avatar, display = kevincord.lookup(userid)
    print(f"Username: {username}") 
```
