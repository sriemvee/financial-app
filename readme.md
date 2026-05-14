# Email Triage Agent MVP

Lightweight FastAPI scaffold for connecting to an email inbox over IMAP, identifying likely irrelevant emails, and requiring explicit confirmation before any deletion happens.

## What this MVP does

- Connects to an IMAP mailbox using environment variables
- Lists likely irrelevant emails using simple, explainable heuristics
- Flags candidates based on sender keywords, subject keywords, and age
- Creates deletion requests without deleting immediately
- Requires a second confirmation call before destructive deletion
- Keeps implementation small and testable with stdlib IMAP support

## Safety model

Deletion is intentionally split into two steps:

1. `POST /email-triage/deletion-requests` creates a pending request
2. `POST /email-triage/deletion-requests/{request_id}/confirm` must be called with `"approve": true`

If confirmation is rejected or the request expires, no emails are deleted.

## Configuration

Copy `backend/.env.example` to `backend/.env` for local development, or export the same variables in your shell.

```env
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_USE_SSL=true
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-app-password
EMAIL_FOLDER=INBOX
TRIAGE_SUBJECT_KEYWORDS=newsletter,promotion,sale,discount,unsubscribe
TRIAGE_SENDER_KEYWORDS=no-reply,noreply,notifications,marketing,mailer-daemon
TRIAGE_OLDER_THAN_DAYS=30
DELETE_CONFIRMATION_WINDOW_MINUTES=15
```

## Run locally

### Backend

```bash
cd backend
pip install fastapi uvicorn python-dotenv
uvicorn main:app --reload
```

### Frontend

The existing frontend remains in the repo, but the email triage MVP is currently backend-first.

```bash
cd frontend
npm install
npm run dev
```

## API endpoints

- `GET /email-triage/status` — check whether required email configuration is present
- `GET /email-triage/candidates?limit=25` — list likely irrelevant emails
- `POST /email-triage/deletion-requests` — create a pending deletion request
- `POST /email-triage/deletion-requests/{request_id}/confirm` — approve or cancel the request

### Example: create a deletion request

```bash
curl -X POST http://localhost:8000/email-triage/deletion-requests \
  -H "Content-Type: application/json" \
  -d '{"message_ids":["101","102"]}'
```

### Example: confirm deletion

```bash
curl -X POST http://localhost:8000/email-triage/deletion-requests/<request_id>/confirm \
  -H "Content-Type: application/json" \
  -d '{"approve":true}'
```

## Tests

Run the basic backend tests with:

```bash
python -m unittest discover -s backend/tests -p "test_*.py"
```

## Notes

- Use an app password where your email provider requires one
- No secrets are hardcoded in the email triage implementation
- The triage rules are intentionally simple so they can be tuned safely later
