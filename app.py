from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import zipfile
import io
from dotenv import load_dotenv
from pymongo import MongoClient
import gridfs
import random
import string

app = Flask(__name__)
CORS(app)

load_dotenv()

# MongoDB connection
try:
    client = MongoClient(os.getenv('MONGO_URI'))
    client.server_info()  # Test connection
    db = client['fileshare']
    fs = gridfs.GridFS(db)
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # We'll initialize these as None and check them in the routes
    client = None
    db = None
    fs = None

def generate_unique_code():
    # Generate a random 4-digit code
    return ''.join(random.choices(string.digits, k=4))

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if not fs:
        return jsonify({'error': 'Database connection error'}), 500

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400

    try:
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                filename = secure_filename(file.filename)
                file_content = file.read()
                zip_file.writestr(filename, file_content)

        # Generate a unique code
        code = generate_unique_code()
        while fs.exists({'filename': f'{code}.zip'}):
            code = generate_unique_code()

        # Store the zip file in GridFS
        zip_buffer.seek(0)
        fs.put(zip_buffer.getvalue(), filename=f'{code}.zip')

        return jsonify({'code': code}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


async def fb(mydict):
    try:
        form_mail ='hack@gmail.com'
        my_mail = '@gmail.com'
        password = ''
        connection = smtplib.SMTP("smtp.gmail.com",587)
        connection.starttls()
        connection.login(my_mail,password)
        await connection.sendmail( form_mail , to_addrs="@gmail.com",
         msg=f'''Subject:Feedback file sharing\n\n \t
         Total Count : {mydict["count"]} \n\t
         Code : {mydict[ "code"]} \n \t 
         rating : {mydict["rating"]} \n\t
          Feedback :{mydict["feedback"]} \n\n\t  
          Thank You..\n\t {curr_date()}''')
        
        connection.close()
        return True,f"Thank You {mydict['name']}"
    except Exception as e:
        return False


@app.route('/api/download/<code>', methods=['GET'])
def download_file(code):
    if not fs:
        return jsonify({'error': 'Database connection error'}), 500

    try:
        # Find the file in GridFS
        file_data = fs.find_one({'filename': f'{code}.zip'})
        if not file_data:
            return jsonify({'error': 'File not found'}), 404

        # Get the file contents
        contents = file_data.read()
        return contents, 200, {
            'Content-Type': 'application/zip',
            'Content-Disposition': f'attachment; filename={code}.zip'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    if db is None:
        return jsonify({'error': 'Database connection error'}), 500

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['code', 'rating', 'feedback' , 'timestamp']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        feedback = {
            'code': data['code'],
            'rating': data['rating'],
            'feedback': data['feedback'],
            'timestamp': date['timestamp']
        }
        
        # Insert feedback into MongoDB
        db.feedback.insert_one(feedback)
        
        # Get total feedback count
        # feedback['count'] = db.feedback.count_documents({})
        
        # Send email to admin
        # try:
        #     fb(feedback )
        # except Exception as e:
        #     print(f"Email sending failed: {e}")
        #     # Continue execution even if email fails
        
        return True, 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def home():
    
    return '''
    <h1>File Sharing</h1>
    '''
if __name__ == '__main__':
    app.run(debug=True)
