from flask import Blueprint, jsonify, abort, make_response, request
from app.models.goal import Goal
from app import db
from app.validate_model import validate_model
from app.models.task import Task

bp = Blueprint("goals", __name__, url_prefix="/goals")

@bp.route("", methods=["POST"])
def create_goal():
    request_body = request.get_json()

    if "title" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))

    new_goal = Goal.from_dict(request_body)

    db.session.add(new_goal)
    db.session.commit()

    return make_response(jsonify({"goal" : new_goal.to_dict()}), 201)


@bp.route("", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    goals_response = [goal.to_dict() for goal in goals]

    return jsonify(goals_response)



@bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return jsonify({"goal": goal.to_dict()}), 200


@bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json() 

    if "title" not in request_body:
        abort(make_response({"details": "Invalid data"}, 400))

    goal.title = request_body["title"]

    db.session.commit()

    return jsonify({"goal": goal.to_dict()}), 200


@bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return make_response(jsonify({"details" : f"Goal 1 \"{goal.title}\" successfully deleted"})), 200


@bp.route("/<goal_id>/tasks", methods=["POST"])
def tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    
    goal.tasks = []
    for task_id in request_body["task_ids"]:
        task = validate_model(Task, task_id)
        goal.tasks.append(task)

    db.session.commit()

    return jsonify({
        "id" : goal.goal_id,
        "task_ids" : goal.task_ids()
    })


@bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_of_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    goal_dict = goal.to_dict()
    goal_dict["tasks"] = [task.to_dict() for task in goal.tasks]

    return jsonify(goal_dict)
