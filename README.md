# NEXORA E-Cell Portal Backend

This backend scaffold mirrors the portal architecture requested for the NEXORA E-Cell website.

## Structure
- API routes: auth, registration, admin, upload, certificate, dashboard, notification
- Models: user, team, project, admin, certificate
- Schemas and services follow the same layered structure

## Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
