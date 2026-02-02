from flask import Flask, render_template
import os

app = Flask(__name__)

CONFIG = {
    'server_name': 'Minecraft Server',
    'server_ip': 'mason.run.place',
    'discord_invite': 'https://discord.gg/VD5F5sSUTH',
}

@app.route('/')
def home():
    return render_template('home.html', config=CONFIG)

def load_mods():
    mods = []
    mods_file = os.path.join(app.static_folder, 'mods.txt')
    
    if os.path.exists(mods_file):
        with open(mods_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.rsplit(' ', 1)
                    if len(parts) == 2:
                        mods.append({'name': parts[0], 'version': parts[1]})
                    else:
                        mods.append({'name': line, 'version': ''})
    
    return mods

@app.route('/about')
def about():
    mods = load_mods()
    return render_template('about.html', config=CONFIG, mods=mods)

@app.route('/pictures')
def pictures():
    pictures_path = os.path.join(app.static_folder, 'pictures')
    if os.path.exists(pictures_path):
        images = [f for f in os.listdir(pictures_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    else:
        images = []
    
    return render_template('pictures.html', config=CONFIG, images=images)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=443)
