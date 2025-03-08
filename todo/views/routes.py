from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta


api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    completed = True if request.args.get("completed", type=str) else False
    window = request.args.get("window", type=int, default=0)

    if completed:
        todos = [todo for todo in todos if todo.completed]

    if window:
        cur = datetime.now() + timedelta(days=window)
        todos = [todo for todo in todos if todo.deadline_at <= cur]


    todos = [todo.to_dict() for todo in todos]

    return jsonify(todos)


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    valid_keys = {"id", "title", "description", "completed", "deadline_at",
                  "created_at", "updated_at"}
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
        )
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    # Request is malformed
    if todo.title is None:
        return jsonify({'error' : 'Malformed Request'}), 400
        # exit(400)

    # If there are invalid keys, exit, request is malformed
    if set(request.json.keys()) - valid_keys:
        return jsonify({'error' : 'Malformed Request'}), 400
        # exit(400)

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    todo = Todo.query.get(todo_id)

    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    if request.json.get('title') is None:
        return jsonify({'error': 'bad request'}), 400

    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    
    db.session.commit()
    
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    # return jsonify(TEST_ITEM)
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 200

 
