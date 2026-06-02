from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.common.s3 import upload_file, generate_presigned_url
from app.domains.cad.models import CadDrawing
from app.config import settings

router = APIRouter()

_ALLOWED_TYPES = {"pdf", "dwg", "dxf"}


async def _parse_cad_task(drawing_id: str, file_path: str):
    """백그라운드 CAD 파싱 작업 — Autodesk Forge API + YOLOv8 (구현 예정)"""
    # TODO: 1) Autodesk Forge 파일 변환
    #       2) YOLOv8 도면 객체 검출
    #       3) XGBoost 견적 예측
    #       4) DB 업데이트: parse_status='DONE', parsed_objects=..., confidence_score=...
    pass


@router.post("", status_code=202)
async def upload_cad(
    order_id: UUID = Form(...),
    drawing_no: str = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """CAD 도면 업로드 → S3 저장 → 비동기 파싱 시작"""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다. 허용: {_ALLOWED_TYPES}")

    file_bytes = await file.read()
    s3_key = f"cad/{order_id}/{drawing_no}/{file.filename}"
    file_type = "PDF" if ext == "pdf" else "DWG"

    # AWS 키 미설정 시 S3 업로드 건너뜀 (개발 환경)
    if settings.AWS_ACCESS_KEY_ID:
        content_type = "application/pdf" if ext == "pdf" else "application/octet-stream"
        await upload_file(file_bytes, s3_key, content_type)
        file_path = f"s3://{settings.S3_BUCKET}/{s3_key}"
    else:
        file_path = f"local://{s3_key}"

    drawing = CadDrawing(
        drawing_no=drawing_no,
        order_id=order_id,
        file_path=file_path,
        file_type=file_type,
        parse_status="PENDING",
    )
    db.add(drawing)
    await db.flush()

    background_tasks.add_task(_parse_cad_task, str(drawing.cad_drawing_id), file_path)

    return ok({
        "drawing_id": str(drawing.cad_drawing_id),
        "drawing_no": drawing_no,
        "file_type": file_type,
        "file_path": file_path,
        "parse_status": "PENDING",
        "message": "CAD 파싱이 시작되었습니다.",
    })


@router.get("/{drawing_id}")
async def get_drawing(drawing_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    drawing = await db.get(CadDrawing, drawing_id)
    if not drawing:
        raise NotFoundError("도면을 찾을 수 없습니다.")
    presigned_url = None
    if settings.AWS_ACCESS_KEY_ID and drawing.file_path.startswith("s3://"):
        s3_key = drawing.file_path.replace(f"s3://{settings.S3_BUCKET}/", "")
        presigned_url = generate_presigned_url(s3_key)
    return ok({
        "drawing_id": str(drawing.cad_drawing_id),
        "drawing_no": drawing.drawing_no,
        "file_type": drawing.file_type,
        "file_path": drawing.file_path,
        "download_url": presigned_url,
        "parse_status": drawing.parse_status,
        "confidence_score": float(drawing.confidence_score) if drawing.confidence_score else None,
        "parsed_objects": drawing.parsed_objects,
        "parsed_at": drawing.parsed_at.isoformat() if drawing.parsed_at else None,
    })


@router.get("/{drawing_id}/parse-status")
async def get_parse_status(drawing_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    drawing = await db.get(CadDrawing, drawing_id)
    if not drawing:
        raise NotFoundError("도면을 찾을 수 없습니다.")
    return ok({"drawing_id": str(drawing_id), "parse_status": drawing.parse_status})


@router.post("/{drawing_id}/parse")
async def reparse(
    drawing_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    drawing = await db.get(CadDrawing, drawing_id)
    if not drawing:
        raise NotFoundError("도면을 찾을 수 없습니다.")
    drawing.parse_status = "PENDING"
    drawing.parsed_at = None
    background_tasks.add_task(_parse_cad_task, str(drawing_id), drawing.file_path)
    return ok({"drawing_id": str(drawing_id), "parse_status": "PENDING"})
