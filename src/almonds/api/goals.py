import datetime
from uuid import UUID

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from almonds.api import root
from almonds.crud import goal as crud_goal
from almonds.schemas.goal import GoalBase, GoalUpdate
from almonds.utils import status_code

goal_bp = Blueprint("goal", __name__)


@goal_bp.route("/")
def view():
    if "username" not in session:
        return redirect(url_for("root.view"))

    goals = crud_goal.get_goals_by_user(session["user_id"])
    return render_template("goals.html", goals=goals, **build_context())


@goal_bp.route("/get", methods=["POST"])
def get_goal():
    body = request.get_json()
    if "goal_id" not in body:
        return (
            jsonify({"error": "Goal ID not provided"}),
            status_code.HTTP_400_BAD_REQUEST,
        )

    goal_id = UUID(body["goal_id"])
    goal = crud_goal.get_goal_by_id(goal_id)
    if goal:
        return (
            jsonify(
                goal.model_dump()
                | {"deadline_datestr": goal.deadline.strftime("%Y-%m-%d")}
            ),
            status_code.HTTP_200_OK,
        )

    return jsonify({"error": "Goal not found"}), status_code.HTTP_404_NOT_FOUND


@goal_bp.route("/create", methods=["POST"])
def create_goal():
    c_goal = GoalBase(
        user_id=session["user_id"],
        name=request.form["goal-name"],
        target_amount=float(request.form["target-amount"]),
        current_amount=float(request.form["current-amount"]),
        deadline=datetime.datetime.strptime(request.form["deadline"], "%Y-%m-%d"),
        status=request.form["status"],
    )
    crud_goal.create_goal(c_goal)
    return redirect(url_for("goal.view"))


@goal_bp.route("/update", methods=["POST"])
def update_goal():
    u_goal = GoalUpdate(
        id=UUID(request.form["goal-id"]),
        user_id=session["user_id"],
        name=request.form["goal-name"],
        target_amount=float(request.form["goal-target-amount"]),
        current_amount=float(request.form["goal-current-amount"]),
        deadline=datetime.datetime.strptime(request.form["goal-deadline"], "%Y-%m-%d"),
        status=request.form["goal-status"],
    )
    crud_goal.update_goal(u_goal)
    return redirect(url_for("goal.view"))


@goal_bp.route("/delete", methods=["POST"])
def delete_goal():
    body = request.get_json()
    goal_id = UUID(body["goal_id"])
    crud_goal.delete_goal(goal_id)
    return redirect(url_for("goal.view"))


def build_context():
    base = root.build_context()

    return base | {
        "title": "Goals",
        "user": {"username": session["username"]},
    }
