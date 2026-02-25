import os
import sqlite3
import csv
import io
import zipfile
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd
from io import StringIO

app = Flask(__name__)
app.config['DATABASE'] = 'downloads.db'

# Tracked datasets (UUID: name)
TRACKED_DATASETS = {
    '6c343726-1e92-451a-876a-76e17d398a1c': 'CPCAD',
    '47caa405-be2b-4e9e-8f53-c478ade2ca74': 'Critical Habitat',
    'd5af4ac5-ebdb-4645-bb0a-8ec5cac5e29f': 'CNWI'
}

ANALYTICS_DATASET_ID = '2916fad5-ebcc-4c86-b0f3-4f619b29f412'

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS monthly_downloads
                 (id INTEGER PRIMARY KEY, dataset_uuid TEXT, year INTEGER, month INTEGER, 
                  downloads INTEGER, status TEXT, source TEXT, UNIQUE(dataset_uuid, year, month))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY, dataset_uuid TEXT, year INTEGER, month INTEGER, 
                  text TEXT, created_at TEXT, author TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ingestion_runs
                 (id INTEGER PRIMARY KEY, ran_at TEXT, source_type TEXT, source_url TEXT, 
                  result TEXT, log TEXT)''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard."""
    return render_template('index.html', datasets=TRACKED_DATASETS)

@app.route('/api/data')
def get_data():
    """Get monthly download data."""
    conn = get_db()
    c = conn.cursor()
    
    data = {}
    for uuid, name in TRACKED_DATASETS.items():
        c.execute('SELECT year, month, , status FROM monthly_ WHERE dataset_uuid = ? ORDER BY year, month', (uuid,))
        rows = c.fetchall()
        data[uuid] = {
            'name': name,
            'months': [dict(row) for row in rows]
        }
    
    conn.close()
    return jsonify(data)

@app.route('/api/dataset/<uuid>')
def get_dataset(uuid):
    """Get data for a specific dataset."""
    if uuid not in TRACKED_DATASETS:
        return jsonify({'error': 'Dataset not found'}), 404
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT year, month, , status FROM monthly_ WHERE dataset_uuid = ? ORDER BY year, month', (uuid,))
    months = [dict(row) for row in c.fetchall()]
    
    c.execute('SELECT text, created_at, author FROM notes WHERE dataset_uuid = ? ORDER BY created_at DESC', (uuid,))
    notes = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'uuid': uuid,
        'name': TRACKED_DATASETS[uuid],
        'months': months,
        'notes': notes
    })

@app.route('/api/notes', methods=['POST'])
def add_note():
    """Add a note to a dataset/month."""
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute('INSERT INTO notes (dataset_uuid, year, month, text, created_at, author) VALUES (?, ?, ?, ?, ?, ?)',
              (data.get('dataset_uuid'), data.get('year'), data.get('month'), 
               data.get('text'), datetime.now().isoformat(), 'user'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh data from Open Government Analytics."""
    try:
        # Download Top 100 CSV
        top100_url = 'https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/ba980e38-f110-466a-ad92-3ee0d5a60d49/download/opendataportal.siteanalytics.top100datasets.bilingual.csv'
        response = requests.get(top100_url)
        response.raise_for_status()
        
        conn = get_db()
        c = conn.cursor()
        
        # Parse CSV
        lines = response.text.split('\n')
        reader = csv.DictReader(lines)
        
        for row in reader:
            if not row or 'id' not in row:
                continue
            
            dataset_id = row['id'].strip()
            if dataset_id not in TRACKED_DATASETS:
                continue
            
            try:
                downloads = int(row.get('downloads_telechargements', 0))
                month = int(row.get('month_mois', 0))
                year = int(row.get('year_annee', 0))
                
                if month > 0 and year > 0:
                    c.execute('''INSERT OR REPLACE INTO monthly_downloads 
                                 (dataset_uuid, year, month, downloads, status, source) 
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (dataset_id, year, month, downloads, 'present_in_top100', 'top100_current'))
            except (ValueError, TypeError):
                continue
        
        conn.commit()
        
        # Log the ingestion
        c.execute('INSERT INTO ingestion_runs (ran_at, source_type, source_url, result, log) VALUES (?, ?, ?, ?, ?)',
                  (datetime.now().isoformat(), 'top100_current', top100_url, 'success', 'Refreshed current month data'))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Data refreshed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export')
def export_csv():
    """Export data as CSV."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT dataset_uuid, year, month, downloads, status 
                 FROM monthly_downloads ORDER BY year DESC, month DESC, dataset_uuid''')
    rows = c.fetchall()
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Dataset', 'Year', 'Month', 'Downloads', 'Status'])
    
    for row in rows:
        dataset_name = TRACKED_DATASETS.get(row['dataset_uuid'], row['dataset_uuid'])
        writer.writerow([dataset_name, row['year'], row['month'], row['downloads'], row['status']])
    
    return output.getvalue(), 200, {'Content-Disposition': 'attachment; filename=downloads.csv'}

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
