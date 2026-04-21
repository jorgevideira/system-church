from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_school_read, require_school_write
from app.db.models.bible_school_class import BibleSchoolClass
from app.db.models.bible_school_course import BibleSchoolCourse
from app.db.models import BibleSchoolAttendance, BibleSchoolStudent
from app.db.models.bible_school_lesson import BibleSchoolLesson
from app.db.models.bible_school_professor import BibleSchoolProfessor
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.bible_school import (
    BibleSchoolAttendanceResponse,
    BibleSchoolAttendanceUpsertRequest,
    BibleSchoolClassCreate,
    BibleSchoolClassResponse,
    BibleSchoolClassUpdate,
    BibleSchoolCourseCreate,
    BibleSchoolCourseResponse,
    BibleSchoolCourseUpdate,
    BibleSchoolLessonCreate,
    BibleSchoolLessonResponse,
    BibleSchoolLessonUpdate,
    BibleSchoolProfessorCreate,
    BibleSchoolProfessorResponse,
    BibleSchoolProfessorUpdate,
    BibleSchoolStudentCreate,
    BibleSchoolStudentResponse,
    BibleSchoolStudentUpdate,
)

router = APIRouter()


@router.get("/courses", response_model=List[BibleSchoolCourseResponse])
def list_courses(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolCourse]:
    q = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.tenant_id == current_tenant.id)
    if active_only:
        q = q.filter(BibleSchoolCourse.active.is_(True))
    return q.order_by(BibleSchoolCourse.name.asc()).all()


