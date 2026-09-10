from flask import Flask, render_template, request, jsonify
from markupsafe import Markup
import json
import subprocess
import os
import threading
import markdown

# Import the gen function from FSM_Gen module
import sys
sys.path.append('..')
sys.path.append('../baseclass')
sys.path.append('../autodesign')
from baseclass.FSM_Gen import gen
from baseclass.MultiAgent import MultiAgentSystem
from CaseGen import case_gen
from evolution.general_evolve import update_mas
from autodesign.evaluate.general_test import run_mas_test
import traceback
from web.content.introduction import INTRODUCTION_CONTENT

app = Flask(__name__)

# Initialize MultiAgentSystem instance
mas_instance = None
mas_lock = threading.Lock()

# Route: Home page
@app.route('/')
def home():
    html_content = markdown.markdown(INTRODUCTION_CONTENT, extensions=['fenced_code', 'tables', 'codehilite'])
    return render_template('home.html', content=Markup(html_content))

# Route: Demo page
@app.route('/demo')
def demo():
    return render_template('index.html')

# Route: Generate MAS
@app.route('/design', methods=['POST'])
def design():
    task_description = request.form.get('task_description')
    mas_path = os.path.join('..', 'examples', 'tests1.json')

    # Call the gen function from FSM_Gen.py to generate MAS
    try:
        agent_dict, fsm, token_cost = gen(task=task_description, mas_saving_path=mas_path)
        if agent_dict is None or fsm is None:
            return jsonify({'status': 'error', 'message': 'FSM generation failed.'})

        return jsonify({
            'status': 'success',
            'message': 'MAS generated successfully.',
            'token_cost': token_cost
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating MAS: {str(e)}'})

# Route: Get FSM data
@app.route('/get_fsm', methods=['GET'])
def get_fsm():
    mas_path = os.path.join('..', 'examples','tests1.json')
    try:
        with open(mas_path, 'r') as f:
            mas_data = json.load(f)
        return jsonify(mas_data)
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'FSM file not found.'})
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'FSM file format error.'})

# Route: Run test during deployment
@app.route('/deploy', methods=['POST'])
def deploy():
    case_input = request.form.get('case_input')
    mas_path = os.path.join('..', 'examples', 'tests1.json')
    if not case_input:
        return jsonify({'status': 'error', 'message': 'Missing case_input parameter.'})

    # Start a background thread to run the test
    test_thread = threading.Thread(target=run_mas_test, args=(mas_path, case_input))
    test_thread.start()

    return jsonify({'status': 'success', 'message': 'Test has started.'})

# Route: Get running log
@app.route('/get_log', methods=['GET'])
def get_log():
    log_path = os.path.join('..', 'workspace', 'running_log.log')
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        return jsonify({'log': log_content})
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'No log file found.'})

# Route: Get current state
@app.route('/current_state', methods=['GET'])
def current_state():
    state_path = os.path.join('..', 'workspace', 'current_state.json')
    try:
        with open(state_path, 'r') as f:
            state_data = json.load(f)
        return jsonify({'current_state': state_data.get('state_id', None)})
    except FileNotFoundError:
        return jsonify({'current_state': None})
    except json.JSONDecodeError:
        return jsonify({'current_state': None})

# Route: Generate test cases
@app.route('/generate_cases', methods=['POST'])
def generate_cases():
    mas_path = os.path.join('..', 'examples', 'tests1.json')
    cases_path = os.path.join('..', 'examples', 'test_cases.jsonl')
    try:
        with open(mas_path, 'r') as f:
            mas_dict = json.load(f)
        task_description = mas_dict.get('task_description', '')
        cases = case_gen(task_description, mas_path)
        with open(cases_path, 'w') as f:
            for case in cases:
                f.write(json.dumps(case) + '\n')
        return jsonify({'status': 'success', 'message': 'Test cases generated successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating test cases: {str(e)}'})

# Route: Get test cases
@app.route('/get_test_cases', methods=['GET'])
def get_test_cases():
    cases_path = os.path.join('..', 'examples', 'test_cases.jsonl')
    try:
        with open(cases_path, 'r') as f:
            cases = [json.loads(line) for line in f]
        return jsonify({'status': 'success', 'test_cases': cases})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error getting test cases: {str(e)}'})

# Route: Evolve MAS
@app.route('/evolve', methods=['POST'])
def evolve():
    # Start a background thread to run the evolution task
    evolve_thread = threading.Thread(target=run_evolve)
    evolve_thread.start()

    return jsonify({'status': 'success', 'message': 'Multi-agent system evolution has started.'})

# Function to run evolution in the background
def run_evolve():
    mas_path = os.path.join('..', 'examples', 'tests1.json')
    cases_path = os.path.join('..', 'examples', 'test_cases.jsonl')

    try:
        with mas_lock:
            mas_instance = MultiAgentSystem.load_from_file(mas_path)
        failed_logs = []

        with open(cases_path, 'r') as f:
            cases = [json.loads(line) for line in f]

        for case in cases:
            mas_instance.start(user_input=case)
            log = mas_instance.get_running_log()
            if "|completed|" not in log:
                failed_logs.append(log)

        if failed_logs:
            # Read the previous task description from mas_path
            with open(mas_path, 'r') as f:
                mas_dict = json.load(f)
            task_description = mas_dict.get('task_description', '')

            # Use the previous task description and failed logs to update the MAS
            update_mas(task_description, mas_path, failed_logs)
            with open('/Users/a11/Desktop/MetaAgent/MetaAgent_release/workspace/running_log.log', 'a') as log_file:
                log_file.write('MAS evolution completed with failures.\n')
        else:
            with open('/Users/a11/Desktop/MetaAgent/MetaAgent_release/workspace/running_log.log', 'a') as log_file:
                log_file.write('All test cases passed. No evolution needed.\n')
    except Exception as e:
        error_traceback = traceback.format_exc()
        with open('/Users/a11/Desktop/MetaAgent/MetaAgent_release/workspace/running_log.log', 'a') as log_file:
            log_file.write(f'Error during MAS evolution: {str(error_traceback)}\n')

if __name__ == '__main__':
    app.run(debug=True)