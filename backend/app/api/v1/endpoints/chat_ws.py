import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.conversation_service import ConversationService
from app.core.logging import logger

router = APIRouter()


@router.websocket("/ws/{conversation_id}")
async def websocket_chat_endpoint(websocket: WebSocket, conversation_id: str):
    """
    Real-time Streaming WebSocket Chat Endpoint for bi-directional dialogue processing.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected to conversation: {conversation_id}")

    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                payload = json.loads(data_text)
                user_msg = payload.get("message", "")
            except Exception:
                user_msg = data_text

            if not user_msg:
                continue

            async with AsyncSessionLocal() as db:
                conv_service = ConversationService(db)
                turn_res = await conv_service.process_turn(conversation_id=conversation_id, user_text=user_msg)
                await db.commit()

            response_payload = {
                "event": "message",
                "conversation_id": conversation_id,
                "user_message": turn_res.user_message,
                "bot_response": turn_res.bot_response,
                "action_taken": turn_res.action_taken,
                "intent_id": turn_res.dialogue_state.current_intent,
                "confidence": turn_res.dialogue_state.intent_confidence,
                "dialogue_state": turn_res.dialogue_state.model_dump()
            }
            await websocket.send_text(json.dumps(response_payload))

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error on conversation {conversation_id}: {str(e)}")
        await websocket.close()