@router.post("/courses", response_model=BibleSchoolCourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: BibleSchoolCourseCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolCourse:
    existing = (
        db.query(BibleSchoolCourse)
        .filter(BibleSchoolCourse.tenant_id == current_tenant.id, BibleSchoolCourse.name == payload.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ja existe um curso com esse nome")

    row = BibleSchoolCourse(**payload.model_dump(), tenant_id=current_tenant.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/courses/{course_id}", response_model=BibleSchoolCourseResponse)
def update_course(
    course_id: int,
    payload: BibleSchoolCourseUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolCourse:
    row = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.id == course_id, BibleSchoolCourse.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso nao encontrado")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)
    return row


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    row = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.id == course_id, BibleSchoolCourse.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso nao encontrado")

    has_classes = (
        db.query(BibleSchoolClass.id)
        .filter(BibleSchoolClass.tenant_id == current_tenant.id, BibleSchoolClass.course_id == course_id)
        .first()
    )
    if has_classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O curso possui turmas vinculadas. Exclua as turmas primeiro.",
        )

    db.delete(row)
    db.commit()


@router.get("/classes", response_model=List[BibleSchoolClassResponse])
def list_classes(
    course_id: Optional[int] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolClassResponse]:
    q = db.query(BibleSchoolClass, BibleSchoolCourse.name.label("course_name")).join(
        BibleSchoolCourse, BibleSchoolCourse.id == BibleSchoolClass.course_id
    ).filter(BibleSchoolClass.tenant_id == current_tenant.id, BibleSchoolCourse.tenant_id == current_tenant.id)
    if course_id:
        q = q.filter(BibleSchoolClass.course_id == course_id)
    if active_only:
        q = q.filter(BibleSchoolClass.active.is_(True))

    rows = q.order_by(BibleSchoolClass.name.asc()).all()
    return [
        BibleSchoolClassResponse(
            id=item.BibleSchoolClass.id,
            course_id=item.BibleSchoolClass.course_id,
            name=item.BibleSchoolClass.name,
            weekday=item.BibleSchoolClass.weekday,
            start_time=item.BibleSchoolClass.start_time,
            end_time=item.BibleSchoolClass.end_time,
            professor_name=item.BibleSchoolClass.professor_name,
            contact=item.BibleSchoolClass.contact,
            classroom=item.BibleSchoolClass.classroom,
            start_date=item.BibleSchoolClass.start_date,
            end_date=item.BibleSchoolClass.end_date,
            active=item.BibleSchoolClass.active,
            course_name=item.course_name,
            created_at=item.BibleSchoolClass.created_at,
            updated_at=item.BibleSchoolClass.updated_at,
        )
        for item in rows
    ]


@router.post("/classes", response_model=BibleSchoolClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    payload: BibleSchoolClassCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolClassResponse:
    course = (
        db.query(BibleSchoolCourse)
        .filter(BibleSchoolCourse.id == payload.course_id, BibleSchoolCourse.tenant_id == current_tenant.id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso nao encontrado")

    row = BibleSchoolClass(**payload.model_dump(), tenant_id=current_tenant.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return BibleSchoolClassResponse(
        **row.__dict__,
        course_name=course.name,
    )


@router.put("/classes/{class_id}", response_model=BibleSchoolClassResponse)
def update_class(
    class_id: int,
    payload: BibleSchoolClassUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolClassResponse:
    row = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    changes = payload.model_dump(exclude_unset=True)
    if "course_id" in changes:
        course = (
            db.query(BibleSchoolCourse)
            .filter(BibleSchoolCourse.id == changes["course_id"], BibleSchoolCourse.tenant_id == current_tenant.id)
            .first()
        )
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso nao encontrado")

    for field, value in changes.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)
    course = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.id == row.course_id, BibleSchoolCourse.tenant_id == current_tenant.id).first()
    return BibleSchoolClassResponse(
        **row.__dict__,
        course_name=course.name if course else None,
    )


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    row = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    has_lessons = (
        db.query(BibleSchoolLesson.id)
        .filter(BibleSchoolLesson.tenant_id == current_tenant.id, BibleSchoolLesson.class_id == class_id)
        .first()
    )
    if has_lessons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A turma possui aulas vinculadas. Exclua as aulas primeiro.",
        )

    db.delete(row)
    db.commit()


@router.get("/professors", response_model=List[BibleSchoolProfessorResponse])
def list_professors(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolProfessor]:
    q = db.query(BibleSchoolProfessor).filter(BibleSchoolProfessor.tenant_id == current_tenant.id)
    if active_only:
        q = q.filter(BibleSchoolProfessor.active.is_(True))
    return q.order_by(BibleSchoolProfessor.name.asc()).all()


@router.post("/professors", response_model=BibleSchoolProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(
    payload: BibleSchoolProfessorCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolProfessor:
    if payload.email:
        existing = (
            db.query(BibleSchoolProfessor)
            .filter(BibleSchoolProfessor.tenant_id == current_tenant.id, BibleSchoolProfessor.email == payload.email)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ja existe um professor com esse email")

    row = BibleSchoolProfessor(**payload.model_dump(), tenant_id=current_tenant.id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/professors/{professor_id}", response_model=BibleSchoolProfessorResponse)
def update_professor(
    professor_id: int,
    payload: BibleSchoolProfessorUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolProfessor:
    row = db.query(BibleSchoolProfessor).filter(BibleSchoolProfessor.id == professor_id, BibleSchoolProfessor.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor nao encontrado")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)
    return row


@router.delete("/professors/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(
    professor_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    row = db.query(BibleSchoolProfessor).filter(BibleSchoolProfessor.id == professor_id, BibleSchoolProfessor.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor nao encontrado")

    has_lessons = (
        db.query(BibleSchoolLesson.id)
        .filter(BibleSchoolLesson.tenant_id == current_tenant.id, BibleSchoolLesson.professor_id == professor_id)
        .first()
    )
    if has_lessons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O professor possui aulas vinculadas. Reatribua ou exclua as aulas primeiro.",
        )

    db.delete(row)
    db.commit()


@router.get("/lessons", response_model=List[BibleSchoolLessonResponse])
def list_lessons(
    class_id: Optional[int] = Query(None),
    professor_id: Optional[int] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolLessonResponse]:
    q = db.query(
        BibleSchoolLesson,
        BibleSchoolClass.name.label("class_name"),
        BibleSchoolCourse.name.label("course_name"),
        BibleSchoolProfessor.name.label("professor_name"),
    ).outerjoin(
        BibleSchoolClass, BibleSchoolClass.id == BibleSchoolLesson.class_id
    ).outerjoin(
        BibleSchoolCourse, BibleSchoolCourse.id == BibleSchoolClass.course_id
    ).outerjoin(
        BibleSchoolProfessor, BibleSchoolProfessor.id == BibleSchoolLesson.professor_id
    ).filter(
        BibleSchoolLesson.tenant_id == current_tenant.id,
        BibleSchoolClass.tenant_id == current_tenant.id,
        BibleSchoolCourse.tenant_id == current_tenant.id,
    )

    if class_id:
        q = q.filter(BibleSchoolLesson.class_id == class_id)
    if professor_id:
        q = q.filter(BibleSchoolLesson.professor_id == professor_id)
    if active_only:
        q = q.filter(BibleSchoolLesson.active.is_(True))

    rows = q.order_by(BibleSchoolLesson.lesson_date.desc()).all()
    return [
        BibleSchoolLessonResponse(
            id=item.BibleSchoolLesson.id,
            class_id=item.BibleSchoolLesson.class_id,
            professor_id=item.BibleSchoolLesson.professor_id,
            lesson_date=item.BibleSchoolLesson.lesson_date,
            topic=item.BibleSchoolLesson.topic,
            notes=item.BibleSchoolLesson.notes,
            status=item.BibleSchoolLesson.status,
            active=item.BibleSchoolLesson.active,
            class_name=item.class_name,
            course_name=item.course_name,
            professor_name=item.professor_name,
            created_at=item.BibleSchoolLesson.created_at,
            updated_at=item.BibleSchoolLesson.updated_at,
        )
        for item in rows
    ]


@router.post("/lessons", response_model=BibleSchoolLessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: BibleSchoolLessonCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolLessonResponse:
    classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == payload.class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    if payload.professor_id:
        professor = db.query(BibleSchoolProfessor).filter(BibleSchoolProfessor.id == payload.professor_id, BibleSchoolProfessor.tenant_id == current_tenant.id).first()
        if not professor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor nao encontrado")
    else:
        professor = None

    row = BibleSchoolLesson(**payload.model_dump(), tenant_id=current_tenant.id)
    db.add(row)
    db.commit()
    db.refresh(row)

    course = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.id == classroom.course_id, BibleSchoolCourse.tenant_id == current_tenant.id).first()
    return BibleSchoolLessonResponse(
        **row.__dict__,
        class_name=classroom.name,
        course_name=course.name if course else None,
        professor_name=professor.name if professor else None,
    )


@router.put("/lessons/{lesson_id}", response_model=BibleSchoolLessonResponse)
def update_lesson(
    lesson_id: int,
    payload: BibleSchoolLessonUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolLessonResponse:
    row = db.query(BibleSchoolLesson).filter(BibleSchoolLesson.id == lesson_id, BibleSchoolLesson.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula nao encontrada")

    changes = payload.model_dump(exclude_unset=True)
    if "class_id" in changes:
        classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == changes["class_id"], BibleSchoolClass.tenant_id == current_tenant.id).first()
        if not classroom:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")
    else:
        classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == row.class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()

    if "professor_id" in changes and changes["professor_id"]:
        professor = db.query(BibleSchoolProfessor).filter(BibleSchoolProfessor.id == changes["professor_id"], BibleSchoolProfessor.tenant_id == current_tenant.id).first()
        if not professor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor nao encontrado")
    else:
        professor = (
            db.query(BibleSchoolProfessor)
            .filter(BibleSchoolProfessor.id == row.professor_id, BibleSchoolProfessor.tenant_id == current_tenant.id)
            .first()
            if row.professor_id else None
        )

    for field, value in changes.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)

    course = (
        db.query(BibleSchoolCourse)
        .filter(BibleSchoolCourse.id == classroom.course_id, BibleSchoolCourse.tenant_id == current_tenant.id)
        .first()
        if classroom else None
    )
    return BibleSchoolLessonResponse(
        **row.__dict__,
        class_name=classroom.name if classroom else None,
        course_name=course.name if course else None,
        professor_name=professor.name if professor else None,
    )


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    row = db.query(BibleSchoolLesson).filter(BibleSchoolLesson.id == lesson_id, BibleSchoolLesson.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula nao encontrada")

    db.delete(row)
    db.commit()


@router.get("/students", response_model=List[BibleSchoolStudentResponse])
def list_students(
    class_id: Optional[int] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolStudentResponse]:
    q = db.query(
        BibleSchoolStudent,
        BibleSchoolClass.name.label("class_name"),
        BibleSchoolCourse.name.label("course_name"),
    ).join(
        BibleSchoolClass,
        BibleSchoolClass.id == BibleSchoolStudent.class_id,
    ).join(
        BibleSchoolCourse,
        BibleSchoolCourse.id == BibleSchoolClass.course_id,
    ).filter(
        BibleSchoolStudent.tenant_id == current_tenant.id,
        BibleSchoolClass.tenant_id == current_tenant.id,
        BibleSchoolCourse.tenant_id == current_tenant.id,
    )

    if class_id:
        q = q.filter(BibleSchoolStudent.class_id == class_id)
    if active_only:
        q = q.filter(BibleSchoolStudent.active.is_(True))

    rows = q.order_by(BibleSchoolStudent.name.asc()).all()
    return [
        BibleSchoolStudentResponse(
            id=item.BibleSchoolStudent.id,
            class_id=item.BibleSchoolStudent.class_id,
            name=item.BibleSchoolStudent.name,
            contact=item.BibleSchoolStudent.contact,
            email=item.BibleSchoolStudent.email,
            birth_date=item.BibleSchoolStudent.birth_date,
            active=item.BibleSchoolStudent.active,
            class_name=item.class_name,
            course_name=item.course_name,
            created_at=item.BibleSchoolStudent.created_at,
            updated_at=item.BibleSchoolStudent.updated_at,
        )
        for item in rows
    ]


@router.post("/students", response_model=BibleSchoolStudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: BibleSchoolStudentCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolStudentResponse:
    classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == payload.class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    if payload.email:
        exists_email = (
            db.query(BibleSchoolStudent)
            .filter(BibleSchoolStudent.tenant_id == current_tenant.id, BibleSchoolStudent.email == payload.email)
            .first()
        )
        if exists_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ja existe um aluno com esse email")

    row = BibleSchoolStudent(**payload.model_dump(), tenant_id=current_tenant.id)
    db.add(row)
    db.commit()
    db.refresh(row)

    course = db.query(BibleSchoolCourse).filter(BibleSchoolCourse.id == classroom.course_id, BibleSchoolCourse.tenant_id == current_tenant.id).first()
    return BibleSchoolStudentResponse(
        **row.__dict__,
        class_name=classroom.name,
        course_name=course.name if course else None,
    )


@router.put("/students/{student_id}", response_model=BibleSchoolStudentResponse)
def update_student(
    student_id: int,
    payload: BibleSchoolStudentUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> BibleSchoolStudentResponse:
    row = db.query(BibleSchoolStudent).filter(BibleSchoolStudent.id == student_id, BibleSchoolStudent.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno nao encontrado")

    changes = payload.model_dump(exclude_unset=True)

    if "class_id" in changes:
        classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == changes["class_id"], BibleSchoolClass.tenant_id == current_tenant.id).first()
        if not classroom:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    if "email" in changes and changes["email"]:
        exists_email = (
            db.query(BibleSchoolStudent)
            .filter(
                BibleSchoolStudent.tenant_id == current_tenant.id,
                BibleSchoolStudent.email == changes["email"],
                BibleSchoolStudent.id != student_id,
            )
            .first()
        )
        if exists_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ja existe um aluno com esse email")

    for field, value in changes.items():
        setattr(row, field, value)

    db.commit()
    db.refresh(row)

    classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == row.class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    course = (
        db.query(BibleSchoolCourse)
        .filter(BibleSchoolCourse.id == classroom.course_id, BibleSchoolCourse.tenant_id == current_tenant.id)
        .first()
        if classroom else None
    )
    return BibleSchoolStudentResponse(
        **row.__dict__,
        class_name=classroom.name if classroom else None,
        course_name=course.name if course else None,
    )


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    row = db.query(BibleSchoolStudent).filter(BibleSchoolStudent.id == student_id, BibleSchoolStudent.tenant_id == current_tenant.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno nao encontrado")

    db.delete(row)
    db.commit()


def _build_attendance_response(
    lesson_id: int,
    tenant_id: int,
    db: Session,
) -> List[BibleSchoolAttendanceResponse]:
    """Helper function to build attendance response list"""
    lesson = db.query(BibleSchoolLesson).filter(BibleSchoolLesson.id == lesson_id, BibleSchoolLesson.tenant_id == tenant_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula nao encontrada")

    classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == lesson.class_id, BibleSchoolClass.tenant_id == tenant_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    students = (
        db.query(BibleSchoolStudent)
        .filter(BibleSchoolStudent.tenant_id == tenant_id, BibleSchoolStudent.class_id == classroom.id)
        .order_by(BibleSchoolStudent.name.asc())
        .all()
    )

    attendance_rows = (
        db.query(BibleSchoolAttendance)
        .filter(BibleSchoolAttendance.tenant_id == tenant_id, BibleSchoolAttendance.lesson_id == lesson_id)
        .all()
    )
    attendance_map = {row.student_id: row for row in attendance_rows}

    result = []
    for student in students:
        att_record = attendance_map.get(student.id)
        result.append(
            BibleSchoolAttendanceResponse(
                lesson_id=lesson.id,
                lesson_date=lesson.lesson_date,
                class_id=classroom.id,
                class_name=classroom.name,
                student_id=student.id,
                student_name=student.name,
                status=att_record.status if att_record else "pending",
                notes=att_record.notes if att_record else None,
            )
        )
    return result


@router.get("/lessons/{lesson_id}/attendance", response_model=List[BibleSchoolAttendanceResponse])
def list_lesson_attendance(
    lesson_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_school_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolAttendanceResponse]:
    return _build_attendance_response(lesson_id, current_tenant.id, db)


@router.put("/lessons/{lesson_id}/attendance", response_model=List[BibleSchoolAttendanceResponse])
def upsert_lesson_attendance(
    lesson_id: int,
    payload: BibleSchoolAttendanceUpsertRequest,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_school_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[BibleSchoolAttendanceResponse]:
    lesson = db.query(BibleSchoolLesson).filter(BibleSchoolLesson.id == lesson_id, BibleSchoolLesson.tenant_id == current_tenant.id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula nao encontrada")

    classroom = db.query(BibleSchoolClass).filter(BibleSchoolClass.id == lesson.class_id, BibleSchoolClass.tenant_id == current_tenant.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma nao encontrada")

    valid_statuses = {"pending", "present", "absent", "justified"}

    for item in payload.items:
        if item.status not in valid_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status de chamada invalido")

        student = db.query(BibleSchoolStudent).filter(BibleSchoolStudent.id == item.student_id, BibleSchoolStudent.tenant_id == current_tenant.id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno nao encontrado")
        if student.class_id != classroom.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno nao pertence a turma da aula")

        existing = (
            db.query(BibleSchoolAttendance)
            .filter(
                BibleSchoolAttendance.tenant_id == current_tenant.id,
                BibleSchoolAttendance.lesson_id == lesson_id,
                BibleSchoolAttendance.student_id == item.student_id,
            )
            .first()
        )
        if existing:
            existing.status = item.status
            existing.notes = item.notes
        else:
            db.add(
                BibleSchoolAttendance(
                    tenant_id=current_tenant.id,
                    lesson_id=lesson_id,
                    student_id=item.student_id,
                    status=item.status,
                    notes=item.notes,
                )
            )

    db.commit()
    return _build_attendance_response(lesson_id, current_tenant.id, db)
