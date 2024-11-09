from flask import Flask, request, jsonify, send_from_directory
import subprocess  # Ensure this import is included

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/run_playbook', methods=['POST'])
def run_playbook():
    playbook = request.json.get('playbook')
    valid_playbooks = [
        'firmware_Check_Upgrade.yml', 'vlan.yml', 'interface_status.yml',
        'backup_config.yml', 'inventory_device_info.yml'
    ]
    if playbook not in valid_playbooks:
        return jsonify({'error': 'Invalid playbook name'}), 400
    result = subprocess.run(['ansible-playbook', playbook], capture_output=True, text=True)
    return jsonify({'output': result.stdout, 'error': result.stderr})

if __name__ == '__main__':
    app.run(debug=True)
