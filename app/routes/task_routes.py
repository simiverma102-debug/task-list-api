from flask import Blueprint, request, Response, abort, make_response
from app.models.task import Task
from ..db import db
from datetime import datetime, timezone
import os
import requests

tasks_bp = Blueprint("tasks_bp",__name__,url_prefix="/tasks")

@tasks_bp.post("")
def create_new_task():
    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict):
        return {"details": "Invalid data"}, 400

    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400
    

    new_task = Task.from_dict(request_body)
    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201

    ''''''
    response = dict(
        id = new_task.id,
        title = new_task.title,
        description = new_task.description,
        is_complete = new_task.is_complete
    )
    return response, 201
    ''''''


@tasks_bp.get("")
def get_all_task():
    sort_query = request.args.get("sort")

    query = db.select(Task)
    if sort_query == 'asc':
        query = query.order_by(Task.title.asc())
    elif sort_query == 'desc':
        query = query.order_by(Task.title.desc())    
    else:
        query = query.order_by(Task.id)    

    tasks_list = db.session.scalars(query)

    task_response = []
    for task in tasks_list:
        task_response.append(task.to_dict())
            
    return task_response, 200

def validate_task(task_id):
    try:
       task_id = int(task_id)
    except(ValueError, TypeError):
        response = {"message": f"task {task_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"task {task_id} not found"}
        abort(make_response(response, 404))

    return task

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)

    return task.to_dict(), 200

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.delete("/<task_id>")
def delete_one_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_task(task_id)

    task.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    print("Slack token loaded:", bool(slack_token))

    if slack_token:
        requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {slack_token}"
            },
            json={
                "channel": "task-notifications-c26",
                "text": f"Someone just completed the task {task.title}"
            },
            timeout=10
        )

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)

    task.completed_at = None

    db.session.commit()

    return Response(status=204, mimetype="application/json")
