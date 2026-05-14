import imaplib

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List

from services.email_triage import (
    DeletionRequestStore,
    EmailConfig,
    EmailConfigError,
    EmailTriageService,
    ImapEmailClient,
)


router = APIRouter(prefix="/email-triage", tags=["email-triage"])
request_store = DeletionRequestStore()


class DeletionRequestCreate(BaseModel):
    message_ids: List[str] = Field(default_factory=list)


class DeletionRequestConfirmation(BaseModel):
    approve: bool


def get_service() -> EmailTriageService:
    try:
        config = EmailConfig.from_env()
    except EmailConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return EmailTriageService(
        client=ImapEmailClient(config),
        config=config,
        store=request_store,
    )


@router.get("/status")
async def get_email_triage_status():
    try:
        config = EmailConfig.from_env()
    except EmailConfigError as exc:
        return {"configured": False, "detail": str(exc)}

    return {
        "configured": True,
        "imap_host": config.imap_host,
        "imap_port": config.imap_port,
        "username": config.username,
        "folder": config.folder,
        "older_than_days": config.older_than_days,
        "confirmation_window_minutes": config.confirmation_window_minutes,
    }


@router.get("/candidates")
async def get_irrelevant_email_candidates(limit: int = 25):
    service = get_service()
    try:
        return {"candidates": service.list_irrelevant_candidates(limit=limit)}
    except (imaplib.IMAP4.error, OSError) as exc:
        raise HTTPException(status_code=502, detail=f"Unable to read mailbox: {exc}") from exc


@router.post("/deletion-requests")
async def create_deletion_request(payload: DeletionRequestCreate):
    service = get_service()
    try:
        request = service.create_deletion_request(payload.message_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "request_id": request.request_id,
        "status": "pending_confirmation",
        "message_ids": request.message_ids,
        "expires_at": request.expires_at.isoformat(),
    }


@router.post("/deletion-requests/{request_id}/confirm")
async def confirm_deletion_request(request_id: str, payload: DeletionRequestConfirmation):
    service = get_service()
    try:
        return service.confirm_deletion(request_id, payload.approve)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (imaplib.IMAP4.error, OSError) as exc:
        raise HTTPException(status_code=502, detail=f"Unable to update mailbox: {exc}") from exc
