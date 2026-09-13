from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy import func, select
from app.models.books import Books
from app.models.dev_leads import Development_Leads
from app.models.movements import Movements
from app.models.stages import Stages
from app.models.writers import Users
from app.techpub_leads.forms.project_details import ProjectDetailsForm
from app.techpub_leads.forms.add_books import BookDetailsForm
from app.development_leads.forms.approve_book import ApproveBookForm
from app.models.projects import Projects
from app.models.techpub_leads import Techpub_Leads
from app import db

dev_leads_bp = Blueprint('development_leads', __name__, template_folder='templates', url_prefix="/development_leads")

@dev_leads_bp.route('/landing')
@login_required
def landing():
    dev_lead_name = current_user.username

    dev_id = db.session.scalar(db.session.query(Development_Leads.dev_id).filter_by(username=dev_lead_name))
    print(dev_id)

    # Build a subquery that returns the latest movement (by movement_id) for each book
    latest_movement_subquery = (
        db.session.query(
            Movements.book_id.label('book_id'),
            func.max(Movements.movement_id).label('max_movement_id')
        )
        .group_by(Movements.book_id)
        .subquery()
    )

    # Fetch distinct project names for books whose latest movement is a review stage
    all_projects = (
        db.session.query(Books.project_name)
        .join(latest_movement_subquery, Books.book_id == latest_movement_subquery.c.book_id)
        .join(Movements, Movements.movement_id == latest_movement_subquery.c.max_movement_id)
        .join(Stages, Movements.stage_id == Stages.stage_id)
        .filter(
            Movements.devreviewer_id == dev_id,
            Stages.stage_name.in_(['External Review'])
        )
        .distinct()
        .order_by(Books.project_name)
        .all()
    )

    project_name = request.args.get('project_name')

    # If no project is selected, redirect to the same route with the first project
    if not project_name and all_projects:
        return redirect(url_for('development_leads.landing', project_name=all_projects[0][0]))

    # Use the latest-movement subquery to select the latest movement row and return mappings
    stmt = (
        select(
            Books.book_id,
            Books.book_number,
            Books.revision,
            Books.project_name,
            Books.book_status,
            Stages.stage_name.label('current_stage'),
        )
        .join(latest_movement_subquery, Books.book_id == latest_movement_subquery.c.book_id)
        .join(Movements, Movements.movement_id == latest_movement_subquery.c.max_movement_id)
        .join(Stages, Movements.stage_id == Stages.stage_id)
        .where(
            Movements.devreviewer_id == dev_id,
            Stages.stage_name.in_(['External Review']),
        )
        .order_by(Books.project_name, Books.book_number)
    )

    books = db.session.execute(stmt).mappings().all()
    approve_form = ApproveBookForm()
    # `books` is now a list of mapping-like objects accessible by key in the template
    print(books)


    return render_template('dev_leads_landing.html', 
                           dev_lead_name=dev_lead_name, 
                           project_name=project_name, 
                           all_projects=all_projects, 
                           books=books,
                           approve_form=approve_form)

@dev_leads_bp.route('/dev_lead_book', methods=['POST','GET'])
@login_required
def dev_leads_movement():
    book_number = request.args.get("book_name")
    revision = request.args.get("revision")
    project_name = request.args.get("project_name")
    stage_name = request.args.get("status")

    if not book_number or not revision:
        flash("Book details are missing.")
        return redirect(url_for('development_leads.landing'))

    book_id = db.session.query(Books.book_id).filter_by(book_number=book_number, revision=revision).scalar()
    if not book_id:
        flash("Book not found.")
        return redirect(url_for('development_leads.landing', project_name=project_name))

    current_stage_id = (
        db.session.query(Movements.stage_id)
        .filter_by(book_id=book_id)
        .order_by(Movements.movement_id.desc())
        .first()
    )
    current_stage_id = current_stage_id[0] if current_stage_id else None

    if current_stage_id is None:
        next_stage_id = 1
    else:
        next_stage = (
            db.session.query(Stages.stage_id)
            .filter(Stages.stage_id > current_stage_id)
            .order_by(Stages.stage_id.asc())
            .first()
        )
        next_stage_id = next_stage[0] if next_stage else current_stage_id



    new_movement = Movements(
        book_id=book_id,
        stage_id=next_stage_id,
        comments=f"Approved from {stage_name or 'current stage'}",
    )
    db.session.add(new_movement)
    db.session.commit()

    return redirect(url_for('development_leads.landing'))