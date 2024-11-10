import logging
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template_string
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Dummy user database
users = {'admin': {'password': 'adminpass'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            logging.info(f'User {username} logged in.')
            return redirect(url_for('index'))
        logging.warning(f'Failed login attempt for username: {username}')
        return 'Invalid credentials', 401
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body class="container">
            <h2 class="my-4">Login</h2>
            <form method="post">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
        </body>
        </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logging.info(f'User {current_user.id} logged out.')
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    logging.info('Serving index.html')
    return send_from_directory('.', 'index.html')

@app.route('/run_playbook', methods=['POST'])
@login_required
def run_playbook():
    logging.info('Received request to run playbook')
    playbook = request.json.get('playbook')
    valid_playbooks = [
        'backup_config.yml', 'device_info.yml', 'device_resources_uptime.yml',
        'error_detection_correction.yml', 'firmware_check_upgrade.yml',
        'interface_status.yml', 'restore_config.yml', 'security_compliance.yml',
        'vlan_config.yml'
    ]
    if playbook not in valid_playbooks:
        logging.error(f'Invalid playbook name: {playbook}')
        return jsonify({'error': 'Invalid playbook name'}), 400
    result = subprocess.run(['ansible-playbook', playbook], capture_output=True, text=True)
    logging.info(f'Playbook {playbook} executed by user {current_user.id}.')
    return jsonify({'output': result.stdout, 'error': result.stderr})

if __name__ == '__main__':
    app.run(debug=True)
