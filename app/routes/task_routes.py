from flask import Blueprint, request, Response
from app.models.task import Task
from ..db import db

tasks_bp = Blueprint("tasks",__name__,url_prefix="/tasks")

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


@tasks_bp.get("/<id>")
def get_task(id):
    tasks = db.session.scalars(db.select(Task)).all()
    tasks_list = [task.to_dict() for task in tasks]

    return tasks_list, 200
