from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import os
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    with sqlite3.connect('dictionary.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                definition TEXT,
                image TEXT,
                voice TEXT,
                link TEXT,
                nepali_translation TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_tags (
                word_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (word_id) REFERENCES words(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (word_id, tag_id)
            )
        ''')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    with sqlite3.connect('dictionary.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM tags")
        tags = [row[0] for row in cursor.fetchall()]
    
    if request.method == 'POST':
        word = request.form['word']
        definition = request.form['definition']
        tags_selected = request.form.getlist('tags')
        new_tag = request.form.get('new_tag')
        nepali_translation = request.form.get('nepali_translation')
        link = request.form.get('link')

        # Handle file uploads
        image_filename = request.files['image'].filename if 'image' in request.files and request.files['image'].filename else None
        voice_filename = request.files['voice'].filename if 'voice' in request.files and request.files['voice'].filename else None
        
        if image_filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            request.files['image'].save(image_path)
        if voice_filename:
            voice_path = os.path.join(app.config['UPLOAD_FOLDER'], voice_filename)
            request.files['voice'].save(voice_path)
        
        # Fetch translation if not provided
        if not nepali_translation:
            try:
                response = requests.get(f"https://api.mymemory.translated.net/get?q={word}&langpair=en|ne")
                data = response.json()
                nepali_translation = data['responseData']['translatedText']
            except:
                nepali_translation = "Translation not available"
        
        with sqlite3.connect('dictionary.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO words (word, definition, nepali_translation, image, voice, link) VALUES (?, ?, ?, ?, ?, ?)",
                (word, definition, nepali_translation, image_filename, voice_filename, link)
            )
            conn.commit()
            
            cursor.execute("SELECT id FROM words WHERE word=?", (word,))
            word_id = cursor.fetchone()[0]

            if new_tag:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (new_tag,))
                conn.commit()
                cursor.execute("SELECT id FROM tags WHERE name=?", (new_tag,))
                tags_selected.append(new_tag)

            for tag in tags_selected:
                cursor.execute("SELECT id FROM tags WHERE name=?", (tag,))
                tag_id = cursor.fetchone()[0]
                cursor.execute("INSERT OR IGNORE INTO word_tags (word_id, tag_id) VALUES (?, ?)", (word_id, tag_id))
                conn.commit()
        
        return redirect(url_for('index'))

    return render_template('index.html', tags=tags)

@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/search-results', methods=['GET'])
def search_results():
    query = request.args.get('query', '').lower()
    tag = request.args.get('tag', '')
    with sqlite3.connect('dictionary.db') as conn:
        cursor = conn.cursor()
        if tag:
            cursor.execute("""
                SELECT words.word FROM words
                JOIN word_tags ON words.id = word_tags.word_id
                JOIN tags ON word_tags.tag_id = tags.id
                WHERE tags.name = ?
            """, (tag,))
        else:
            cursor.execute("SELECT word FROM words WHERE LOWER(word) LIKE ?", (f"%{query}%",))
        words = [row[0] for row in cursor.fetchall()]
    return jsonify({"words": words})

@app.route('/saved', methods=['GET'])
def saved():
    with sqlite3.connect('dictionary.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM words')
        words = [row[0] for row in cursor.fetchall()]
    
    return render_template('saved.html', words=words)

@app.route('/translate', methods=['GET'])
def translate():
    word = request.args.get('word', '')
    if not word:
        return jsonify({"translation": ""})

    try:
        response = requests.get(f"https://api.mymemory.translated.net/get?q={word}&langpair=en|ne")
        data = response.json()
        translation = data['responseData']['translatedText']
    except:
        translation = "Translation not available"
    return jsonify({"translation": translation})

@app.route('/word/<word>', methods=['GET'])
def word_details(word):
    with sqlite3.connect('dictionary.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words WHERE LOWER(word) = LOWER(?)", (word,))
        result = cursor.fetchone()

    if result:
        word_data = {
            "word": result[1],
            "definition": result[2],
            "image": result[3],
            "voice": result[4],
            "link": result[5],
            "nepali_translation": result[6]
        }
        return render_template('word.html', word_data=word_data)
    else:
        return "Word not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)