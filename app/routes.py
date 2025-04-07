import os
from flask import Blueprint, request, jsonify
from . import db
from .models import User, TaskManager, TaskLogger
import pandas as pd
from datetime import datetime
import redis
from sqlalchemy.orm import joinedload
import json
from .utils.jwt_helper import token_required
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from .utils.jwt_helper import generate_token
from app import limiter

# Initialize Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({'message': 'Welcome to MaidiaAMP !'}), 200


#curl -X POST http://127.0.0.1:5000/create-user \-H "Content-Type: application/json" \ -d '{"username": "john_doe", "password": "secret123"}'

@main.route('/create-user', methods=['POST'])
@limiter.limit("20 per hour")
def create_user():
    data = request.json
    hashed_pw = generate_password_hash(data['password'])
    user = User(username=data['username'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201



@main.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = generate_token(user.id)
    return jsonify({'token': token}), 200


@main.route('/create-task', methods=['POST'])
@token_required
@limiter.limit("40 per day")
def create_task():
    user_id = request.user_id
    data = request.json
    user = User.query.get(user_id)

    task = TaskManager(
        task_name=data['task_name'],
        description=data['description'],
        status=data['status'],
        priority=data['priority'],
        created_at=datetime.strptime(data['created_at'], '%Y-%m-%d').date(),
        assigned_user=user.id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201








@main.route('/create-log', methods=['POST'])
def create_log():
    data = request.json
    task = TaskManager.query.get(data['task_id'])
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    log = TaskLogger(
        task_id=task.id,
        log_message=data['log_message']
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Log created successfully'}), 201


@main.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            user = User.query.filter_by(username=row['assigned_user']).first()
            if not user:
                user = User(username=row['assigned_user'], password=generate_password_hash('default123'))
                db.session.add(user)
                db.session.commit()


            task = TaskManager(
                task_name=row['task_name'],
                description=row['description'],
                status=row['status'] == 'TRUE',
                priority=row['priority'],
                created_at=datetime.strptime(row['created_at'], '%m/%d/%Y').date(),
                assigned_user=user.id
            )
            db.session.add(task)
        db.session.commit()

        return jsonify({'message': 'CSV file successfully uploaded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@main.route('/tasks', methods=['GET'])
def get_tasks():
    date = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if date:
        cache_key = f"tasks:{date}"
        cached_data = r.get(cache_key)
        if cached_data:
            return jsonify(json.loads(cached_data))

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            tasks = TaskLogger.query.join(TaskManager).filter(TaskManager.created_at == date_obj).all()
            result = [
                {
                    'log_id': t.id,
                    'log_message': t.log_message,
                    'task_name': t.task.task_name,
                    'created_at': t.task.created_at.strftime('%Y-%m-%d')
                } for t in tasks
            ]
            r.set(cache_key, json.dumps(result), ex=300)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    logs = TaskLogger.query.paginate(page=page, per_page=per_page, error_out=False)
    result = [
        {
            'log_id': log.id,
            'log_message': log.log_message,
            'task_name': log.task.task_name,
            'created_at': log.task.created_at.strftime('%Y-%m-%d')
        } for log in logs.items
    ]
    return jsonify(result)


@main.route('/task/<int:task_logger_id>', methods=['GET'])
def get_task_log(task_logger_id):
    log = TaskLogger.query.options(
        joinedload(TaskLogger.task).joinedload(TaskManager.user)
    ).filter_by(id=task_logger_id).first()

    if not log:
        return jsonify({'error': 'Task log not found'}), 404

    return jsonify({
        'log_id': log.id,
        'log_message': log.log_message,
        'task': {
            'task_name': log.task.task_name,
            'description': log.task.description,
            'status': log.task.status,
            'priority': log.task.priority,
            'created_at': log.task.created_at.strftime('%Y-%m-%d'),
            'assigned_user': log.task.user.username  # ← changed here
        }
    })


@main.route('/task/<int:task_id>', methods=['DELETE'])
def soft_delete_task(task_id):
    task = TaskManager.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.is_active = False
    db.session.commit()
    return jsonify({'message': 'Task soft deleted'}), 200


