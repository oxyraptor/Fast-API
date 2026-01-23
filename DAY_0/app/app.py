from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from .schemas import PosteCreate, PosteResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, create_db_and_tables, get_async_session, User
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


app.include_router(fastapi_users.get_auth_router(auth_backend), prefix = '/auth/jwt', tags = ['auth'])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix = '/auth', tags = ['auth'])
app.include_router(fastapi_users.get_reset_password_router(), prefix = '/auth', tags = ['auth'])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix = '/auth', tags = ['auth'])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix = '/users', tags = ['users'])




@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    temp_file_path = None

    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Upload to ImageKit (v4 syntax)
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename
        )

        # Extract actual saved filename (v4 structure)
        saved_file_name = upload_result.file_path.split("/")[-1]

        # Save post in DB
        post = Post(
            caption=caption,
            url=upload_result.url,
            user_id = str(user.id),
            file_type="Video" if file.content_type.startswith("video/") else "Image",
            file_name=saved_file_name, 
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()




        
from sqlalchemy.orm import selectinload

@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await session.execute(
        select(Post)
        .options(selectinload(Post.user))      # <-- FIX
        .order_by(Post.created_at.desc())
    )
    
    posts = result.scalars().all()
    
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "author": post.user.email if post.user else "Unknown",       # <-- now safe
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": str(post.user_id) == str(user.id),
            }
        )
    
    return {"posts": posts_data}



@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    print("DEBUG: post_id received =", post_id, "TYPE:", type(post_id))

    try:
        result = await session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        

        await session.delete(post)
        await session.commit()

        return {
            "success": True,
            "message": "Post deleted successfully",
            "deleted_id": post_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting post: {str(e)}"
        )


