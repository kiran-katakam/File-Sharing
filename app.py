from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home page showing all folders
@app.route('/')
def home():
    users = os.listdir(UPLOAD_FOLDER)
    return render_template_string('''
        <h1>Available Uploads</h1>
        <ul>
            {% for user in users %}
                <li>
                    {{ user }}
                    <form action="/download/{{ user }}" method="post">
                        <input type="password" name="password" placeholder="Enter password" required>
                        <button type="submit">Download</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
        <hr>
        <a href="/upload">Upload Files</a>
    ''', users=users)

# Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        files = request.files.getlist('files')

        user_folder = os.path.join(UPLOAD_FOLDER, username)
        os.makedirs(user_folder, exist_ok=True)

        with open(os.path.join(user_folder, 'password.txt'), 'w') as f:
            f.write(password)

        for file in files:
            file.save(os.path.join(user_folder, file.filename))

        return redirect(url_for('home'))

    return render_template_string('''
    <h1>Upload Files</h1>
    <form id="uploadForm">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <input type="file" name="files" multiple required><br>
        <button type="submit">Upload</button>
    </form>
    <progress id="progressBar" value="0" max="100" style="width:300px; display:none;"></progress>
    <p id="status"></p>
    <a href="/">Back to Home</a>

    <script>
    const form = document.getElementById('uploadForm');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('status');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();

        xhr.open('POST', '/upload', true);

        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                let percent = (e.loaded / e.total) * 100;
                progressBar.style.display = 'block';
                progressBar.value = percent;
            }
        };

        xhr.onload = function() {
            if (xhr.status == 200) {
                statusText.innerText = "Upload complete!";
                window.location.href = "/";
            } else {
                statusText.innerText = "Upload failed!";
            }
        };

        xhr.send(formData);
    });
    </script>
''')


# Download route
@app.route('/download/<username>', methods=['POST'])
def download(username):
    entered_password = request.form['password']
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    password_file = os.path.join(user_folder, 'password.txt')

    if not os.path.exists(password_file):
        return 'User not found'

    with open(password_file, 'r') as f:
        correct_password = f.read().strip()

    if entered_password != correct_password:
        return 'Wrong password'

    files = os.listdir(user_folder)
    files.remove('password.txt')

    return render_template_string('''
        <h1>Files for {{ user }}</h1>
        <ul>
            {% for file in files %}
                <li><a href="/getfile/{{ user }}/{{ file }}">{{ file }}</a></li>
            {% endfor %}
        </ul>
        <a href="/">Back</a>
    ''', user=username, files=files)

# Serve the actual files
@app.route('/getfile/<user>/<filename>')
def get_file(user, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, user), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
