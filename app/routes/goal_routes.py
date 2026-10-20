from flask import Blueprint, request, Response, abort, make_response
from app.models.goal import Goal
from ..db import db

goals_bp = Blueprint("goals_bp",__name__,url_prefix="/goals")

@goals_bp.post("")
def create_new_goal():
    request_body = request.get_json(silent=True)
    if not isinstance(request_body, dict) or "title" not in request_body:
        return {"details": "Invalid data"}, 400

    new_goal = Goal.from_dict(request_body)
    db.session.add(new_goal)
    db.session.commit()
    return new_goal.to_dict(), 201

@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goal_list = db.session.scalars(query)

    goal_response = []
    for goal in goal_list:
        goal_response.append(goal.to_dict())

    return goal_response, 200

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except (ValueError, TypeError):
        response = {"message": f"goal {goal_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        response = {"message":f"goal {goal_id} not found"}
        abort(make_response(response, 404))

    return goal        

@goals_bp.get("/<goal_id>")
def get_goal(goal_id):
    goal = validate_goal(goal_id)
    return goal.to_dict(), 200

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()
    goal.title = request_body["title"]
    db.session.commit()
    return goal.to_dict(), 200

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="applicate/json")