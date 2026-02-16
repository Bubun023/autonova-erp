# 1. Navigate to backend folder
cd backend

# 2. Install Flask-Migrate (if not installed)
pip install Flask-Migrate

# 3. Initialize migrations (if migrations folder doesn't exist)
flask db init

# 4. Create migration
flask db migrate -m "Add estimate management tables"

# 5. Apply migration
flask db upgrade

# 6. Seed the database
python seed.py

# 7. Start the server
python app.py
