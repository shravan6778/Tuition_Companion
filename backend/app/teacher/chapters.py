import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import storage
from app.core.config import settings
from app.models import Chapter, ChapterStatus, Subject


def list_chapters(db: Session, subject: Subject) -> list[Chapter]:
    return list(
        db.scalars(select(Chapter).where(Chapter.subject_id == subject.id).order_by(Chapter.position, Chapter.created_at))
    )


def upload_chapter(db: Session, subject: Subject, title: str, upload: UploadFile) -> Chapter:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = upload.file.read(max_bytes + 1)  # read one extra byte to detect oversize
    if len(data) > max_bytes:
        raise HTTPException(413, f"File is larger than {settings.max_upload_mb} MB")
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file is empty")

    ext = storage.detect_extension(data)
    if ext is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported file. Upload a PDF, PNG or JPG.")

    file_hash = storage.sha256_hex(data)
    duplicate = db.scalar(
        select(Chapter.title).where(Chapter.subject_id == subject.id, Chapter.file_hash == file_hash)
    )
    if duplicate is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f'This file is already uploaded as "{duplicate}"')

    next_position = (db.scalar(select(func.max(Chapter.position)).where(Chapter.subject_id == subject.id)) or 0) + 1
    file_path = storage.save_by_hash(data, file_hash, ext)

    chapter = Chapter(
        subject_id=subject.id,
        title=title,
        position=next_position,
        status=ChapterStatus.uploaded,
        file_path=file_path,
        file_hash=file_hash,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter

def delete_chapter(db: Session, subject: Subject, chapter_id: uuid.UUID) -> None:
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.subject_id == subject.id))
    if chapter is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    if chapter.status == ChapterStatus.processing:
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is being processed. Try again in a moment.")

    file_path, file_hash = chapter.file_path, chapter.file_hash
    db.delete(chapter)
    db.commit()

    # Files are shared by hash: remove from disk only when no chapter (any subject) still uses it.
    if file_path and file_hash:
        still_used = db.scalar(select(Chapter.id).where(Chapter.file_hash == file_hash).limit(1))
        if still_used is None:
            storage.delete_file(file_path)