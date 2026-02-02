# MCWebsite
Website for a Minecraft Server by penguin

## Setup

### 1. Install Flask
```bash
pip install -r requirements.txt
```

### 2. Update Config
Edit lines in `app.py`:
```python
'server_name': 'your-server-name',
'server_ip': 'your-server-ip',
'discord_invite': 'https://discord.gg/YOUR-INVITE-CODE',
```

### 3. Run the Server
```bash
python app.py
```

Visit: http://localhost:8000

### 4. Admin Login
Visit: http://localhost:8000/admin/login

**Default credentials:**
- Username: `admin`
- Password: `pass123`

**CHANGE THIS PASSWORD IMMEDIATELY!**

### 5. Production
Run the website with a WSGI server like gunicorn:
```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
```