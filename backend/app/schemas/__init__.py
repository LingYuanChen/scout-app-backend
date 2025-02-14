from .attendance import (
    MealChoiceCreate,
    MealChoiceCreateBase,
    MealChoiceUpdate,
)
from .auth import (
    Message,
    NewPassword,
    Token,
    TokenPayload,
    UpdatePassword,
)
from .equipment import (
    EquipmentBase,
    EquipmentCreate,
    EquipmentPublic,
    EquipmentsPublic,
    EquipmentUpdate,
)
from .event import (
    EventBase,
    EventCreate,
    EventPublic,
    EventsPublic,
    EventUpdate,
)
from .event_meal_option import (
    EventMealOptionCreate,
)
from .meal import (
    MealBase,
    MealCreate,
    MealPublic,
    MealUpdate,
)
from .packing import (
    EventPackingList,
    PackingEquipmentBase,
    PackingEquipmentCreate,
    PackingEquipmentPublic,
    PackingEquipmentsPublic,
    PackingEquipmentUpdate,
)
from .user import (
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UserPublic",
    "UsersPublic",
    # Auth schemas
    "Token",
    "TokenPayload",
    "NewPassword",
    "UpdatePassword",
    "Message",
    # Equipment schemas
    "EquipmentBase",
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentPublic",
    "EquipmentsPublic",
    # Event schemas
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "EventPublic",
    "EventsPublic",
    # Meal schemas
    "MealBase",
    "MealCreate",
    "MealUpdate",
    "MealPublic",
    # Packing schemas
    "PackingEquipmentBase",
    "PackingEquipmentCreate",
    "PackingEquipmentUpdate",
    "PackingEquipmentPublic",
    "PackingEquipmentsPublic",
    "EventPackingList",
    # Attendance schemas
    "MealChoiceCreateBase",
    "MealChoiceCreate",
    "MealChoiceUpdate",
    # Event Meal Option schemas
    "EventMealOptionCreate",
]
