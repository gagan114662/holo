"""
Avatar Generation Router
API endpoints for custom avatar creation and management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from ..database import get_db
from ..services.avatar_generation import avatar_generation_service, GeneratedAvatar
from .auth import get_current_user
from ..models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class AvatarCreateResponse(BaseModel):
    id: str
    name: str
    source_image_url: str
    thumbnail_url: str
    has_voice: bool
    created_at: str


class GenerateVideoRequest(BaseModel):
    text: str
    emotion: str = "neutral"


class GenerateVideoResponse(BaseModel):
    video_url: Optional[str]
    status: str
    message: str


@router.post("/from-image", response_model=AvatarCreateResponse)
async def create_avatar_from_image(
    name: str = Form(...),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """
    Create a custom avatar from a single photo.

    The photo should:
    - Be a clear front-facing portrait
    - Have good lighting
    - Be at least 512x512 pixels

    Returns the created avatar with URLs to access the processed images.
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, or WebP)"
        )

    # Read image data
    image_data = await image.read()

    # Validate size (max 10MB)
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image too large. Maximum size is 10MB"
        )

    # Validate minimum size
    if len(image_data) < 1000:
        raise HTTPException(
            status_code=400,
            detail="Image too small or corrupted"
        )

    try:
        avatar = await avatar_generation_service.create_avatar_from_image(
            user_id=str(user.id),
            name=name,
            image_data=image_data,
            image_filename=image.filename or "upload.jpg"
        )

        return AvatarCreateResponse(
            id=avatar.id,
            name=avatar.name,
            source_image_url=f"/api/avatars/generated/{avatar.id}/image",
            thumbnail_url=f"/api/avatars/generated/{avatar.id}/thumbnail",
            has_voice=avatar.voice_sample_path is not None,
            created_at=avatar.created_at.isoformat()
        )

    except Exception as e:
        logger.error(f"Avatar creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create avatar. Please try again."
        )


@router.post("/from-video", response_model=AvatarCreateResponse)
async def create_avatar_from_video(
    name: str = Form(...),
    video: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """
    Create a custom avatar from a short video (15-60 seconds).

    The video should:
    - Show your face clearly
    - Include you speaking (for voice cloning)
    - Be well-lit with a neutral background

    This will extract the best frame for the avatar image and
    capture your voice for optional voice cloning.
    """
    # Validate file type
    valid_types = ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"]
    if not video.content_type or video.content_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail="File must be a video (MP4, WebM, MOV, or AVI)"
        )

    # Read video data
    video_data = await video.read()

    # Validate size (max 100MB)
    if len(video_data) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Video too large. Maximum size is 100MB"
        )

    try:
        avatar = await avatar_generation_service.create_avatar_from_video(
            user_id=str(user.id),
            name=name,
            video_data=video_data,
            video_filename=video.filename or "upload.mp4"
        )

        return AvatarCreateResponse(
            id=avatar.id,
            name=avatar.name,
            source_image_url=f"/api/avatars/generated/{avatar.id}/image",
            thumbnail_url=f"/api/avatars/generated/{avatar.id}/thumbnail",
            has_voice=avatar.voice_sample_path is not None,
            created_at=avatar.created_at.isoformat()
        )

    except Exception as e:
        logger.error(f"Avatar creation from video failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create avatar from video. Please try again."
        )


@router.get("/my-avatars")
async def get_my_avatars(
    user: User = Depends(get_current_user)
):
    """Get all avatars created by the current user"""
    avatars = await avatar_generation_service.get_user_avatars(str(user.id))
    return {
        "avatars": [a.to_dict() for a in avatars],
        "count": len(avatars)
    }


@router.get("/{avatar_id}")
async def get_avatar(
    avatar_id: str,
    user: User = Depends(get_current_user)
):
    """Get details of a specific avatar"""
    avatar = await avatar_generation_service.get_avatar(avatar_id)

    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    # Only owner can view their avatars (for now)
    if avatar.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return avatar.to_dict()


@router.get("/{avatar_id}/image")
async def get_avatar_image(avatar_id: str):
    """Get the source image for an avatar (public endpoint for rendering)"""
    image_data = await avatar_generation_service.get_image_data(avatar_id)

    if not image_data:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=image_data,
        media_type="image/jpeg"
    )


@router.get("/{avatar_id}/thumbnail")
async def get_avatar_thumbnail(avatar_id: str):
    """Get the thumbnail image for an avatar (public endpoint for UI)"""
    image_data = await avatar_generation_service.get_thumbnail_data(avatar_id)

    if not image_data:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return Response(
        content=image_data,
        media_type="image/jpeg"
    )


@router.post("/{avatar_id}/generate-video", response_model=GenerateVideoResponse)
async def generate_talking_video(
    avatar_id: str,
    request: GenerateVideoRequest,
    user: User = Depends(get_current_user)
):
    """
    Generate a talking head video for the avatar.

    This uses AI to animate the avatar's face to match the spoken text.
    Processing may take 30-60 seconds depending on text length.
    """
    avatar = await avatar_generation_service.get_avatar(avatar_id)

    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    if avatar.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate text length
    if len(request.text) > 500:
        raise HTTPException(
            status_code=400,
            detail="Text too long. Maximum 500 characters per generation."
        )

    if len(request.text) < 2:
        raise HTTPException(
            status_code=400,
            detail="Text too short"
        )

    # Validate emotion
    valid_emotions = ["neutral", "happy", "sad", "surprised", "angry", "thinking"]
    if request.emotion not in valid_emotions:
        request.emotion = "neutral"

    try:
        video_path = await avatar_generation_service.generate_talking_video(
            avatar_id=avatar_id,
            text=request.text,
            emotion=request.emotion
        )

        if video_path:
            return GenerateVideoResponse(
                video_url=f"/api/avatars/generated/{avatar_id}/video/{video_path.split('/')[-1]}",
                status="success",
                message="Video generated successfully"
            )
        else:
            return GenerateVideoResponse(
                video_url=None,
                status="unavailable",
                message="Video generation not available. Using TTS fallback."
            )

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Video generation failed. Please try again."
        )


@router.delete("/{avatar_id}")
async def delete_avatar(
    avatar_id: str,
    user: User = Depends(get_current_user)
):
    """Delete an avatar (only the owner can delete)"""
    success = await avatar_generation_service.delete_avatar(
        avatar_id=avatar_id,
        user_id=str(user.id)
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Avatar not found or access denied"
        )

    return {"message": "Avatar deleted successfully"}
