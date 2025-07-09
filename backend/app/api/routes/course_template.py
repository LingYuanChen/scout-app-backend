from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.db import CourseTemplate, Equipment
from app.db.enums import RoleType
from app.schemas import (
    CourseTemplateCreate,
    CourseTemplatePublic,
    CourseTemplateUpdate,
    Message,
)

router = APIRouter(prefix="/course_templates", tags=["course_templates"])


def check_admin_permission(current_user: CurrentUser) -> None:
    if current_user.role_type != RoleType.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admin users can perform this action"
        )


@router.post("/", response_model=CourseTemplatePublic)
def create_course_template(
    session: SessionDep, current_user: CurrentUser, course_data: CourseTemplateCreate
) -> Any:
    check_admin_permission(current_user)

    # Create course template
    course = CourseTemplate(
        **course_data.model_dump(exclude={"equipments"}), created_by=current_user.id
    )
    session.add(course)
    session.commit()
    session.refresh(course)

    # Add equipment relationships
    if course_data.equipments:
        equipment_ids = course_data.equipments
        equipments = session.exec(
            select(Equipment).where(Equipment.id.in_(equipment_ids))
        ).all()
        course.equipments = equipments
        session.add(course)
        session.commit()
        session.refresh(course)

    return course


@router.post("/batch", response_model=list[CourseTemplatePublic])
def create_course_templates(
    session: SessionDep,
    current_user: CurrentUser,
    courses_data: list[CourseTemplateCreate],
) -> Any:
    check_admin_permission(current_user)

    courses = []
    for data in courses_data:
        course = CourseTemplate(
            **data.model_dump(exclude={"equipments"}), created_by=current_user.id
        )
        session.add(course)
        courses.append(course)

    session.commit()

    # Add equipment relationships
    for course, data in zip(courses, courses_data, strict=False):
        if data.equipments:
            equipment_ids = data.equipments
            equipments = session.exec(
                select(Equipment).where(Equipment.id.in_(equipment_ids))
            ).all()
            course.equipments = equipments

    session.commit()
    return courses


@router.get("/", response_model=list[CourseTemplatePublic])
def read_course_templates(session: SessionDep) -> Any:
    courses = session.exec(select(CourseTemplate)).all()
    return courses


@router.get("/{course_id}", response_model=CourseTemplatePublic)
def read_course_template(session: SessionDep, course_id: UUID) -> Any:
    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")
    return course


@router.put("/{course_id}", response_model=CourseTemplatePublic)
def update_course_template(
    session: SessionDep,
    current_user: CurrentUser,
    course_id: UUID,
    course_data: CourseTemplateUpdate,
) -> Any:
    check_admin_permission(current_user)

    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")

    # Update basic fields
    update_dict = course_data.model_dump(exclude_unset=True, exclude={"equipments"})
    for key, value in update_dict.items():
        setattr(course, key, value)

    # Update equipment relationships if provided
    if course_data.equipments is not None:
        equipment_ids = course_data.equipments
        equipments = session.exec(
            select(Equipment).where(Equipment.id.in_(equipment_ids))
        ).all()
        course.equipments = equipments

    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}", response_model=Message)
def delete_course_template(
    session: SessionDep, current_user: CurrentUser, course_id: UUID
) -> Any:
    check_admin_permission(current_user)

    course = session.get(CourseTemplate, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course template not found")

    try:
        # Clear equipment relationships before deletion
        # This removes entries from the link table
        course.equipments = []
        session.add(course)
        session.commit()

        # Now delete the course template
        session.delete(course)
        session.commit()
        return Message(message="Course template is deleted")
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400, detail=f"Cannot delete course template: {str(e)}"
        )
