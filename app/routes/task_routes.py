from flask import Blueprint

tasks_bp = Blueprint("tasks",__name__,url_prefix="/tasks")

@tasks_bp.get("")
def get_tasks():
    pass