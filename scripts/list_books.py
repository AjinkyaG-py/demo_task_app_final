import os
import sys

# Ensure project root is on sys.path so 'app' can be imported when running from scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.models.books import Books

app = create_app()
with app.app_context():
    rows = db.session.query(Books.book_number, Books.revision, Books.project_name, Books.writer).all()
    if not rows:
        print('NO_BOOKS')
    else:
        for b in rows:
            print(f"{b.writer} | {b.project_name} | {b.book_number} | rev:{b.revision}")
