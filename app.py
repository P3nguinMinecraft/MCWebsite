from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from functools import wraps
import database
from files import FileManager

app = Flask(__name__)
app.secret_key = os.urandom(16)

file = FileManager(app.root_path)
database.init_db()


def get_config():
    """Load config from data/config.json"""
    return file.load_config()


def allowed_file(filename):
    config = get_config()
    exts = set(e.lower() for e in config.get('allowed_extensions', ['png','jpg','jpeg','gif','webp']))
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in exts


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def replace_tokens(value, config):
    """Replace {ip} and {name} tokens in info row values"""
    return (value
            .replace('{ip}', config.get('server_ip', ''))
            .replace('{name}', config.get('server_name', '')))


# ── Public routes ─────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html', config=get_config())


@app.route('/discord')
def discord():
    return redirect(get_config().get('discord_invite', '/'))


@app.route('/data/pictures/<filename>')
def serve_picture(filename):
    return send_from_directory(file.get_pictures_dir(), filename)


@app.route('/about')
def about():
    config = get_config()
    details = file.load_details()
    mods_txt    = file.load_mods()
    custom = file.load_custom()

    details = {
        'info_rows': [
            {'label': row['label'], 'value': replace_tokens(row['value'], config)}
            for row in details.get('info_rows', [])
        ]
    }

    mods = []
    for line in mods_txt.splitlines():
        line = line.strip()
        if line:
            parts = line.rsplit(' ', 1)
            mods.append({'name': parts[0], 'version': parts[1] if len(parts) == 2 else ''})

    return render_template('about.html', config=config, details=details, mods=mods, custom=custom)


@app.route('/pictures')
def pictures():
    config      = get_config()
    pics_dir    = file.get_pictures_dir()
    images      = []

    if os.path.exists(pics_dir):
        for filename in os.listdir(pics_dir):
            if allowed_file(filename):
                meta = database.get_image_metadata(filename)
                images.append({
                    'filename':    filename,
                    'title':       meta['title'] or filename,
                    'description': meta['description'] or ''
                })

    is_admin = 'admin_logged_in' in session
    return render_template('pictures.html', config=config, images=images, is_admin=is_admin)


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if database.verify_admin(username, password):
            session['admin_logged_in'] = True
            session['admin_username']  = username
            return redirect(url_for('admin_panel'))
        flash('Invalid credentials. Please try again.', 'error')
    return render_template('admin_login.html', config=get_config())


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('pictures'))


@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    config = get_config()
    if request.method == 'POST':
        current  = request.form.get('current_password')
        new_pw   = request.form.get('new_password')
        confirm  = request.form.get('confirm_password')
        username = session.get('admin_username')

        if not database.verify_admin(username, current):
            flash('Current password is incorrect.', 'error')
        elif new_pw != confirm:
            flash('New passwords do not match.', 'error')
        elif len(new_pw) < 4:
            flash('Password must be at least 4 characters.', 'error')
        elif database.change_password(username, new_pw):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Failed to change password.', 'error')
    return render_template('change_password.html', config=config)


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
def admin_panel():
    return render_template('admin.html', config=get_config())


# ── Admin data API ────────────────────────────────────────────────────────────

@app.route('/admin/api/config', methods=['GET'])
@login_required
def api_get_config():
    return jsonify(file.load_config())


@app.route('/admin/api/config', methods=['POST'])
@login_required
def api_save_config():
    data = request.json or {}
    # Validate / coerce fields
    config = {
        'server_name':       str(data.get('server_name', 'Minecraft Server')),
        'server_ip':         str(data.get('server_ip', '')),
        'discord_invite':    str(data.get('discord_invite', '')),
        'allowed_extensions': [str(e).lower() for e in data.get('allowed_extensions', ['png','jpg','jpeg','gif','webp'])],
        'max_file_size':     int(data.get('max_file_size', 20)),
        'file_size_unit':    str(data.get('file_size_unit', 'MB')).upper(),
    }
    file.save_config(config)
    return jsonify({'success': True})


@app.route('/admin/api/details', methods=['GET'])
@login_required
def api_get_details():
    return jsonify(file.load_details())


@app.route('/admin/api/details', methods=['POST'])
@login_required
def api_save_details():
    data = request.json or {}
    rows = [{'label': str(r.get('label','')), 'value': str(r.get('value',''))}
            for r in data.get('info_rows', [])]
    file.save_details({'info_rows': rows})
    return jsonify({'success': True})


@app.route('/admin/api/mods', methods=['GET'])
@login_required
def api_get_mods():
    return jsonify({'content': file.load_mods()})


@app.route('/admin/api/mods', methods=['POST'])
@login_required
def api_save_mods():
    data = request.json or {}
    file.save_mods(data.get('content', ''))
    return jsonify({'success': True})


@app.route('/admin/api/custom', methods=['GET'])
@login_required
def api_get_custom():
    return jsonify(file.load_custom())


@app.route('/admin/api/custom', methods=['POST'])
@login_required
def api_save_custom():
    data = request.json or {}
    sections = []
    for s in data.get('sections', []):
        rows = [{'label': str(r.get('label','')), 'value': str(r.get('value',''))}
                for r in s.get('rows', [])]
        sections.append({'name': str(s.get('name','')), 'rows': rows})
    file.save_custom({'sections': sections})
    return jsonify({'success': True})


# ── Image API ─────────────────────────────────────────────────────────────────
@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(file.get_pictures_dir(), filename)

        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{name}_{counter}{ext}"
                filepath = os.path.join(file.get_pictures_dir(), filename)
                counter += 1

        uploaded_file.save(filepath)
        database.update_image_metadata(filename, filename, '')
        return jsonify({'success': True, 'filename': filename})

    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/admin/delete/<filename>', methods=['DELETE'])
@login_required
def delete_image(filename):
    filepath = os.path.join(file.get_pictures_dir(), filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        database.delete_image_metadata(filename)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'File not found'}), 404


@app.route('/admin/update-metadata', methods=['POST'])
@login_required
def update_metadata():
    data = request.json or {}
    filename    = data.get('filename')
    title       = data.get('title')
    description = data.get('description')
    if not filename:
        return jsonify({'success': False, 'error': 'No filename provided'}), 400
    database.update_image_metadata(filename, title, description)
    resp = jsonify({'success': True})
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
