from flask import Blueprint, jsonify, abort, make_response, request
from app.models.task import Task
from app import db
from datetime import datetime
import requests
import os
from app.validate_model import validate_model

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))

    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify(dict(task=new_task.to_dict())), 201)


@bp.route("", methods=["GET"])
def get_all():
    task_query = Task.query
    sort_param = request.args.get("sort")

    if sort_param == "asc":
        task_query = Task.query.order_by(Task.title)
    if sort_param == "desc":
        task_query = Task.query.order_by(Task.title.desc())

    tasks = task_query.all()
    task_response = [task.to_dict() for task in tasks]

    return jsonify(task_response), 200


@bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return jsonify({"task": task.to_dict()}), 200


@bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    if "title" not in request_body or "description" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return jsonify({"task": task.to_dict()}), 200


@bp.route("/<task_id>", methods=["DELETE"])
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

    slack_token = os.environ.get("API_KEY")
    headers = {"Authorization": f"Bearer {slack_token}" }

    requests.post(URL, json=params, headers=headers)


@bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    task.is_complete = True

    db.session.commit()

    post_to_slack(task)

    print(task.is_complete)

    return make_response(jsonify(dict(task = task.to_dict())), 200)

@bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None

    db.session.commit()

    return make_response(jsonify(dict(task = task.to_dict())), 200)

