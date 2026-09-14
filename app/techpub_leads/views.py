from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy import func, select
from app.models.books import Books
from app.models.movements import Movements
from app.models.stages import Stages
from app.models.writers import Users
from app.techpub_leads.forms.project_details import ProjectDetailsForm
from app.techpub_leads.forms.add_books import BookDetailsForm
from app.techpub_leads.forms.approve_book import ApproveBookForm
from app.models.projects import Projects
from app.models.techpub_leads import Techpub_Leads
from app import db

techpub_leads_bp = Blueprint('techpub_leads', __name__, template_folder='templates', url_prefix="/techpub_leads")

def safe_strip(value):
    if value is None:
        return None
    try:
        return value.strip()
    except AttributeError:
        return str(value).strip()

@techpub_leads_bp.route('/landing')
@login_required
def landing():

    techpub_lead_name = current_user.username
    # get scalar reviewer id for the logged-in techpub lead
    reviewer_id = db.session.scalar(db.session.query(Techpub_Leads.reviewer_id).filter_by(username=techpub_lead_name))

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
            Movements.techpubreviewer_id == reviewer_id,
            Stages.stage_name.in_(['Internal Review'])
        )
        .distinct()
        .order_by(Books.project_name)
        .all()
    )

    project_name = safe_strip(request.args.get('project_name'))

    # If no project is selected, redirect to the same route with the first project
    if not project_name and all_projects:
        return redirect(url_for('techpub_leads.landing', project_name=all_projects[0][0]))

    current_project = None
    if project_name:
        current_project = db.session.query(Projects.project_id).filter_by(project_name=project_name).first()
    project_id = current_project[0] if current_project else None

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
            Movements.techpubreviewer_id == reviewer_id,
            Stages.stage_name.in_(['Internal Review']),
        )
        .order_by(Books.project_name, Books.book_number)
    )

    books = db.session.execute(stmt).mappings().all()
    approve_form = ApproveBookForm()
    book_form = BookDetailsForm()
    # `books` is now a list of mapping-like objects accessible by key in the template
    print(books)


    return render_template('techpub_leads_landing.html', 
                           techpub_lead_name=techpub_lead_name, 
                           project_name=project_name, 
                           project_id=project_id,
                           all_projects=all_projects, 
                           books=books,
                           approve_form=approve_form,
                           book_form=book_form)

@techpub_leads_bp.route('/create_work', methods=['GET', 'POST'])
@login_required
def create_work():
    project_details_form = ProjectDetailsForm()

    if project_details_form.validate_on_submit():
        network_id = project_details_form.network_id.data.strip()
        project_name = project_details_form.project_name.data.strip()
        product_line = project_details_form.product_line.data.strip()
        development_manager = project_details_form.development_manager.data.strip()
        techpub_manager = project_details_form.techpub_manager.data.strip()

        #fetching data from the form and creating a new project instance
        if all([network_id, project_name, product_line, development_manager, techpub_manager]):

            # Create a new project instance and save it to the database
            project = Projects(
                network_id=network_id,
                project_name=project_name,
                product_line=product_line,
                development_manager=development_manager,
                techpub_manager=techpub_manager
            )

            db.session.add(project)
            db.session.commit()

            #fetching the newly created project_id to pass it to the next page
            project_details = db.session.query(Projects.project_id, Projects.project_name).filter_by(network_id=network_id, project_name=project_name).first()
            print(f"Project details: {project_details}")
            return redirect(url_for('techpub_leads.add_books', project_id=project_details.project_id, project_name=project_details.project_name))

        # Process the form data (e.g., save to database, create work item, etc.)

    return render_template('project_details.html', form=project_details_form)

