from enum import Enum


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    LATE_NIGHT = "late_night"


class RoleType(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STAFF = "staff"
    STUDENT = "student"


class RoleCode(str, Enum):
    # Admin roles
    ADMIN_DEFAULT = "admin_default"

    # Teacher roles
    TEACHER_DEFAULT = "teacher_default"

    # Staff roles
    STAFF_DEFAULT = "staff_default"
    EQUIPMENT_STAFF = "equipment_staff"
    ACTIVITY_STAFF = "activity_staff"
    CATERING_STAFF = "catering_staff"

    # Student roles
    STUDENT_DEFAULT = "student_default"
    GROUP_LEADER = "group_leader"


# Mapping of valid role codes for each role type
VALID_ROLE_CODES: dict[RoleType, list[RoleCode]] = {
    RoleType.ADMIN: [
        RoleCode.ADMIN_DEFAULT,
    ],
    RoleType.TEACHER: [
        RoleCode.TEACHER_DEFAULT,
    ],
    RoleType.STAFF: [
        RoleCode.STAFF_DEFAULT,
        RoleCode.EQUIPMENT_STAFF,
        RoleCode.ACTIVITY_STAFF,
        RoleCode.CATERING_STAFF,
    ],
    RoleType.STUDENT: [
        RoleCode.STUDENT_DEFAULT,
        RoleCode.GROUP_LEADER,
    ],
}


def validate_role_code(role_type: RoleType, role_code: RoleCode) -> bool:
    """
    Validate that the given role_code is valid for the role_type
    Returns True if valid, False if invalid
    """
    return role_code in VALID_ROLE_CODES[role_type]


__all__ = ["MealType", "RoleType", "RoleCode", "VALID_ROLE_CODES", "validate_role_code"]
