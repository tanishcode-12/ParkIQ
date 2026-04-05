from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import json
import random
import math
from models.pricing import run_all_models

app = Flask(__name__)
app.secret_key = 'parking_hackathon_iitg_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user store (extend with DB for production)
USERS = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User',
        'lot_name': 'IIT Guwahati — Lot A',
        'lat': 26.1445,
        'lon': 91.7362
    },
    'owner': {
        'password': generate_password_hash('owner123'),
        'name': 'Lot Owner',
        'lot_name': 'IIT Guwahati — Lot B',
        'lat': 26.1430,
        'lon': 91.7340
    }
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.name = USERS[username]['name']
        self.lot_name = USERS[username]['lot_name']
        self.lat = USERS[username]['lat']
        self.lon = USERS[username]['lon']

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username in USERS and check_password_hash(USERS[username]['password'], password):
            user = User(username)
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# ─── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are accepted'}), 400
    try:
        df = pd.read_csv(file)
        result = run_all_models(df)
        session['parking_data'] = result
        return jsonify({'success': True, 'rows': len(df), 'data': result})
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/api/prices')
@login_required
def get_prices():
    if 'parking_data' in session:
        return jsonify(session['parking_data'])
    return jsonify(generate_mock_data())

@app.route('/api/simulate')
@login_required
def simulate():
    """Append a new simulated data point to existing session data."""
    data = session.get('parking_data', generate_mock_data())
    t = len(data['times'])
    occ_ratio = min(0.5 + t * 0.02 + random.uniform(-0.05, 0.05), 1.0)

    data['times'].append(t)
    data['labels'].append(f'T{t}')
    data['occupancy'].append(int(occ_ratio * 100))
    data['capacity'].append(100)

    prev_baseline = data['baseline'][-1]
    new_baseline = round(prev_baseline + 10 * occ_ratio + random.uniform(-1, 1), 2)
    data['baseline'].append(new_baseline)

    nd = min(occ_ratio + random.uniform(-0.05, 0.05), 1.0)
    new_demand = round(100 * (1 + 0.5 * nd) + random.uniform(-3, 3), 2)
    data['demand'].append(new_demand)

    comp_base = 55 + 8 * occ_ratio
    if occ_ratio > 0.9 and comp_base > 57:
        comp_base -= 5
    elif 57 > comp_base:
        comp_base += 3
    data['competitive'].append(round(comp_base + random.uniform(-2, 2), 2))

    data['comparison'].append({
        'label': f'T{t}',
        'baseline': data['baseline'][-1],
        'demand': data['demand'][-1],
        'competitive': data['competitive'][-1],
        'occupancy': data['occupancy'][-1]
    })

    session['parking_data'] = data
    return jsonify(data)

@app.route('/api/map_data')
@login_required
def map_data():
    return jsonify({
        'your_lot': {
            'name': current_user.lot_name,
            'lat': current_user.lat,
            'lon': current_user.lon,
            'price': round(session.get('parking_data', {}).get('competitive', [58])[-1], 2)
            if session.get('parking_data') else 58.0,
            'occupancy': session.get('parking_data', {}).get('occupancy', [72])[-1]
            if session.get('parking_data') else 72
        },
        'competitors': [
            {'name': 'Competitor A', 'lat': 26.1450, 'lon': 91.7370, 'price': 50, 'occupancy': 65},
            {'name': 'Competitor B', 'lat': 26.1440, 'lon': 91.7340, 'price': 60, 'occupancy': 80},
            {'name': 'Competitor C', 'lat': 26.1430, 'lon': 91.7350, 'price': 70, 'occupancy': 45},
        ]
    })

# ─── Mock Data ─────────────────────────────────────────────────────────────────

def generate_mock_data(n=24):
    baseline, demand, competitive, occupancy = [], [], [], []
    labels = []
    for i in range(n):
        t = i / n
        occ = int(40 + 50 * math.sin(math.pi * t) + random.uniform(-5, 5))
        occ = max(10, min(100, occ))
        occ_r = occ / 100

        b = round(50 + 10 * occ_r * (i + 1) / n + random.uniform(-2, 2), 2)
        nd = occ_r + random.uniform(-0.05, 0.05)
        d = round(100 * (1 + 0.5 * max(0, min(1, nd))) + random.uniform(-3, 3), 2)
        c_base = 50 + 10 * occ_r
        if occ_r > 0.9 and c_base > 55:
            c_base -= 5
        elif 55 > c_base:
            c_base += 3
        c = round(c_base + random.uniform(-2, 2), 2)

        baseline.append(b)
        demand.append(d)
        competitive.append(c)
        occupancy.append(occ)
        labels.append(f'{(8 + i) % 24:02d}:00')

    return {
        'times': list(range(n)),
        'labels': labels,
        'baseline': baseline,
        'demand': demand,
        'competitive': competitive,
        'occupancy': occupancy,
        'capacity': [100] * n,
        'comparison': [
            {'label': labels[i], 'baseline': baseline[i], 'demand': demand[i],
             'competitive': competitive[i], 'occupancy': occupancy[i]}
            for i in range(n)
        ]
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
