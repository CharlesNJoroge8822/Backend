from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize Flask App
app = Flask(__name__)

# Database Configuration (Using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models AFTER initializing db to avoid circular imports
from models import User, Space, Booking, Payment, Agreement

# Import and Register Blueprints
from views import user_bp
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)
