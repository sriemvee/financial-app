import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.email_triage import (  # noqa: E402
    DeletionRequestStore,
    EmailConfig,
    EmailConfigError,
    EmailMessageSummary,
    EmailTriageService,
    score_message,
)


class FakeEmailClient:
    def __init__(self, messages, fail_on_delete=False):
        self.messages = messages
        self.deleted_batches = []
        self.fail_on_delete = fail_on_delete

    def list_messages(self, limit=25):
        return self.messages[:limit]

    def delete_messages(self, message_ids):
        if self.fail_on_delete:
            raise RuntimeError("mailbox unavailable")
        batch = list(message_ids)
        self.deleted_batches.append(batch)
        return len(batch)


class EmailTriageTests(unittest.TestCase):
    def test_config_requires_imap_credentials(self):
        with self.assertRaises(EmailConfigError):
            EmailConfig.from_env({})

    def test_promotional_message_is_scored_as_irrelevant(self):
        config = EmailConfig(
            imap_host="imap.example.com",
            username="user@example.com",
            password="secret",
            older_than_days=14,
        )
        message = EmailMessageSummary(
            uid="101",
            sender="Deals <no-reply@shop.example>",
            subject="Huge promotion - unsubscribe any time",
            received_at=datetime.now(timezone.utc) - timedelta(days=45),
        )

        candidate = score_message(message, config)

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.uid, "101")
        self.assertGreaterEqual(candidate.score, 5)
        self.assertIn("subject matches a low-priority keyword", candidate.reasons)
        self.assertIn("sender matches a low-priority keyword", candidate.reasons)
        self.assertIn("older than 14 days", candidate.reasons)

    def test_delete_requires_separate_confirmation(self):
        config = EmailConfig(
            imap_host="imap.example.com",
            username="user@example.com",
            password="secret",
        )
        client = FakeEmailClient(messages=[])
        service = EmailTriageService(client=client, config=config, store=DeletionRequestStore())

        request = service.create_deletion_request(["1", "2", "2"])
        self.assertEqual(client.deleted_batches, [])

        cancelled = service.confirm_deletion(request.request_id, approve=False)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(client.deleted_batches, [])

    def test_confirmed_delete_calls_client_once(self):
        config = EmailConfig(
            imap_host="imap.example.com",
            username="user@example.com",
            password="secret",
        )
        client = FakeEmailClient(messages=[])
        service = EmailTriageService(client=client, config=config, store=DeletionRequestStore())

        request = service.create_deletion_request(["alpha", "beta"])
        result = service.confirm_deletion(request.request_id, approve=True)

        self.assertEqual(result["status"], "deleted")
        self.assertEqual(result["deleted_count"], 2)
        self.assertEqual(client.deleted_batches, [["alpha", "beta"]])

    def test_failed_delete_keeps_request_available(self):
        config = EmailConfig(
            imap_host="imap.example.com",
            username="user@example.com",
            password="secret",
        )
        store = DeletionRequestStore()
        client = FakeEmailClient(messages=[], fail_on_delete=True)
        service = EmailTriageService(client=client, config=config, store=store)

        request = service.create_deletion_request(["retry-me"])

        with self.assertRaises(RuntimeError):
            service.confirm_deletion(request.request_id, approve=True)

        self.assertIsNotNone(store.get(request.request_id))


if __name__ == "__main__":
    unittest.main()
