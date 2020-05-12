"""empty message

Revision ID: 85937d0da4ac
Revises: 55790eeec3bf
Create Date: 2020-05-13 13:04:42.762330

"""
import re
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "85937d0da4ac"
down_revision = "55790eeec3bf"
branch_labels = None
depends_on = None


def upgrade():
    stmt = text("update messages set subject = :subject where id = :id").bindparams(
        id="id", subject="subject"
    )
    # Get all messages with project link only.
    conn = op.get_bind()
    pattern = r'<a href=".*/project/(.*)\?tab=chat">(.*)</a>'
    results = conn.execute(
        text("select id, subject from messages where subject ilike '%?tab=chat%'")
    )

    len_results = results.rowcount
    print(f"Found {len_results} project messages")
    for i, res in enumerate(results):
        match = re.search(pattern, res.subject)
        project_id, url_message = match.groups()

        new_url = f'<Link to="/projects/{project_id}">{url_message}</Link>'
        new_subject = (
            f"{res.subject[:match.start()]}{new_url}{res.subject[match.end():]}"
        )
        conn.execute(stmt, id=res.id, subject=new_subject)
        print(f"Processing {i+1}/{len_results}", end="\r")

    # Now task urls.
    results = conn.execute(
        text("select id, subject from messages where subject ilike '%?task=%'")
    )

    len_results = results.rowcount
    print(f"Found {len_results} task messages")
    pattern = r'<a href=".*/project/(.*)\/\?task=(.*)">(.*)</a>'
    for i, res in enumerate(results):
        match = re.search(pattern, res.subject)
        project_id, task_id, url_message = match.groups()

        new_url = f'<Link to="/projects/{project_id}/tasks/?search={task_id}">{url_message}</Link>'
        new_subject = (
            f"{res.subject[:match.start()]}{new_url}{res.subject[match.end():]}"
        )
        conn.execute(stmt, id=res.id, subject=new_subject)
        print(f"Processing {i+1}/{len_results}", end="\r")


def downgrade():
    pass
