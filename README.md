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

## Features
- Upload images through web interface with drag-and-drop support
- Change admin password from the gallery page
- Edit image titles and descriptions inline
- Delete images from the gallery
- Discord redirect at `/discord`
- Images stored in `data/pictures` directory

## File Structure
- `data/pictures/` - Image gallery storage
- `data/server.db` - SQLite database for admin accounts and image metadata
- `static/mods.txt` - Server mod list

### 5. Production
Run the website with a WSGI server like gunicorn:
```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
```