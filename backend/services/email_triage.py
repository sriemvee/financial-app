import imaplib
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.utils import parseaddr, parsedate_to_datetime
from typing import Iterable, List, Optional


def _split_comma_separated(value: str) -> tuple[str, ...]:
    return tuple(item.strip().lower() for item in value.split(",") if item.strip())


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class EmailConfigError(ValueError):
    pass


@dataclass(frozen=True)
class EmailConfig:
    imap_host: str
    username: str
    password: str
    imap_port: int = 993
    folder: str = "INBOX"
    use_ssl: bool = True
    subject_keywords: tuple[str, ...] = (
        "newsletter",
        "promotion",
        "sale",
        "discount",
        "unsubscribe",
    )
    sender_keywords: tuple[str, ...] = (
        "no-reply",
        "noreply",
        "notifications",
        "marketing",
        "mailer-daemon",
    )
    older_than_days: int = 30
    confirmation_window_minutes: int = 15

    @classmethod
    def from_env(cls, environ: Optional[dict] = None) -> "EmailConfig":
        env = environ or os.environ
        required_keys = ("EMAIL_IMAP_HOST", "EMAIL_USERNAME", "EMAIL_PASSWORD")
        missing = [key for key in required_keys if not env.get(key)]
        if missing:
            raise EmailConfigError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            imap_host=env["EMAIL_IMAP_HOST"].strip(),
            imap_port=int(env.get("EMAIL_IMAP_PORT", "993")),
            username=env["EMAIL_USERNAME"].strip(),
            password=env["EMAIL_PASSWORD"],
            folder=env.get("EMAIL_FOLDER", "INBOX").strip() or "INBOX",
            use_ssl=_parse_bool(env.get("EMAIL_USE_SSL", "true")),
            subject_keywords=_split_comma_separated(
                env.get(
                    "TRIAGE_SUBJECT_KEYWORDS",
                    "newsletter,promotion,sale,discount,unsubscribe",
                )
            ),
            sender_keywords=_split_comma_separated(
                env.get(
                    "TRIAGE_SENDER_KEYWORDS",
                    "no-reply,noreply,notifications,marketing,mailer-daemon",
                )
            ),
            older_than_days=max(0, int(env.get("TRIAGE_OLDER_THAN_DAYS", "30"))),
            confirmation_window_minutes=max(
                1, int(env.get("DELETE_CONFIRMATION_WINDOW_MINUTES", "15"))
            ),
        )


@dataclass(frozen=True)
class EmailMessageSummary:
    uid: str
    sender: str
    subject: str
    received_at: Optional[datetime] = None


@dataclass(frozen=True)
class TriageCandidate:
    uid: str
    sender: str
    subject: str
    received_at: Optional[str]
    score: int
    reasons: List[str]


@dataclass(frozen=True)
class PendingDeletionRequest:
    request_id: str
    message_ids: List[str]
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ImapEmailClient:
    def __init__(self, config: EmailConfig):
        self.config = config

    def _connect(self):
        if self.config.use_ssl:
            mailbox = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
        else:
            mailbox = imaplib.IMAP4(self.config.imap_host, self.config.imap_port)

        mailbox.login(self.config.username, self.config.password)
        mailbox.select(self.config.folder)
        return mailbox

    def list_messages(self, limit: int = 25) -> List[EmailMessageSummary]:
        mailbox = self._connect()
        try:
            status, data = mailbox.uid("SEARCH", None, "ALL")
            if status != "OK":
                return []

            message_uids = data[0].split()[-limit:]
            messages: List[EmailMessageSummary] = []
            for uid in reversed(message_uids):
                fetch_status, payload = mailbox.uid(
                    "FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
                )
                if fetch_status != "OK" or not payload or not payload[0]:
                    continue

                raw_headers = payload[0][1]
                header_message = message_from_bytes(raw_headers)
                messages.append(
                    EmailMessageSummary(
                        uid=uid.decode("utf-8"),
                        sender=header_message.get("From", ""),
                        subject=header_message.get("Subject", ""),
                        received_at=_parse_received_at(header_message.get("Date")),
                    )
                )
            return messages
        finally:
            try:
                mailbox.close()
            except imaplib.IMAP4.error:
                pass
            mailbox.logout()

    def delete_messages(self, message_ids: Iterable[str]) -> int:
        mailbox = self._connect()
        flagged_for_deletion: List[str] = []
        try:
            for message_id in message_ids:
                status, _ = mailbox.uid(
                    "STORE", message_id.encode("utf-8"), "+FLAGS", "(\\Deleted)"
                )
                if status != "OK":
                    raise imaplib.IMAP4.error(
                        f"Unable to flag message {message_id} for deletion."
                    )
                flagged_for_deletion.append(message_id)

            if flagged_for_deletion:
                mailbox.expunge()
            return len(flagged_for_deletion)
        except Exception:
            for message_id in flagged_for_deletion:
                try:
                    mailbox.uid(
                        "STORE", message_id.encode("utf-8"), "-FLAGS", "(\\Deleted)"
                    )
                except imaplib.IMAP4.error:
                    pass
            raise
        finally:
            try:
                mailbox.close()
            except imaplib.IMAP4.error:
                pass
            mailbox.logout()


