from flask import Blueprint, redirect, render_template, request, url_for, flash
from sqlalchemy import func
from app import db
from app.models.books import Books, BookStatus
from app.models.movements import Movements
from app.models.projects import Projects
from app.models.stages import Stages
from app.models.writers import Users
from app.writers.forms.book_transfer import BookTransferForm
from app.writers.forms.book_transfer import BookTransferForm
from app.writers.forms.move_book_to_next_stage import MoveBookToNextStageForm
from app.techpub_leads.forms.add_books import BookDetailsForm
from app.models.techpub_leads import Techpub_Leads
from app.models.dev_leads import Development_Leads
from flask_login import current_user, login_required

writers_bp = Blueprint('writers', __name__, template_folder='templates', url_prefix="/writers")

@writers_bp.route('/add_books_from_landing', methods=['GET', 'POST'])
@login_required
def add_books_from_landing():
    project_name_value = request.args.get('project_name') or request.form.get('project_name')
    project_name = project_name_value.strip() if project_name_value else None
    writer_name = current_user.username
    book_form = BookDetailsForm()

    if request.method == 'POST' and book_form.validate_on_submit():
        if not project_name:
            flash('Project is required to add a book.', 'danger')
            return redirect(url_for('writers.landing'))

        book_number = book_form.book_number.data.strip()
        revision = book_form.revision.data.strip()
        assigned_writer_name = book_form.writer_name.data.strip()
        

        existing_book = db.session.query(Books).filter_by(
            book_number=book_number,
            revision=revision,
            project_name=project_name,
            writer=writer_name
        ).first()

        if existing_book:
            flash('A book with the same number and revision already exists in this project.', 'danger')
            return redirect(url_for('writers.landing', project_name=project_name))

        project_record = db.session.query(Projects.project_id).filter_by(project_name=project_name).first()
        if not project_record:
            flash('Project not found.', 'danger')
            return redirect(url_for('writers.landing'))

        new_book = Books(
            book_number=book_number,
            revision=revision,
            writer=assigned_writer_name,
            project_name=project_name,
            project_id=project_record[0]
        )
        db.session.add(new_book)
        db.session.commit()

        first_stage = db.session.query(Stages.stage_id).first()
        movement = Movements(
            book_id=new_book.book_id,
            stage_id=first_stage.stage_id,
            user_id=db.session.query(Users.user_id).filter_by(username=writer_name).scalar(),
            comments='Book created by writer'
        )
        db.session.add(movement)
        db.session.commit()

        return redirect(url_for('writers.landing', project_name=project_name))

    return redirect(url_for('writers.landing', project_name=project_name))

@writers_bp.route('/landing', methods=['GET', 'POST'])
@login_required
def landing():
    writer_name = current_user.username

    transfer_form = BookTransferForm()
    book_form = BookDetailsForm()

    if request.method == 'POST' and request.form.get('add_book_submit') == 'true':
        if book_form.validate_on_submit():
            project_name_value = request.form.get('project_name') or request.args.get('project_name')
            project_name = project_name_value.strip() if project_name_value else None
            if not project_name:
                flash('Project is required to add a book.', 'danger')
                return redirect(url_for('writers.landing'))

            book_number = book_form.book_number.data.strip()
            revision = book_form.revision.data.strip()

            existing_book = db.session.query(Books).filter_by(
                book_number=book_number,
                revision=revision,
                project_name=project_name,
                writer=writer_name
            ).first()

            if existing_book:
                flash('A book with the same number and revision already exists in this project.', 'danger')
                return redirect(url_for('writers.landing', project_name=project_name))

            project_record = db.session.query(Projects.project_id).filter_by(project_name=project_name).first()
            if not project_record:
                flash('Project not found.', 'danger')
                return redirect(url_for('writers.landing'))

            new_book = Books(
                book_number=book_number,
                revision=revision,
                writer=writer_name,
                project_name=project_name,
                project_id=project_record[0]
            )
            db.session.add(new_book)
            db.session.commit()

            first_stage = db.session.query(Stages.stage_id).first()
            movement = Movements(
                book_id=new_book.book_id,
                stage_id=first_stage.stage_id,
                user_id=db.session.query(Users.user_id).filter_by(username=writer_name).scalar(),
                comments='Book created by writer'
            )
            db.session.add(movement)
            db.session.commit()

            flash('Book successfully added. Continue to add more books to this project or return to Home.', 'success')
            return redirect(url_for('writers.landing', project_name=project_name))

    if transfer_form.validate_on_submit():
        book_number_value = request.form.get('book_number')
        book_number = book_number_value.strip() if book_number_value else None
        revision_value = request.form.get('revision')
        revision = revision_value.strip() if revision_value else None
        project_name_value = request.form.get('project_name')
        project_name = project_name_value.strip() if project_name_value else None
        status_value = request.form.get('status')
        status = status_value.strip() if status_value else None
        new_user = transfer_form.writer_name.data.strip()



        revision = db.session.query(Books.revision).filter_by(book_number=book_number, project_name=project_name).scalar()

        book_id = db.session.query(Books.book_id).filter_by(project_name=project_name, book_number=book_number, revision=revision).scalar()

        task_to_update = db.session.query(Books).filter(Books.book_id == book_id, Books.revision == revision).first()
        if task_to_update:
            task_to_update.writer = new_user
            db.session.add(task_to_update)
            db.session.commit()

        return redirect(url_for('writers.landing'))

    all_projects = (
        db.session.query(Books.project_name)
        .filter(Books.writer == writer_name)
        .distinct()
        .order_by(Books.project_name)
        .all()
    )

    project_name_value = request.args.get('project_name')
    project_name = project_name_value.strip() if project_name_value else None

    latest_stage_subquery = (
        db.session.query(
            Movements.book_id.label('book_id'),
            func.max(Movements.stage_id).label('latest_stage_id')
        )
        .group_by(Movements.book_id)
        .subquery()
    )

    books = (
        db.session.query(
            Books.book_id,
            Books.book_number,
            Books.revision,
            Books.project_name,
            Books.book_status,
            Stages.stage_name.label('current_stage')
        )
        .join(latest_stage_subquery, Books.book_id == latest_stage_subquery.c.book_id)
        .join(Stages, latest_stage_subquery.c.latest_stage_id == Stages.stage_id)
        .filter(Books.writer == writer_name, Books.book_status == BookStatus.OPEN.value)
        .order_by(Books.project_name, Books.book_number)
        .all()
    )

    if not project_name and all_projects:
        project_name = all_projects[0][0]

    print(books)
    return render_template(
        'writers_landing.html',
        all_projects=all_projects,
        books=books,
        project_name=project_name,
        transfer_form=transfer_form,
        book_form=book_form,
        writer_name=writer_name
    )

