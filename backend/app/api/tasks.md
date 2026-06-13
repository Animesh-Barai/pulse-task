# Tasks Module

## Purpose
The Tasks module provides the core business logic for managing todo items, including creation, updates, deletion, and cross-workspace organization.

## Public API
### REST Endpoints
- `POST /api/v1/tasks`: Create a new task.
- `GET /api/v1/tasks/{task_id}`: Retrieve task details.
- `GET /api/v1/tasks`: List tasks with filters (status, priority, list_id).
- `PUT /api/v1/tasks/{task_id}`: Update task fields (title, description, status, etc.).
- `DELETE /api/v1/tasks/{task_id}`: Permanently remove a task.

### Socket Events
- `task_created`: Broadcasted when a new task is added.
- `task_updated`: Broadcasted when task fields are modified.
- `task_deleted`: Broadcasted when a task is removed.

## Data Models
### Task
- `id`: Unique identifier (ObjectId).
- `list_id`: Foreign key to parent TaskList.
- `title`: Short summary of the task.
- `description`: Detailed task requirements.
- `assignee_id`: User ID of the owner.
- `priority`: Numeric 1-5 (Low to Urgent).
- `status`: Enum (OPEN, IN_PROGRESS, DONE).
- `due_date`: Optional ISO timestamp.
- `tags`: List of strings for categorization.

## Events Emitted/Consumed
- **Emitted**: `task_created`, `task_updated`, `task_deleted` (via SocketService).
- **Consumed**: None (Task changes are triggered by API calls).

## Invariants
- A task must belong to a valid list_id.
- Priority must be within 1-5 range.
- Task status transitions are generally loose but title is required.

## Edge Cases
- **Simultaneous Edit**: For fields not managed by CRDT, the "last write wins" strategy is used via MongoDB update.
- **Dangling Tasks**: Deleting a list should ideally delete all child tasks (implemented via cascade or background job).

## Test Coverage
- Unit tests for task creation and filtering in `backend/tests/unit/test_task_service.py`.
- Integration tests for Task CRUD endpoints and socket broadcasts in `backend/tests/integration/test_tasks_api.py`.
