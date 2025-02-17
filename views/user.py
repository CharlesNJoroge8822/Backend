from flask import Blueprint, request, jsonify
from models import User, db
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/users", methods=['POST'])
def create_user():
    get_user_data = request.get_json()  
    
    name = get_user_data.get('name')
    email = get_user_data.get('email')
    password = get_user_data.get('password')
    image = get_user_data.get('image')
    role = get_user_data.get('role', 'Client')  

    # ✅ Check if user already exists
    check_email = User.query.filter_by(email=email).first()
    check_name = User.query.filter_by(name=name).first()

    if check_email or check_name:
        return jsonify({"error": "User with Email or Username already exists"}), 400

    # ✅ Hash password once
    hashed_password = generate_password_hash(password)

    # ✅ Create new user
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        image=image,
        role=role
    )

    # ✅ Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
        "image": new_user.image,
        "created_at": new_user.created_at
    }), 201  


# Read
@user_bp.route("/users/<int:id>", methods=['GET'])
def fetch_users(id):
    get_user = User.query.get(id)

    if get_user is None:
        return jsonify({"Error" : "User With ID not found .."}), 404
    else:
        return get_user

# Update ..
@user_bp.route("/users/<int:id>", methods=['PATCH'])
def update_user(id):
    current_user = User.query.get(id)

    if not current_user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    
    # Validate and update fields if provided
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if username:
        if len(username) < 3:
            return jsonify({"msg": "Username must be at least 3 characters long"}), 400
        current_user.name = username

    if email:
        # Ensure email format is valid
        if "@" not in email or "." not in email:
            return jsonify({"msg": "Invalid email format"}), 400
        
        # Ensure email is unique
        existing_user = User.query.filter_by(email=email).filter(User.id != id).first()
        if existing_user:
            return jsonify({"msg": "Email already in use"}), 409
        
        current_user.email = email

    if password:
        if not re.match(PASSWORD_REGEX, password):
            return jsonify({
                "msg": "Password must be at least 6 characters long, contain one uppercase letter, one number, and one special character (@$!%*?&)"
            }), 400
        
        current_user.password = generate_password_hash(password, method="pbkdf2:sha256")

    # ✅ Commit changes to the database
    db.session.commit()

    return jsonify({
        "msg": "User updated successfully",
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }), 200

# ✅ DELETE USER (Admin Only)
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    current_user = User.query.get()

    if not is_admin(current_user):
        return jsonify({"msg": "Admins only"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if current_user.id == user.id:
        return jsonify({"msg": "Admins cannot delete themselves"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted successfully"}), 200





    

