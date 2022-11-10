from flask import Blueprint, jsonify, abort, make_response, request
from app.models.task import Task
from app import db
from datetime import datetime
import requests
import os

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

#helper function
def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"message": f"{cls.__name__} {model_id} is invalid"}, 400))

    model = cls.query.get(model_id)

    if not model:
        abort(make_response({"message": f"{cls.__name__} {model_id} not found"}, 404))
    
    return model


@task_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))

    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({
        "task": {
            "id" : new_task.task_id,
            "title" : new_task.title,
            "description" : new_task.description,
            "is_complete" : False
        }
    }), 201)


@task_bp.route("", methods=["GET"])
def get_all():
    task_query = Task.query
    title_query = request.args.get("sort")

    if title_query == "asc":
        task_query = Task.query.order_by(Task.title)
    if title_query == "desc":
        task_query = Task.query.order_by(Task.title.desc())

    tasks = task_query.all()
    task_response = [task.to_dict() for task in tasks]

    return jsonify(task_response)


@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.is_complete = False

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response(jsonify({"details" : f"Task 1 \"{task.title}\" successfully deleted"})), 200


#helper function
def post_to_slack(task):
    URL = "https://slack.com/api/chat.postMessage"

    params = {
        "channel" : "task-notifications",
        "text" : f"Someone just completed the task {task.title}"
    }

    headers = {"Authorization": os.environ.get("API_KEY")}

    requests.post(URL, json=params, headers=headers)


@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()

    db.session.commit()

    post_to_slack(task)

    return {"task": {
    "id": task.task_id,
    "title": task.title,
    "description": task.description,
    "is_complete": True
    } }


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None

    db.session.commit()

    return {"task": {
    "id": task.task_id,
    "title": task.title,
    "description": task.description,
    "is_complete": False
    } }
