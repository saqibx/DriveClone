from flask import Flask, session
from pymongo import MongoClient
from routes.Upload import upload_bp
from routes.home import home_bp
from routes.login import login_bp
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

app = Flask(__name__)
client = MongoClient(os.environ.get('MONGO_URI'), ssl = True)

db = client['sadsDB']
data_collection = db['AIDB']

app.register_blueprint(upload_bp)
app.register_blueprint(home_bp)
app.register_blueprint(login_bp)
app.secret_key = '1234'


# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)


