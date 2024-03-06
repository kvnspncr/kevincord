<h2>kevincord</h2>
<p>Kevincord is a simple API wrapper for Discord I originally wrote to help my selfbot work. Feel free to use it as you like</p>
<h4>Example usage</h4>
<p>This is for a simple bot</p>

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