def _parse_received_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def score_message(message: EmailMessageSummary, config: EmailConfig) -> Optional[TriageCandidate]:
    sender_value = message.sender.lower()
    subject_value = message.subject.lower()
    sender_address = parseaddr(message.sender)[1].lower()

    reasons: List[str] = []
    score = 0

    if any(keyword in subject_value for keyword in config.subject_keywords):
        reasons.append("subject matches a low-priority keyword")
        score += 2

    if any(keyword in sender_value or keyword in sender_address for keyword in config.sender_keywords):
        reasons.append("sender matches a low-priority keyword")
        score += 2

    if message.received_at and config.older_than_days:
        age = datetime.now(timezone.utc) - message.received_at
        if age >= timedelta(days=config.older_than_days):
            reasons.append(f"older than {config.older_than_days} days")
            score += 1

    if not reasons:
        return None

    return TriageCandidate(
        uid=message.uid,
        sender=message.sender,
        subject=message.subject,
        received_at=message.received_at.isoformat() if message.received_at else None,
        score=score,
        reasons=reasons,
    )


class DeletionRequestStore:
    def __init__(self):
        self._requests: dict[str, PendingDeletionRequest] = {}

    def create(
        self,
        message_ids: Iterable[str],
        confirmation_window_minutes: int,
        now: Optional[datetime] = None,
    ) -> PendingDeletionRequest:
        unique_message_ids = list(dict.fromkeys(message_ids))
        if not unique_message_ids:
            raise ValueError("At least one message ID is required.")

        created_at = now or datetime.now(timezone.utc)
        request = PendingDeletionRequest(
            request_id=str(uuid.uuid4()),
            message_ids=unique_message_ids,
            created_at=created_at,
            expires_at=created_at + timedelta(minutes=confirmation_window_minutes),
        )
        self._requests[request.request_id] = request
        return request

    def get(self, request_id: str) -> Optional[PendingDeletionRequest]:
        request = self._requests.get(request_id)
        if not request:
            return None
        if request.expires_at < datetime.now(timezone.utc):
            self._requests.pop(request_id, None)
            return None
        return request

    def pop(self, request_id: str) -> Optional[PendingDeletionRequest]:
        return self._requests.pop(request_id, None)


class EmailTriageService:
    def __init__(
        self,
        client: ImapEmailClient,
        config: EmailConfig,
        store: Optional[DeletionRequestStore] = None,
    ):
        self.client = client
        self.config = config
        self.store = store or DeletionRequestStore()

    def list_irrelevant_candidates(self, limit: int = 25) -> List[TriageCandidate]:
        candidates: List[TriageCandidate] = []
        for message in self.client.list_messages(limit=limit):
            candidate = score_message(message, self.config)
            if candidate:
                candidates.append(candidate)
        return sorted(candidates, key=lambda item: (-item.score, item.uid))

    def create_deletion_request(self, message_ids: Iterable[str]) -> PendingDeletionRequest:
        return self.store.create(message_ids, self.config.confirmation_window_minutes)

    def confirm_deletion(self, request_id: str, approve: bool) -> dict:
        request = self.store.get(request_id)
        if not request:
            raise ValueError("Deletion request not found or expired.")

        if not approve:
            self.store.pop(request_id)
            return {
                "request_id": request_id,
                "status": "cancelled",
                "deleted_count": 0,
                "message_ids": request.message_ids,
            }

        deleted_count = self.client.delete_messages(request.message_ids)
        result = {
            "request_id": request_id,
            "status": "deleted",
            "deleted_count": deleted_count,
            "message_ids": request.message_ids,
        }
        self.store.pop(request_id)
        return result