@techpub_leads_bp.route('/add_books', methods=['GET', 'POST'])
@login_required
def add_books(project_id=None, project_name=None):

    if not project_id:
        project_id = safe_strip(request.args.get('project_id') or request.form.get('project_id'))
    if not project_name:
        project_name = safe_strip(request.args.get('project_name') or request.form.get('project_name'))

    if not project_id and project_name:
        project = db.session.query(Projects.project_id).filter_by(project_name=project_name).first()
        project_id = project[0] if project else None

    book_form = BookDetailsForm()

    if request.method == 'POST' and book_form.validate_on_submit():
        if not project_id or not project_name:
            flash('Project details are missing.', 'danger')
            return redirect(url_for('techpub_leads.landing'))

        book_number = book_form.book_number.data.strip()
        revision = book_form.revision.data.strip()
        writer = book_form.writer.data.strip()

        existing_book = db.session.query(Books).filter_by(
            book_number=book_number,
            revision=revision,
            project_id=project_id
        ).first()

        if existing_book:
            flash('A book with the same number and revision already exists in this project.', 'danger')
            return redirect(url_for('techpub_leads.landing', project_name=project_name))

        book_entry = Books(
            book_number=book_number,
            revision=revision,
            writer=writer,
            project_name=project_name,
            project_id=project_id
        )
        db.session.add(book_entry)
        db.session.commit()

        first_stage = db.session.query(Stages.stage_id).first()
        writer_id = db.session.query(Users.user_id).filter_by(username=writer).first()

        movement_entry = Movements(
            book_id=book_entry.book_id,
            stage_id=first_stage.stage_id,
            user_id=writer_id.user_id if writer_id else None
        )
        db.session.add(movement_entry)
        db.session.commit()

        flash('Book successfully added. Continue adding books.', 'success')
        return redirect(url_for('techpub_leads.add_books', project_id=project_id, project_name=project_name))

    return render_template('add_books.html', project_id=project_id, project_name=project_name, book_form=book_form)


@techpub_leads_bp.route('/add_books_from_landing', methods=['GET', 'POST'])
@login_required
def add_books_from_landing():
    project_id = safe_strip(request.args.get('project_id') or request.form.get('project_id'))
    project_name = safe_strip(request.args.get('project_name') or request.form.get('project_name'))

    if not project_id and project_name:
        project = db.session.query(Projects.project_id).filter_by(project_name=project_name).first()
        project_id = project[0] if project else None

    book_form = BookDetailsForm()

    if request.method == 'POST' and book_form.validate_on_submit():
        if not project_id or not project_name:
            flash('Project details are missing.', 'danger')
            return redirect(url_for('techpub_leads.landing'))

        book_number = book_form.book_number.data.strip()
        revision = book_form.revision.data.strip()
        writer = book_form.writer.data.strip()

        existing_book = db.session.query(Books).filter_by(
            book_number=book_number,
            revision=revision,
            project_id=project_id
        ).first()

        if existing_book:
            flash('A book with the same number and revision already exists in this project.', 'danger')
            return redirect(url_for('techpub_leads.landing', project_name=project_name))

        book_entry = Books(
            book_number=book_number,
            revision=revision,
            writer=writer,
            project_name=project_name,
            project_id=project_id
        )
        db.session.add(book_entry)
        db.session.commit()

        first_stage = db.session.query(Stages.stage_id).first()
        writer_id = db.session.query(Users.user_id).filter_by(username=writer).first()

        movement_entry = Movements(
            book_id=book_entry.book_id,
            stage_id=first_stage.stage_id,
            user_id=writer_id.user_id if writer_id else None
        )
        db.session.add(movement_entry)
        db.session.commit()


        return redirect(url_for('techpub_leads.landing', project_name=project_name))

    return redirect(url_for('techpub_leads.landing', project_name=project_name))

@techpub_leads_bp.route('/techpub_leads_movement', methods=['GET', 'POST'])
@login_required
def techpub_leads_movement():
    book_number = safe_strip(request.args.get("book_name"))
    revision = safe_strip(request.args.get("revision"))
    project_name = safe_strip(request.args.get("project_name"))
    stage_name = safe_strip(request.args.get("status"))

    if not book_number or not revision:
        flash("Book details are missing.")
        return redirect(url_for('techpub_leads.landing'))

    book_id = db.session.query(Books.book_id).filter_by(book_number=book_number, revision=revision).scalar()
    if not book_id:
        flash("Book not found.")
        return redirect(url_for('techpub_leads.landing', project_name=project_name))

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
        comments=f"Approved from {stage_name or 'current stage'}")
    db.session.add(new_movement)
    db.session.commit()

    return redirect(url_for('techpub_leads.landing'))