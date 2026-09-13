from app import create_app, db
from app.models.writers import Users
from app.models.techpub_leads import Techpub_Leads
from app.models.dev_leads import Development_Leads
from app.models.stages import Stages
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        # Create the database tables
        db.create_all()
        default_password_hash = generate_password_hash("password123")  # Replace with your desired default password
        # Seed Users table
        
        users_data = [
            {"user_id": 1, "username": "Ajinkya Godbole", "email": "aj@gmail.com", 'role' :'Writer', 'product_line':'all'},
            {"user_id": 2, "username": "Michael Curry", "email": "mc@gmail.com", 'role' :'Writer', 'product_line':'all'}
        ]

        for user_info in users_data:
            # Check if user already exists to avoid duplicates
            if not Users.query.get(user_info["user_id"]):
                user = Users(
                    user_id=user_info["user_id"],
                    username=user_info["username"],
                    password=default_password_hash,  # Dynamically generated hash
                    email=user_info["email"],
                    role=user_info.get("role"),
                    product_line=user_info.get("product_line"),
                )
                db.session.add(user)

        # -------------------------------------------------------------
        # 2. SEED TECHPUB LEADS
        # -------------------------------------------------------------
        techpub_data = [
            {"reviewer_id": 1, "username": "Gail Baragar", "email": "gb@gmail.com", 'product_line':'all'},
        ]

        for lead_info in techpub_data:
            if not Techpub_Leads.query.get(lead_info["reviewer_id"]):
                lead = Techpub_Leads(
                    reviewer_id=lead_info["reviewer_id"],
                    username=lead_info["username"],
                    password=default_password_hash,
                    email=lead_info["email"],
                    product_line=lead_info["product_line"],
                )
                db.session.add(lead)

        # -------------------------------------------------------------
        # 3. SEED DEVELOPMENT LEADS
        # -------------------------------------------------------------
        development_leads_data = [
            {"dev_id": 1, "username": "David M", "email": "dm@gmail.com"},
        ]

        for lead_info in development_leads_data:
            if not Development_Leads.query.get(lead_info["dev_id"]):
                lead = Development_Leads(
                    dev_id=lead_info["dev_id"],
                    username=lead_info["username"],
                    password=default_password_hash,
                    email=lead_info["email"],
                )
                db.session.add(lead)

        # -------------------------------------------------------------
        # 4. SEED STAGES
        # -------------------------------------------------------------
        stage_names = [
            "Gathering Requirements",
            "Draft Content",
            "Internal Review",
            "Internal Review Approved",
            "External Review",
            "External Review Approved",
            "Release",
        ]

        for stage_name in stage_names:
            if not Stages.query.filter_by(stage_name=stage_name).first():
                stage = Stages(stage_name=stage_name)
                db.session.add(stage)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()