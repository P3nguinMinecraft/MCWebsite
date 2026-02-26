import sqlite3
import os
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

DATABASE = 'data/server.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database with required tables"""
    os.makedirs('data', exist_ok=True)
    db = get_db()
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            title TEXT,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.commit()
    db.close()
    
    create_default_admin()

def create_default_admin():
    """Create a default admin account"""
    
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) FROM admins')
    count = cursor.fetchone()[0]
    db.close()
    
    if count == 0:
        create_admin("admin", "pass123")
        print("<!> Default admin created. Change password <!>")
    
def create_admin(username, password):
    db = get_db()
    db.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
    )
    db.commit()
    print(f"Admin created! User: {username}, Password: {password}")
    db.close()

def get_image_metadata(filename):
    """Get metadata for a specific image"""
    db = get_db()
    cursor = db.execute(
        'SELECT title, description FROM images WHERE filename = ?',
        (filename,)
    )
    result = cursor.fetchone()
    db.close()
    
    if result:
        return {'title': result['title'], 'description': result['description']}
    return {'title': None, 'description': None}

def update_image_metadata(filename, title, description):
    """Update metadata for an image"""
    db = get_db()
    
    cursor = db.execute('SELECT id FROM images WHERE filename = ?', (filename,))
    exists = cursor.fetchone()
    
    if exists:
        db.execute(
            'UPDATE images SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE filename = ?',
            (title, description, filename)
        )
    else:
        db.execute(
            'INSERT INTO images (filename, title, description) VALUES (?, ?, ?)',
            (filename, title, description)
        )
    
    db.commit()
    db.close()

def delete_image_metadata(filename):
    """Delete metadata for an image"""
    db = get_db()
    db.execute('DELETE FROM images WHERE filename = ?', (filename,))
    db.commit()
    db.close()

def verify_admin(username, password):
    """Verify admin credentials"""
    
    db = get_db()
    cursor = db.execute(
        'SELECT password_hash FROM admins WHERE username = ?',
        (username,)
    )
    result = cursor.fetchone()
    db.close()
    
    if result and check_password_hash(result['password_hash'], password):
        return True
    return False

def change_password(username, new_password):
    """Change admin password"""
    db = get_db()
    try:
        db.execute(
            'UPDATE admins SET password_hash = ? WHERE username = ?',
            (generate_password_hash(new_password), username)
        )
        db.commit()
        db.close()
        return True
    except:
        db.close()
        return False