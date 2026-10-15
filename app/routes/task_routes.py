from flask import Blueprint, request, Response
from app.models.task import Task
from ..db import db

tasks_bp = Blueprint("tasks_bp",__name__,url_prefix="/tasks")

@tasks_bp.post("")
def create_new_task():
    request_body = request.get_json()
    title = request_body["title"]
    description = request_body["description"]
    

    new_task = Task(title=title, description=description)
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
    query = db.select(Task).order_by(Task.id)
    tasks_list = db.session.scalars(query)

    task_response = []
    for task in tasks_list:
        task_response.append(task.to_dict())
            
    return task_response, 200