@writers_bp.route('/writers_movement', methods=['GET', 'POST'])
@login_required
def writers_movement():

    Writer_name = "Ajinkya Godbole"

    book_number_value = request.args.get("book_name")
    book_number = book_number_value.strip() if book_number_value else None
    print(book_number)
    revision_value = request.args.get("revision")
    revision = revision_value.strip() if revision_value else None
    project_name_value = request.args.get("project_name")
    project_name = project_name_value.strip() if project_name_value else None
    writer_name_value = request.args.get("writer")
    writer_name = writer_name_value.strip() if writer_name_value else None
    status_value = request.args.get("status")
    status = status_value.strip() if status_value else None

    writers_movement_form = MoveBookToNextStageForm()

    if writers_movement_form.validate_on_submit():
        # Handle form submission and move the book to the next stage
        stage_name = writers_movement_form.stage_name.data

        stage_id = db.session.query(Stages.stage_id).filter_by(stage_name=stage_name).scalar()

        writers_comment = writers_movement_form.comments.data

        reviewer_names = writers_movement_form.reviewer_names.data
        if stage_name not in ("Internal Review", "External Review"):
            reviewer_names = None

        # Lookup reviewer ids from the Reviewers table (supports comma-separated names)
        reviewer_list = [r.strip() for r in reviewer_names.split(",")] if reviewer_names else []

        # Preparing to update it in the movements table
        book_id = db.session.query(Books.book_id).filter_by(book_number=book_number, revision=revision).scalar()
        print(book_id)
        user_id = db.session.query(Users.user_id).filter_by(username="Ajinkya Godbole").scalar()
        print(user_id)
        # Add one movement per reviewer (or a single movement with no reviewer if none provided)
        if stage_name == "Release":
            book_status_update = db.session.query(Books).filter_by(book_id=book_id).first()
            book_status_update.book_status = BookStatus.CLOSED.value
            db.session.commit()
            
        if reviewer_list:
            for rname in reviewer_list:
                tech_id = db.session.query(Techpub_Leads.reviewer_id).filter_by(username=rname).scalar()
                dev_id = db.session.query(Development_Leads.dev_id).filter_by(username=rname).scalar()

                # If found as a techpub lead, add movement for techpub reviewer
                if tech_id:
                    new_movement = Movements(
                        book_id=book_id,
                        stage_id=stage_id,
                        user_id=user_id,
                        techpubreviewer_id=tech_id,
                        comments=writers_comment,
                    )
                    db.session.add(new_movement)

                # If found as a development lead, add movement for dev reviewer
                if dev_id:
                    new_movement = Movements(
                        book_id=book_id,
                        stage_id=stage_id,
                        user_id=user_id,
                        devreviewer_id=dev_id,
                        comments=writers_comment,
                    )
                    db.session.add(new_movement)

                # If not found in either table, create a movement without reviewer
                if not tech_id and not dev_id:
                    new_movement = Movements(
                        book_id=book_id,
                        stage_id=stage_id,
                        user_id=user_id,
                        techpubreviewer_id=None,
                        devreviewer_id=None,
                        comments=writers_comment,
                    )
                    db.session.add(new_movement)
        else:
            new_movement = Movements(
                book_id=book_id,
                stage_id=stage_id,
                user_id=user_id,
                techpubreviewer_id=None,
                comments=writers_comment,
            )
            db.session.add(new_movement)

        db.session.commit()

        return redirect(url_for('writers.landing'))
    

    return render_template('writers_movement.html', writers_movement_form=writers_movement_form)


@writers_bp.route('timesheet', methods=['GET', 'POST'])
@login_required
def timesheet():
    return render_template('timesheet.html')