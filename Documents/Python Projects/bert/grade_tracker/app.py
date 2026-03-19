from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'grade_tracker_secret_2024'

DATA_FILE = 'grades_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"subjects": [], "assignments": [], "goals": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_gpa(grade):
    if grade >= 97: return 4.0
    elif grade >= 93: return 4.0
    elif grade >= 90: return 3.7
    elif grade >= 87: return 3.3
    elif grade >= 83: return 3.0
    elif grade >= 80: return 2.7
    elif grade >= 77: return 2.3
    elif grade >= 73: return 2.0
    elif grade >= 70: return 1.7
    elif grade >= 67: return 1.3
    elif grade >= 65: return 1.0
    else: return 0.0

def get_letter(grade):
    if grade >= 93: return 'A'
    elif grade >= 90: return 'A-'
    elif grade >= 87: return 'B+'
    elif grade >= 83: return 'B'
    elif grade >= 80: return 'B-'
    elif grade >= 77: return 'C+'
    elif grade >= 73: return 'C'
    elif grade >= 70: return 'C-'
    elif grade >= 67: return 'D+'
    elif grade >= 65: return 'D'
    else: return 'F'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    data = load_data()
    # Enrich subjects with computed stats
    for subject in data['subjects']:
        sid = subject['id']
        assignments = [a for a in data['assignments'] if a['subject_id'] == sid and a.get('graded', False)]
        if assignments:
            # Weighted average
            total_weight = sum(a.get('weight', 1) for a in assignments)
            weighted_sum = sum(a['score'] * a.get('weight', 1) for a in assignments)
            avg = weighted_sum / total_weight if total_weight > 0 else 0
            subject['average'] = round(avg, 1)
            subject['letter'] = get_letter(avg)
            subject['gpa'] = calculate_gpa(avg)
        else:
            subject['average'] = None
            subject['letter'] = 'N/A'
            subject['gpa'] = None
        subject['assignments'] = [a for a in data['assignments'] if a['subject_id'] == sid]
        subject['goal'] = data['goals'].get(sid)
    return jsonify(data)

@app.route('/api/subjects', methods=['POST'])
def add_subject():
    data = load_data()
    body = request.json
    subject = {
        'id': str(datetime.now().timestamp()).replace('.', ''),
        'name': body['name'],
        'color': body.get('color', '#6366f1'),
        'credits': body.get('credits', 3),
        'created': datetime.now().isoformat()
    }
    data['subjects'].append(subject)
    save_data(data)
    return jsonify(subject)

@app.route('/api/subjects/<sid>', methods=['DELETE'])
def delete_subject(sid):
    data = load_data()
    data['subjects'] = [s for s in data['subjects'] if s['id'] != sid]
    data['assignments'] = [a for a in data['assignments'] if a['subject_id'] != sid]
    if sid in data['goals']:
        del data['goals'][sid]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/assignments', methods=['POST'])
def add_assignment():
    data = load_data()
    body = request.json
    assignment = {
        'id': str(datetime.now().timestamp()).replace('.', ''),
        'subject_id': body['subject_id'],
        'name': body['name'],
        'type': body.get('type', 'assignment'),
        'score': body.get('score'),
        'max_score': body.get('max_score', 100),
        'weight': body.get('weight', 1),
        'graded': body.get('graded', False),
        'due_date': body.get('due_date'),
        'created': datetime.now().isoformat()
    }
    data['assignments'].append(assignment)
    save_data(data)
    return jsonify(assignment)

@app.route('/api/assignments/<aid>', methods=['PUT'])
def update_assignment(aid):
    data = load_data()
    body = request.json
    for a in data['assignments']:
        if a['id'] == aid:
            a.update(body)
            break
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/assignments/<aid>', methods=['DELETE'])
def delete_assignment(aid):
    data = load_data()
    data['assignments'] = [a for a in data['assignments'] if a['id'] != aid]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/goals/<sid>', methods=['POST'])
def set_goal(sid):
    data = load_data()
    body = request.json
    data['goals'][sid] = body['goal']
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    all_grades = []
    for subject in data['subjects']:
        sid = subject['id']
        assignments = [a for a in data['assignments'] if a['subject_id'] == sid and a.get('graded')]
        if assignments:
            total_weight = sum(a.get('weight', 1) for a in assignments)
            weighted_sum = sum(a['score'] * a.get('weight', 1) for a in assignments)
            avg = weighted_sum / total_weight if total_weight > 0 else 0
            credits = subject.get('credits', 3)
            all_grades.append({'avg': avg, 'credits': credits, 'name': subject['name']})

    cumulative_gpa = 0
    if all_grades:
        total_credits = sum(g['credits'] for g in all_grades)
        weighted_gpa = sum(calculate_gpa(g['avg']) * g['credits'] for g in all_grades)
        cumulative_gpa = round(weighted_gpa / total_credits, 2) if total_credits > 0 else 0

    pending = [a for a in data['assignments'] if not a.get('graded') and a.get('due_date')]
    pending.sort(key=lambda x: x.get('due_date', ''))

    return jsonify({
        'cumulative_gpa': cumulative_gpa,
        'total_subjects': len(data['subjects']),
        'total_assignments': len(data['assignments']),
        'graded': len([a for a in data['assignments'] if a.get('graded')]),
        'pending': pending[:5],
        'grade_distribution': all_grades
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
