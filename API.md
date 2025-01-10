# API Documentation

## Authentication
- `POST /api/v1/login/access-token` - Get JWT access token
- `POST /api/v1/login/test-token` - Validate token
- `POST /api/v1/password-recovery/{email}` - Request password reset
- `POST /api/v1/reset-password/` - Reset password

## User Management
- `POST /api/v1/users/signup` - Register new user
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update own profile
- `PATCH /api/v1/users/me/password` - Update own password
- `DELETE /api/v1/users/me` - Delete own account

### Admin Only
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{user_id}` - Get user details
- `PATCH /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

## Events Management
- `GET /api/v1/events/` - List all events
- `GET /api/v1/events/{id}` - Get event details
- `POST /api/v1/events/` - Create new event (teachers only)
- `PUT /api/v1/events/{id}` - Update event (teachers only)
- `DELETE /api/v1/events/{id}` - Delete event (teachers only)

## Event Attendance
- `POST /api/v1/attendance/{event_id}/join` - Join an event
- `POST /api/v1/attendance/{event_id}/leave` - Leave an event
- `GET /api/v1/attendance/my-events` - List attended events
- `GET /api/v1/attendance/{event_id}/packing-list` - Get event packing list

## Items and Packing Lists
- `GET /api/v1/items/` - List items catalog (teachers only)
- `POST /api/v1/items/` - Create item (teachers only)
- `GET /api/v1/items/{id}` - Get item details
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item
- `POST /api/v1/items/{event_id}/packing` - Add item to event packing list
- `GET /api/v1/items/event/{event_id}` - Get event packing list

## Meals Management
- `GET /api/v1/meals/` - List all meals (teachers only)
- `POST /api/v1/meals/` - Create new meal (teachers only)
- `GET /api/v1/meals/{id}` - Get meal details
- `PUT /api/v1/meals/{id}` - Update meal (teachers only)
- `DELETE /api/v1/meals/{id}` - Delete meal (teachers only)

## Meal Choices
- `POST /api/v1/meal-choices/` - Create meal choice
- `GET /api/v1/meal-choices/` - List meal choices
- `PUT /api/v1/meal-choices/{id}` - Update meal choice
- `DELETE /api/v1/meal-choices/{id}` - Delete meal choice
