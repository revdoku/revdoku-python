import os

from revdoku import Revdoku

# Reads REVDOKU_API_KEY. REVDOKU_ACCOUNT_ID is optional.
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_projects(status="active", limit=100, cursor=cursor).data
        for project in page.projects:
            print(project.id, project.email.address if project.email and project.email.address else project.id)
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("Project pagination did not advance")
        seen.add(cursor)
