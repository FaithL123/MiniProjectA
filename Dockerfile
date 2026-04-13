FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "from app import app, db; app.app_context().push(); db.create_all()"
RUN python -c "from app import app, db, User; app.app_context().push(); admin = User(username='admin', password_hash='secret'); db.session.add(admin); db.session.commit()"

EXPOSE 5000
CMD ["python", "app.py"]