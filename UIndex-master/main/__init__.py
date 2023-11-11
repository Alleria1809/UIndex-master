from flask import Flask, render_template


app = Flask(__name__, static_folder='./static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SECRET_KEY'] = '5a0d3c614b8f1a2e7107ea71'

# please don't move this line --- will cause circular import
from main import routes



