"""
Code Review Endpoints: Single, Batch, Status, Results, Feedback, and WebSocket.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from cerberus.agents.orchestrator import orchestrator
from cerberus.api.dependencies import verify_api_key
from cerberus.core.database import AsyncSessionLocal
from cerberus.models.database import CodeReviewRecord, FindingRecord, ReviewFeedbackRecord
from cerberus.models.schemas import (
    BatchReviewRequest,
    BatchReviewResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    FeedbackRequest,
    FeedbackResponse,
)

logger = logging.getLogger("cerberus.api.review")
router = APIRouter(prefix="/api/v1/review", tags=["Review"])

# In-memory store for quick lookups and active WebSocket broadcasts
reviews_store: Dict[str, CodeReviewResponse] = {}
ws_connections: Dict[str, List[WebSocket]] = {}


@router.post("", response_model=CodeReviewResponse, status_code=status.HTTP_200_OK)
async def submit_review(
    request: CodeReviewRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit source code for multi-agent review across Security, Performance, and Quality.
    """
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Source code snippet cannot be empty")

    response = await orchestrator.execute_review(request)
    reviews_store[response.review_id] = response

    # Persist in background DB
    asyncio.create_task(_persist_review_record(request, response))

    # Notify connected WebSockets
    if response.review_id in ws_connections:
        for ws in ws_connections[response.review_id]:
            try:
                await ws.send_text(json.dumps({
                    "event": "review_completed",
                    "review_id": response.review_id,
                    "overall_score": response.overall_score
                }))
            except Exception:
                pass

    return response


@router.get("/{review_id}", response_model=CodeReviewResponse)
async def get_review_status(
    review_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get the current processing status and summary of a review."""
    if review_id in reviews_store:
        return reviews_store[review_id]

    # Check database
    try:
        async with AsyncSessionLocal() as session:
            record = await session.get(CodeReviewRecord, review_id)
            if record and record.results_json:
                return CodeReviewResponse(**record.results_json)
    except Exception as e:
        logger.warning(f"DB lookup failed for {review_id}: {e}")

    raise HTTPException(status_code=404, detail=f"Review with ID '{review_id}' was not found.")


@router.get("/{review_id}/results", response_model=CodeReviewResponse)
async def get_review_results(
    review_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Retrieve full synthesized results, agent findings, and remediation suggestions."""
    return await get_review_status(review_id, api_key)


@router.post("/batch", response_model=BatchReviewResponse)
async def batch_review(
    request: BatchReviewRequest,
    api_key: str = Depends(verify_api_key)
):
    """Submit multiple files or snippets for concurrent batch code review."""
    tasks = [orchestrator.execute_review(req) for req in request.files]
    results: List[CodeReviewResponse] = await asyncio.gather(*tasks)

    for res in results:
        reviews_store[res.review_id] = res

    return BatchReviewResponse(
        batch_id=f"batch_{uuid.uuid4().hex[:12]}",
        total_files=len(results),
        reviews=results
    )


@router.post("/{review_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    review_id: str,
    feedback: FeedbackRequest,
    api_key: str = Depends(verify_api_key)
):
    """Submit developer feedback and rating for a completed review."""
    try:
        async with AsyncSessionLocal() as session:
            record = ReviewFeedbackRecord(
                review_id=review_id,
                user_id=api_key,
                rating=feedback.rating,
                is_helpful=feedback.is_helpful,
                false_positives=feedback.false_positives,
                false_negatives=feedback.false_negatives,
                comments=feedback.comments
            )
            session.add(record)
            await session.commit()
    except Exception as e:
        logger.warning(f"Could not persist feedback: {e}")

    return FeedbackResponse(status="success", message="Feedback recorded. Thank you for improving Cerberus.")


@router.websocket("/{review_id}/ws")
async def websocket_review_stream(websocket: WebSocket, review_id: str):
    """Live WebSocket stream broadcasting agent lifecycle events and progress."""
    await websocket.accept()
    if review_id not in ws_connections:
        ws_connections[review_id] = []
    ws_connections[review_id].append(websocket)

    try:
        await websocket.send_text(json.dumps({
            "event": "connected",
            "review_id": review_id,
            "message": "Subscribed to live agent updates."
        }))
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if review_id in ws_connections and websocket in ws_connections[review_id]:
            ws_connections[review_id].remove(websocket)


async def _persist_review_record(request: CodeReviewRequest, response: CodeReviewResponse) -> None:
    """Asynchronously persist review and findings to database."""
    try:
        async with AsyncSessionLocal() as session:
            review_rec = CodeReviewRecord(
                id=response.review_id,
                code_snippet=request.code[:2000],  # truncate if very large
                language=request.language or "python",
                status=response.status,
                overall_score=response.overall_score,
                processing_time_ms=response.processing_time_ms,
                results_json=response.model_dump(),
            )
            session.add(review_rec)

            # Add individual findings
            for f in response.critical_issues + response.warnings + response.suggestions:
                finding_rec = FindingRecord(
                    review_id=response.review_id,
                    agent_name=f.category,
                    severity=f.severity.value,
                    category=f.category,
                    title=f.title,
                    message=f.message,
                    line_number=f.line,
                    code_snippet=f.code_snippet,
                    remediation=f.recommendation,
                    suggestion=f.suggestion,
                    cwe_id=f.cwe_id,
                    cvss_score=f.cvss_score,
                )
                session.add(finding_rec)

            await session.commit()
    except Exception as e:
        logger.warning(f"Database background write error: {e}")
