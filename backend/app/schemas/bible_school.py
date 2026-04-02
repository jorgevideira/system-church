from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


class BibleSchoolCourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    total_lessons: Optional[int] = None
    active: bool = True


class BibleSchoolCourseCreate(BibleSchoolCourseBase):
    pass


class BibleSchoolCourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_lessons: Optional[int] = None
    active: Optional[bool] = None


class BibleSchoolCourseResponse(BibleSchoolCourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BibleSchoolClassBase(BaseModel):
    course_id: int
    name: str
    weekday: str
    start_time: time
    end_time: time
    professor_name: Optional[str] = None
    contact: Optional[str] = None
    classroom: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    active: bool = True


class BibleSchoolClassCreate(BibleSchoolClassBase):
    pass


class BibleSchoolClassUpdate(BaseModel):
    course_id: Optional[int] = None
    name: Optional[str] = None
    weekday: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    professor_name: Optional[str] = None
    contact: Optional[str] = None
    classroom: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    active: Optional[bool] = None


class BibleSchoolClassResponse(BibleSchoolClassBase):
    id: int
    course_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BibleSchoolProfessorBase(BaseModel):
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    active: bool = True


class BibleSchoolProfessorCreate(BibleSchoolProfessorBase):
    pass


class BibleSchoolProfessorUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    active: Optional[bool] = None


class BibleSchoolProfessorResponse(BibleSchoolProfessorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BibleSchoolLessonBase(BaseModel):
    class_id: int
    professor_id: Optional[int] = None
    lesson_date: date
    topic: Optional[str] = None
    notes: Optional[str] = None
    status: str = "scheduled"
    active: bool = True


class BibleSchoolLessonCreate(BibleSchoolLessonBase):
    pass


class BibleSchoolLessonUpdate(BaseModel):
    class_id: Optional[int] = None
    professor_id: Optional[int] = None
    lesson_date: Optional[date] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    active: Optional[bool] = None


class BibleSchoolLessonResponse(BibleSchoolLessonBase):
    id: int
    class_name: Optional[str] = None
    course_name: Optional[str] = None
    professor_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BibleSchoolStudentBase(BaseModel):
    class_id: int
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    active: bool = True


class BibleSchoolStudentCreate(BibleSchoolStudentBase):
    pass


class BibleSchoolStudentUpdate(BaseModel):
    class_id: Optional[int] = None
    name: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    active: Optional[bool] = None


class BibleSchoolStudentResponse(BibleSchoolStudentBase):
    id: int
    class_name: Optional[str] = None
    course_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BibleSchoolAttendanceItem(BaseModel):
    student_id: int
    status: str = "pending"
    notes: Optional[str] = None


class BibleSchoolAttendanceUpsertRequest(BaseModel):
    items: list[BibleSchoolAttendanceItem]


class BibleSchoolAttendanceResponse(BaseModel):
    lesson_id: int
    lesson_date: date
    class_id: int
    class_name: Optional[str] = None
    student_id: int
    student_name: str
    status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
