from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_active_user, get_optional_user
from app.schemas.chat import StartConversationRequest, ChatMessageRequest, ChatMessageResponse, MessageRead
from app.schemas.common import APIResponse
from app.services.conversation_service import ConversationService
from app.models.user import User
from app.models.customer import CustomerProfile

router = APIRouter()


@router.post(
    "/start",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Start Conversation Session",
    description="Initializes a new dialogue session and creates conversation state tracking."
)
async def start_conversation(
    req: StartConversationRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    conv_service = ConversationService(db)
    user_id = current_user.id if current_user else "default_customer_user_id"

    # Query CustomerProfile asynchronously to avoid greenlet implicit load errors
    stmt = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
    res = await db.execute(stmt)
    cust_profile = res.scalars().first()
    
    if not cust_profile:
        # Create customer profile if missing
        cust_profile = CustomerProfile(
            user_id=user_id,
            phone_number=f"+919876543210",
            segment="STANDARD"
        )
        db.add(cust_profile)
        await db.flush()

    conv = await conv_service.start_conversation(customer_id=cust_profile.id, channel=req.channel)
    
    return APIResponse(
        success=True,
        message="Conversation session started.",
        data={"conversation_id": conv.id, "channel": conv.channel, "status": conv.resolution_status.value}
    )


@router.post(
    "/message",
    response_model=APIResponse[ChatMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Process Customer Chat Turn",
    description="Executes NLU pipeline, updates dialogue state tracker, records turn message, and returns agent response."
)
async def process_message(
    req: ChatMessageRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    conv_service = ConversationService(db)
    conv_id = req.conversation_id
    user_id = current_user.id if current_user else "default_customer_user_id"

    # Auto-initialize session if conversation_id is not provided yet
    if not conv_id:
        stmt = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
        res = await db.execute(stmt)
        cust_profile = res.scalars().first()
        if not cust_profile:
            cust_profile = CustomerProfile(
                user_id=user_id,
                phone_number=f"+919876543210",
                segment="STANDARD"
            )
            db.add(cust_profile)
            await db.flush()
        conv = await conv_service.start_conversation(customer_id=cust_profile.id, channel="web")
        conv_id = conv.id

    try:
        turn_res = await conv_service.process_turn(
            conversation_id=conv_id,
            user_text=req.message,
            customer_profile=req.customer_profile
        )
        
        resp_data = ChatMessageResponse(
            conversation_id=turn_res.conversation_id,
            user_message=turn_res.user_message,
            bot_response=turn_res.bot_response,
            action_taken=turn_res.action_taken,
            intent_id=turn_res.dialogue_state.current_intent,
            confidence=turn_res.dialogue_state.intent_confidence,
            sentiment_score=turn_res.nlu_result["sentiment_language"]["sentiment_score"],
            detected_language=turn_res.nlu_result["sentiment_language"]["detected_language"],
            latency_ms=turn_res.nlu_result.get("latency_ms", 12.5),
            dialogue_state=turn_res.dialogue_state.model_dump()
        )
        return APIResponse(
            success=True,
            message="Turn processed successfully.",
            data=resp_data
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.get(
    "/history/{conversation_id}",
    response_model=APIResponse[List[MessageRead]],
    status_code=status.HTTP_200_OK,
    summary="Get Conversation History",
    description="Retrieves chronological message history for a conversation session."
)
async def get_history(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    conv_service = ConversationService(db)
    messages = await conv_service.get_history(conversation_id)
    return APIResponse(
        success=True,
        message="Conversation history retrieved.",
        data=[MessageRead.model_validate(m) for m in messages]
    )
