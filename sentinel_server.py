from flask import Flask, request, redirect, url_for, render_template_string
import json
import os

app = Flask(__name__)
TASKS_FILE = "sentinel_tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/', methods=['GET'])
def index():
    tasks = load_tasks()
    return render_template_string("""
    <h1>Sentinel Tasks</h1>
    <form method="POST" action="/add">
        <input name="url" placeholder="URL" required>
        <input name="selector" placeholder="Selector" required>
        <select name="method">
            <option value="headless">headless</option>
            <option value="headed">headed</option>
        </select>
        <input name="sleep" placeholder="Sleep (s)" required type="number">
        <input name="webhook" placeholder="Webhook URL" required>
        <input name="frequency" placeholder="Frequency (s)" required type="number">
        <label>
            <input type="checkbox" name="report_only_if_missing" value="1">
            Only Report If Missing Element
        </label>
        <button type="submit">Add Task</button>
    </form>
    <hr>
    <ul>
    {% for task in tasks %}
        <li>
            <code>{{ task['url'] }}</code> | {{ task['selector'] }} | {{ task['method'] }} | every {{ task['frequency'] }}s
            {% if task.get('report_only_if_missing') %}
                | <strong>Only If Missing</strong>
            {% else %}
                | <em>Always Report</em>
            {% endif %}
            <form method="POST" action="/delete" style="display:inline;">
                <input type="hidden" name="url" value="{{ task['url'] }}">
                <button type="submit">Delete</button>
            </form>
        </li>
    {% endfor %}
    </ul>
    """, tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task = {
        "url": request.form['url'],
        "selector": request.form['selector'],
        "method": request.form['method'],
        "sleep": int(request.form['sleep']),
        "webhook": request.form['webhook'],
        "frequency": int(request.form['frequency']),
        "report_only_if_missing": 'report_only_if_missing' in request.form,
        "last_checked": 0
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    url = request.form['url']
    tasks = load_tasks()
    tasks = [t for t in tasks if t['url'] != url]
    save_tasks(tasks)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
