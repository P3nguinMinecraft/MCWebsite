from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.utils import secure_filename
from functools import wraps
import database

app = Flask(__name__)
app.secret_key = os.urandom(16)

CONFIG = {
    'server_name': 'Minecraft Server',
    'server_ip': 'mason.run.place',
    'discord_invite': 'https://discord.gg/VD5F5sSUTH',
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'max_file_size': 20 * 1024 * 1024,  # 20 MB
    'directories': {
        'pictures': 'static/pictures',
        'mods': 'static/mods.txt'
    }
}

database.init_db()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in CONFIG['allowed_extensions']

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html', config=CONFIG)

def load_mods():
    """Load mods from static/mods.txt file"""
    mods = []
    mods_file = os.path.join(app.root_path, CONFIG['directories']['mods'])
    
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
    """Get all image files from the pictures folder"""
    pictures_path = os.path.join(app.root_path, CONFIG['directories']['pictures'])
    if os.path.exists(pictures_path):
        filenames = [f for f in os.listdir(pictures_path) if allowed_file(f.lower())]
        images = []
        for filename in filenames:
            metadata = database.get_image_metadata(filename)
            images.append({
                'filename': filename,
                'title': metadata['title'] or filename,
                'description': metadata['description'] or ''
            })
    else:
        images = []
    
    is_admin = 'admin_logged_in' in session
    return render_template('pictures.html', config=CONFIG, images=images, is_admin=is_admin)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if database.verify_admin(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('pictures'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('admin_login.html', config=CONFIG)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Successfully logged out.', 'success')
    return redirect(url_for('pictures'))

@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.root_path, CONFIG['directories']['pictures'], filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        database.update_image_metadata(filename, filename, '')
        
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/admin/delete/<filename>', methods=['DELETE'])
@login_required
def delete_image(filename):
    filepath = os.path.join(app.root_path, CONFIG['directories']['pictures'], filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        database.delete_image_metadata(filename)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/admin/update-metadata', methods=['POST'])
@login_required
def update_metadata():
    data = request.json
    filename = data.get('filename')
    title = data.get('title')
    description = data.get('description')
    
    if not filename:
        return jsonify({'success': False, 'error': 'No filename provided'}), 400
    
    database.update_image_metadata(filename, title, description)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
