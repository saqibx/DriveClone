import datetime

from flask import Flask, request, render_template, Blueprint, send_file, flash, session
from flask import redirect, url_for
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from io import BytesIO
from .auth import hash_password

client = MongoClient(os.environ.get('MONGO_URI'), ssl = True)
db = client['sadsDB']
app = Flask(__name__, template_folder="templates")
upload_bp = Blueprint('upload', __name__)
file_metadata_collection = db['file_metadata']


# Initialize GridFS with the custom collection "AIDB"
fs = gridfs.GridFS(db, collection="AIDB")

@upload_bp.route('/upload', methods=['POST', 'GET'])
def upload_files():
    if request.method == 'POST':
        if "file" not in request.files:
            return "No files in process"
        file = request.files.get('file')


        email = session.get('email')
        password = hash_password(session.get('password'))
        if not email:
            return redirect(url_for('login.login'))

        if file.filename == '':
            return 'No file selected'
        if file:
            # Upload file to GridFS in the custom collection "AIDB"
            file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
            flash("Success! File has been uploaded")

            file_metadata = {
                "file_id": file_id,
                "email": email,
                'filename':file.filename,
                'upload_date': datetime.datetime.utcnow(),
                "content_type": file.content_type
            }
            file_metadata_collection.insert_one(file_metadata)

            return render_template('home.html')
    return render_template('upload.html')

def find_user_files(email):
    user_files = file_metadata_collection.find({'email':email})
    return user_files




@upload_bp.route('/files')
def list_files():
    email = session.get('email')
    # Retrieve all files from the GridFS collection
    files = find_user_files(email)
    file_list = []

    # Extract file information (like name and ID) to pass to the template
    for file in files:
        file_list.append({
            'filename': file.get('filename'),
            'file_id': str(file.get('file_id'))  # Convert ObjectId to string for template
        })

    return render_template('files.html', files=file_list)


@upload_bp.route('/download/<file_id>')
def download_files(file_id):
    try:
        # Convert string ID to ObjectId
        file_id_obj = ObjectId(file_id)

        # Retrieve file using the custom GridFS collection "AIDB"
        grid_out = fs.get(file_id_obj)

        # Create a BytesIO object from the file data
        data = grid_out.read()
        file_stream = BytesIO(data)

        return send_file(
            file_stream,
            download_name=grid_out.filename,
            mimetype=grid_out.content_type,
            as_attachment=True
        )
    except gridfs.errors.NoFile:
        return "File not found", 404
    except Exception as e:
        return f"Error retrieving file: {str(e)}", 500

@upload_bp.route('/delete/<file_id>')
def delete_file(file_id):
    file_id_obj = ObjectId(file_id)

    # Retrieve file using the custom GridFS collection "AIDB"
    file_metadata_collection.delete_one({'file_id':file_id_obj})

    return render_template('files.html')


