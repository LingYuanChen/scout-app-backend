from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.db import CourseTemplate, Equipment
from app.schemas import CourseTemplatePublic, CourseTemplateCreate, CourseTemplateUpdate, Message
from app.db.enums import RoleType

router = APIRouter(prefix="/course_templates", tags=["course_templates"])


def check_admin_permission(current_user: CurrentUser) -> None:
    if current_user.role_type != RoleType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )


@router.post("/", response_model=CourseTemplatePublic)
def create_course_template(session: SessionDep, current_user: CurrentUser, course_data: CourseTemplateCreate) -> Any:
    check_admin_permission(current_user)
    
    # Create course template
    course = CourseTemplate(**course_data.dict(exclude={"equipments"}), created_by=current_user.id)
    session.add(course)
    session.commit()
    session.refresh(course)
    
    # Add equipment relationships
    if course_data.equipments:
        equipment_ids = course_data.equipments
        equipments = session.exec(select(Equipment).where(Equipment.id.in_(equipment_ids))).all()
        course.equipments = equipments
        session.add(course)
        session.commit()
        session.refresh(course)
    
    return course


@router.post("/batch", response_model=List[CourseTemplatePublic])
def create_course_templates(session: SessionDep, current_user: CurrentUser, courses_data: List[CourseTemplateCreate]) -> Any:
    check_admin_permission(current_user)
    
    courses = []
    for data in courses_data:
        course = CourseTemplate(**data.dict(exclude={"equipments"}), created_by=current_user.id)
        session.add(course)
        courses.append(course)
    
    session.commit()
    
    # Add equipment relationships
    for course, data in zip(courses, courses_data):
        if data.equipments:
            equipment_ids = data.equipments
            equipments = session.exec(select(Equipment).where(Equipment.id.in_(equipment_ids))).all()
            course.equipments = equipments
    
    session.commit()
    return courses


@router.get("/", response_model=List[CourseTemplatePublic])
def read_course_templates(session: SessionDep, current_user: CurrentUser) -> Any:
    courses = session.exec(select(CourseTemplate)).all()
    return courses


@router.get("/{course_id}", response_model=CourseTemplatePublic)
def read_course_template(session: SessionDep, current_user: CurrentUser, course_id: UUID) -> Any:
    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")
    return course


@router.put("/{course_id}", response_model=CourseTemplatePublic)
def update_course_template(
    session: SessionDep, current_user: CurrentUser, course_id: UUID, course_data: CourseTemplateUpdate
) -> Any:
    check_admin_permission(current_user)
    
    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")
    
    # Update basic fields
    update_dict = course_data.dict(exclude_unset=True, exclude={"equipments"})
    for key, value in update_dict.items():
        setattr(course, key, value)
    
    # Update equipment relationships if provided
    if course_data.equipments is not None:
        equipment_ids = course_data.equipments
        equipments = session.exec(select(Equipment).where(Equipment.id.in_(equipment_ids))).all()
        course.equipments = equipments
    
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}", response_model=Message)
def delete_course_template(session: SessionDep, current_user: CurrentUser, course_id: UUID) -> Any:
    check_admin_permission(current_user)
    
    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")
    session.delete(course)
    session.commit()
    return Message(detail="Course template is deleted")
