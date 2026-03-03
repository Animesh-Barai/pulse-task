# Phase 3: Advanced Features Implementation

**Status**: 🟡 **Not Started** (43-71 hours estimated)
**Duration**: 4-6 weeks
**Priority**: 🟢 **MEDIUM** (Nice to have for MVP)
**Owner**: Full-Stack Development Team

---

## 📋 Executive Summary

Phase 3 focuses on implementing advanced features that differentiate PulseTasks from basic task management tools. These features include workspace management, blocker detection, time-aware prioritization, analytics dashboards, OAuth2 integration, security/compliance features, CI/CD pipelines, monitoring, and load testing. While not critical for a minimum viable product, these features are essential for production readiness and enterprise adoption.

### Current State Analysis

| Component | Status | Completion | Blocking Issues |
|-----------|--------|------------|-----------------|
| **Workspace Management** | ❌ Missing | 0% | No workspace models or API |
| **Blocker Detection** | ❌ Missing | 0% | No inference worker |
| **Prioritization** | ❌ Missing | 0% | No calendar integration |
| **Analytics Dashboard** | ❌ Missing | 0% | No metrics collection |
| **OAuth2 Integration** | ❌ Missing | 0% | No Google OAuth |
| **Security/RBAC** | ❌ Missing | 0% | No role-based permissions |
| **CI/CD Pipeline** | ❌ Missing | 0% | No automated deployments |
| **Monitoring** | ❌ Missing | 0% | No Prometheus/Sentry |
| **Load Testing** | ❌ Missing | 0% | No performance tests |

### Phase 3 Objectives

1. **Workspace & Member Management** - Multi-tenant support with team collaboration
2. **Blocker Detection** - Automatic dependency inference and notifications
3. **Time-aware Prioritization** - Calendar integration and intelligent scheduling
4. **Analytics Dashboard** - Business metrics and user insights
5. **OAuth2 Integration** - Single sign-on with Google
6. **Security & Compliance** - RBAC, audit trails, GDPR tools
7. **CI/CD Pipeline** - Automated testing and deployment
8. **Monitoring & Observability** - Prometheus, Grafana, Sentry
9. **Performance Testing** - Load testing and optimization

**Success Criteria**:
- Multi-workspace support with member management
- Automatic blocker detection with >90% accuracy
- AI-powered prioritization with calendar awareness
- Real-time analytics dashboard
- Google OAuth2 sign-in working
- Role-based access control implemented
- Automated CI/CD pipeline deployed
- Monitoring dashboards operational
- Load tests passing for 10k concurrent users

---

## ✅ What's Already Done (Completed in Previous Phases)

### 3.1 Backend Foundation ✅

**Completed in Phase 1**:
- ✅ FastAPI application with all core routers
- ✅ MongoDB connection and models
- ✅ Redis client initialized
- ✅ Socket.IO server with real-time events
- ✅ AI microservice with OpenAI integration
- ✅ Celery workers for background jobs

### 3.2 Frontend Application ✅

**Completed in Phase 2**:
- ✅ React application with full structure
- ✅ Authentication UI (login/signup)
- ✅ Task management with CRUD
- ✅ Real-time features with Socket.IO
- ✅ AI suggestions integration

### 3.3 Existing API Endpoints ✅

**Authentication**:
```
✅ POST /api/v1/auth/signup
✅ POST /api/v1/auth/login
✅ POST /api/v1/auth/refresh
```

**Tasks**:
```
✅ POST /api/v1/tasks
✅ GET /api/v1/tasks/{id}
✅ GET /api/v1/tasks
✅ PUT /api/v1/tasks/{id}
✅ DELETE /api/v1/tasks/{id}
```

**AI**:
```
✅ POST /api/v1/ai/rewrite
✅ POST /api/v1/ai/prioritize
✅ POST /api/v1/ai/feedback
```

**Real-time**:
```
✅ ws://localhost:8000/socket.io/
```

---

## ❌ What's Left to Implement

### Task 3.1: Workspace & Member Management (10-14 hours) 🟢 MEDIUM

**Current State**:
- No workspace models in database
- No workspace API endpoints
- No member invitation system
- No role-based permissions

**What's Missing**:

#### 3.1.1 Create Workspace Data Models

**File**: `backend/app/models/workspace.py` (create new)

```python
# backend/app/models/workspace.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class WorkspaceMemberRole(str):
    """Workspace member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class WorkspaceMember(BaseModel):
    """Workspace member"""
    user_id: str = Field(..., description="User ID")
    role: WorkspaceMemberRole = Field(default=WorkspaceMemberRole.MEMBER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active")  # active, invited, pending

class WorkspaceCreate(BaseModel):
    """Create workspace request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    region: Optional[str] = Field(default="us-east-1")

class WorkspaceUpdate(BaseModel):
    """Update workspace request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    region: Optional[str] = None

class Workspace(BaseModel):
    """Workspace model"""
    id: str = Field(..., description="Workspace ID")
    name: str
    description: Optional[str]
    owner_id: str
    members: List[WorkspaceMember]
    region: str
    created_at: datetime
    updated_at: datetime

class WorkspaceInvite(BaseModel):
    """Workspace invite"""
    email: str = Field(..., description="Invited email")
    role: WorkspaceMemberRole = Field(default=WorkspaceMemberRole.MEMBER)
    workspace_id: str = Field(..., description="Workspace ID")
    invited_by: str = Field(..., description="User ID who sent invite")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Invite expiration")
    status: str = Field(default="pending")  # pending, accepted, declined, expired

class WorkspaceSettings(BaseModel):
    """Workspace settings"""
    workspace_id: str
    allow_ai_suggestions: bool = True
    enable_cloud_llm: bool = True
    require_2fa: bool = False
    audit_log_enabled: bool = True
    data_retention_days: int = 90
```

#### 3.1.2 Update MongoDB Collections

**File**: `backend/app/db/database.py` (modify)

```python
# Add to backend/app/db/database.py

# Workspace collections
def get_workspaces_collection():
    return db.workspaces

def get_workspace_invites_collection():
    return db.workspace_invites

# Indexes
async def create_workspace_indexes():
    """Create indexes for workspace collections"""
    workspaces = get_workspaces_collection()

    # Index for owner_id lookups
    await workspaces.create_index([("owner_id", 1)])

    # Index for member lookups
    await workspaces.create_index([("members.user_id", 1)])

    # Index for region lookups
    await workspaces.create_index([("region", 1)])

    # Invites collection
    invites = get_workspace_invites_collection()
    await invites.create_index([("email", 1), ("workspace_id", 1)])
    await invites.create_index([("status", 1), ("expires_at", 1)])
```

#### 3.1.3 Create Workspace Service

**File**: `backend/app/services/workspace_service.py` (create new)

```python
# backend/app/services/workspace_service.py
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from backend.app.models.workspace import (
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceMember,
    WorkspaceInvite,
    WorkspaceMemberRole,
)
from backend.app.db.database import (
    get_workspaces_collection,
    get_workspace_invites_collection,
)

class WorkspaceService:
    """Workspace management service"""

    async def create_workspace(
        self,
        workspace_data: WorkspaceCreate,
        owner_id: str
    ) -> Workspace:
        """Create new workspace"""
        collection = get_workspaces_collection()

        workspace = Workspace(
            id=str(ObjectId()),
            name=workspace_data.name,
            description=workspace_data.description,
            owner_id=owner_id,
            members=[
                WorkspaceMember(
                    user_id=owner_id,
                    role=WorkspaceMemberRole.OWNER,
                    joined_at=datetime.utcnow()
                )
            ],
            region=workspace_data.region,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        result = await collection.insert_one(workspace.dict(by_alias=True))
        return workspace

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID"""
        collection = get_workspaces_collection()
        data = await collection.find_one({"_id": ObjectId(workspace_id)})
        return Workspace(**data) if data else None

    async def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """Get all workspaces for user"""
        collection = get_workspaces_collection()
        cursor = collection.find({
            "$or": [
                {"owner_id": user_id},
                {"members.user_id": user_id}
            ]
        })
        return [Workspace(**data) async for data in cursor]

    async def update_workspace(
        self,
        workspace_id: str,
        updates: WorkspaceUpdate,
        user_id: str
    ) -> Optional[Workspace]:
        """Update workspace (owner or admin only)"""
        workspace = await self.get_workspace(workspace_id)

        if not workspace:
            return None

        # Check permissions
        member = next(
            (m for m in workspace.members if m.user_id == user_id),
            None
        )
        if not member or member.role not in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]:
            raise PermissionError("Insufficient permissions")

        # Update workspace
        collection = get_workspaces_collection()
        update_data = {
            **updates.dict(exclude_none=True),
            "updated_at": datetime.utcnow()
        }

        await collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": update_data}
        )

        return await self.get_workspace(workspace_id)

    async def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace (owner only)"""
        workspace = await self.get_workspace(workspace_id)

        if not workspace or workspace.owner_id != user_id:
            raise PermissionError("Only owner can delete workspace")

        collection = get_workspaces_collection()
        result = await collection.delete_one({"_id": ObjectId(workspace_id)})
        return result.deleted_count > 0

    async def invite_member(
        self,
        workspace_id: str,
        email: str,
        role: WorkspaceMemberRole,
        inviter_id: str
    ) -> WorkspaceInvite:
        """Invite member to workspace"""
        collection = get_workspace_invites_collection()

        # Check if user is already a member
        workspace = await self.get_workspace(workspace_id)
        if workspace:
            existing = next(
                (m for m in workspace.members if m.user_id == email),
                None
            )
            if existing:
                raise ValueError("User is already a member")

        # Create invite
        invite = WorkspaceInvite(
            email=email,
            role=role,
            workspace_id=workspace_id,
            invited_by=inviter_id,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days
        )

        result = await collection.insert_one(invite.dict())
        return invite

    async def accept_invite(self, invite_id: str, user_id: str) -> bool:
        """Accept workspace invite"""
        collection = get_workspace_invites_collection()
        invites = get_workspace_invites_collection()

        # Get invite
        invite = await collection.find_one({"_id": ObjectId(invite_id)})
        if not invite:
            raise ValueError("Invite not found")

        if invite["expires_at"] < datetime.utcnow():
            await collection.update_one(
                {"_id": ObjectId(invite_id)},
                {"$set": {"status": "expired"}}
            )
            raise ValueError("Invite has expired")

        # Add member to workspace
        workspaces = get_workspaces_collection()
        await workspaces.update_one(
            {"_id": ObjectId(invite["workspace_id"])},
            {
                "$push": {
                    "members": {
                        "user_id": user_id,
                        "role": invite["role"],
                        "joined_at": datetime.utcnow(),
                        "status": "active"
                    }
                }
            }
        )

        # Update invite status
        await collection.update_one(
            {"_id": ObjectId(invite_id)},
            {"$set": {"status": "accepted"}}
        )

        return True

    async def remove_member(
        self,
        workspace_id: str,
        user_id: str,
        remover_id: str
    ) -> bool:
        """Remove member from workspace"""
        workspace = await self.get_workspace(workspace_id)

        if not workspace:
            raise ValueError("Workspace not found")

        # Check permissions
        remover = next(
            (m for m in workspace.members if m.user_id == remover_id),
            None
        )
        if not remover:
            raise PermissionError("Not a member")

        # Owner can remove anyone
        # Admin can remove non-owners
        # Members can only remove themselves
        if (
            remover.role != WorkspaceMemberRole.OWNER and
            (
                remover.role != WorkspaceMemberRole.ADMIN or
                user_id == workspace.owner_id
            ) and
            user_id != remover_id
        ):
            raise PermissionError("Insufficient permissions")

        # Remove member
        collection = get_workspaces_collection()
        result = await collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$pull": {"members": {"user_id": user_id}}}
        )

        return result.modified_count > 0

    async def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        new_role: WorkspaceMemberRole,
        updater_id: str
    ) -> bool:
        """Update member role (owner/admin only)"""
        workspace = await self.get_workspace(workspace_id)

        if not workspace:
            raise ValueError("Workspace not found")

        # Check permissions (owner or admin)
        updater = next(
            (m for m in workspace.members if m.user_id == updater_id),
            None
        )
        if not updater or updater.role not in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]:
            raise PermissionError("Insufficient permissions")

        # Cannot change owner role
        if user_id == workspace.owner_id:
            raise ValueError("Cannot change owner role")

        # Cannot promote to owner
        if new_role == WorkspaceMemberRole.OWNER:
            raise ValueError("Cannot promote to owner")

        # Update role
        collection = get_workspaces_collection()
        result = await collection.update_one(
            {
                "_id": ObjectId(workspace_id),
                "members.user_id": user_id
            },
            {"$set": {"members.$.role": new_role}}
        )

        return result.modified_count > 0
```

#### 3.1.4 Create Workspace API Endpoints

**File**: `backend/app/api/workspaces.py` (create new)

```python
# backend/app/api/workspaces.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from backend.app.models.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    Workspace,
    WorkspaceMember,
    WorkspaceInvite,
    WorkspaceMemberRole,
)
from backend.app.services.workspace_service import WorkspaceService
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])
workspace_service = WorkspaceService()

@router.post("", response_model=Workspace, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new workspace"""
    try:
        return await workspace_service.create_workspace(
            workspace_data,
            current_user["id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[Workspace])
async def list_workspaces(
    current_user: dict = Depends(get_current_user)
):
    """List user's workspaces"""
    try:
        return await workspace_service.get_user_workspaces(current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}", response_model=Workspace)
async def get_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workspace by ID"""
    try:
        workspace = await workspace_service.get_workspace(workspace_id)

        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Check if user is member
        is_member = any(
            m.user_id == current_user["id"] for m in workspace.members
        )
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member")

        return workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: str,
    updates: WorkspaceUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update workspace (owner/admin only)"""
    try:
        return await workspace_service.update_workspace(
            workspace_id,
            updates,
            current_user["id"]
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete workspace (owner only)"""
    try:
        success = await workspace_service.delete_workspace(
            workspace_id,
            current_user["id"]
        )
        if not success:
            raise HTTPException(status_code=404, detail="Workspace not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{workspace_id}/invite")
async def invite_member(
    workspace_id: str,
    email: str,
    role: WorkspaceMemberRole = WorkspaceMemberRole.MEMBER,
    current_user: dict = Depends(get_current_user)
):
    """Invite member to workspace (owner/admin only)"""
    try:
        return await workspace_service.invite_member(
            workspace_id,
            email,
            role,
            current_user["id"]
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{workspace_id}/members/{member_id}/remove")
async def remove_member(
    workspace_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove member from workspace"""
    try:
        success = await workspace_service.remove_member(
            workspace_id,
            member_id,
            current_user["id"]
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{workspace_id}/members/{member_id}/role")
async def update_member_role(
    workspace_id: str,
    member_id: str,
    new_role: WorkspaceMemberRole,
    current_user: dict = Depends(get_current_user)
):
    """Update member role (owner/admin only)"""
    try:
        success = await workspace_service.update_member_role(
            workspace_id,
            member_id,
            new_role,
            current_user["id"]
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Update backend/app/main.py**:
```python
# Add to backend/app/main.py
from backend.app.api import workspaces

app.include_router(workspaces.router)
```

#### 3.1.5 Create Frontend Components

**File**: `frontend/src/pages/Workspace.tsx` (create/modify)

```typescript
// frontend/src/pages/Workspace.tsx
import { useParams } from 'react-router-dom'
import { useWorkspaces, useWorkspace } from '@/hooks/useWorkspace'
import Button from '@/components/common/Button'
import LoadingSpinner from '@/components/common/LoadingSpinner'

export default function Workspace() {
  const { id } = useParams<{ id: string }>()
  const { workspace, loading, error } = useWorkspace(id!)

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !workspace) {
    return <div>Workspace not found</div>
  }

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{workspace.name}</h1>
        {workspace.description && (
          <p className="text-text-secondary">{workspace.description}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Members section */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Members</h2>
          <div className="space-y-3">
            {workspace.members.map((member) => (
              <div
                key={member.user_id}
                className="flex items-center justify-between p-3 bg-bg-secondary rounded"
              >
                <div>
                  <p className="font-medium">{member.user_id}</p>
                  <p className="text-sm text-text-secondary capitalize">
                    {member.role}
                  </p>
                </div>
                <span className="badge badge-success">
                  {member.status}
                </span>
              </div>
            ))}
          </div>

          <Button
            variant="primary"
            className="mt-4"
            onClick={() => console.log('Invite member')}
          >
            Invite Member
          </Button>
        </div>

        {/* Tasks section */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Tasks</h2>
          <p className="text-text-secondary">
            Workspace tasks will appear here
          </p>
          <Button
            variant="secondary"
            className="mt-4"
            onClick={() => console.log('View tasks')}
          >
            View All Tasks
          </Button>
        </div>
      </div>
    </div>
  )
}
```

**Deliverables**:
- ✅ Workspace data models
- ✅ MongoDB collections with indexes
- ✅ Workspace service with all operations
- ✅ Workspace API endpoints
- ✅ Frontend workspace page
- ✅ Member management UI

**Acceptance Criteria**:
```bash
# Test 1: Create workspace works
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workspace"}'
# Expected: Workspace created, ID returned

# Test 2: Invite member works
curl -X POST http://localhost:8000/api/v1/workspaces/{id}/invite \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","role":"member"}'
# Expected: Invite created

# Test 3: Role permissions work
# Try to update workspace as guest
# Expected: 403 Forbidden
```

**Third-Party Credentials Required**:
```env
# Email service for invite emails (optional)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.xxxxxxxxxxxxxxxxxxxxxxxxx

# Get from: https://sendgrid.com/
# Free tier: 100 emails/day
# Paid tier: $15/month for 40,000 emails
```

**Dependencies**:
- Backend (Phase 1)
- Frontend (Phase 2)
- SendGrid API key (optional, for email invites)

**Estimated Time**: 10-14 hours

---

### Task 3.2: Blocker Detection Implementation (8-12 hours) 🟢 MEDIUM

**Current State**:
- No blocker detection logic
- No inference worker
- No dependency analysis

**What's Missing**:

#### 3.2.1 Create Blocker Detection Service

**File**: `backend/app/services/blocker_detection_service.py` (create new)

```python
# backend/app/services/blocker_detection_service.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.app.db.database import get_tasks_collection
from backend.app.models.task import Task

class BlockerDetectionService:
    """Blocker detection using NLP and heuristics"""

    def __init__(self):
        # Blocker keywords
        self.blocker_keywords = [
            'waiting for', 'depends on', 'blocked by', 'pending',
            'waiting on', 'needs approval', 'requires review',
            'stuck', 'blocked', 'held up'
        ]

        # Time thresholds (days)
        self.stuck_thresholds = {
            'IN_PROGRESS': 7,  # Tasks in progress > 7 days
            'OPEN': 14,        # Tasks open > 14 days
        }

    async def detect_blockers_in_workspace(
        self,
        workspace_id: str
    ) -> List[Dict]:
        """Detect blockers for all tasks in workspace"""
        collection = get_tasks_collection()

        # Get all tasks in workspace
        cursor = collection.find({"workspace_id": workspace_id})
        tasks = [Task(**task) async for task in cursor]

        blocked_tasks = []

        for task in tasks:
            blockers = await self.analyze_task(task)
            if blockers:
                blocked_tasks.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'workspace_id': workspace_id,
                    'blockers': blockers,
                    'confidence': self._calculate_confidence(blockers),
                    'suggested_action': self._suggest_action(blockers)
                })

        return blocked_tasks

    async def analyze_task(self, task: Task) -> List[Dict]:
        """Analyze single task for blockers"""
        blockers = []

        # Check 1: Keyword-based blockers
        keyword_blockers = self._detect_keyword_blockers(task)
        blockers.extend(keyword_blockers)

        # Check 2: Duration-based blockers
        duration_blockers = self._detect_duration_blockers(task)
        blockers.extend(duration_blockers)

        # Check 3: Assignment-based blockers
        assignment_blockers = self._detect_assignment_blockers(task)
        blockers.extend(assignment_blockers)

        # Check 4: Dependency-based blockers (simple version)
        dependency_blockers = await self._detect_dependency_blockers(task)
        blockers.extend(dependency_blockers)

        return blockers

    def _detect_keyword_blockers(self, task: Task) -> List[Dict]:
        """Detect blockers from task text"""
        blockers = []

        text = (task.title + " " + (task.description or "")).lower()

        for keyword in self.blocker_keywords:
            if keyword in text:
                blockers.append({
                    'type': 'keyword',
                    'keyword': keyword,
                    'source': 'task_text',
                    'severity': 'medium',
                    'description': f'Detected blocker phrase: "{keyword}"'
                })

        return blockers

    def _detect_duration_blockers(self, task: Task) -> List[Dict]:
        """Detect blockers based on task duration in status"""
        blockers = []

        if task.status in self.stuck_thresholds:
            threshold = self.stuck_thresholds[task.status]
            duration = (datetime.utcnow() - task.updated_at).days

            if duration > threshold:
                blockers.append({
                    'type': 'duration',
                    'status': task.status,
                    'duration_days': duration,
                    'threshold_days': threshold,
                    'source': 'task_status',
                    'severity': 'high' if duration > threshold * 2 else 'medium',
                    'description': f'Task stuck in {task.status} for {duration} days'
                })

        return blockers

    def _detect_assignment_blockers(self, task: Task) -> List[Dict]:
        """Detect blockers based on assignment overload"""
        blockers = []

        if not task.assignee_id:
            blockers.append({
                'type': 'assignment',
                'source': 'task_assignment',
                'severity': 'low',
                'description': 'Task is unassigned'
            })

        return blockers

    async def _detect_dependency_blockers(self, task: Task) -> List[Dict]:
        """Detect blockers based on task dependencies"""
        blockers = []

        collection = get_tasks_collection()

        # Simple dependency detection: check for references to other tasks
        text = (task.title + " " + (task.description or "")).lower()

        # Look for task ID patterns (e.g., "task-123", "#123")
        import re
        task_id_pattern = r'(?:(?:task|#)\-?\s*)(\d+)'
        matches = re.findall(task_id_pattern, text)

        for match in matches:
            blockers.append({
                'type': 'dependency',
                'depends_on_task_id': match,
                'source': 'task_references',
                'severity': 'high',
                'description': f'Waiting for task #{match} to complete'
            })

        return blockers

    def _calculate_confidence(self, blockers: List[Dict]) -> float:
        """Calculate confidence score for blocker detection"""
        if not blockers:
            return 0.0

        # Base confidence
        confidence = 0.5

        # Increase for high severity
        high_severity = sum(1 for b in blockers if b['severity'] == 'high')
        confidence += high_severity * 0.15

        # Increase for multiple indicators
        confidence += len(blockers) * 0.05

        # Cap at 0.95
        return min(confidence, 0.95)

    def _suggest_action(self, blockers: List[Dict]) -> str:
        """Suggest action to unblock task"""
        if not blockers:
            return "No blockers detected"

        # Check for keyword blockers
        keyword_blockers = [b for b in blockers if b['type'] == 'keyword']
        if keyword_blockers:
            return "Follow up on the blocked dependency or remove blocker phrase"

        # Check for duration blockers
        duration_blockers = [b for b in blockers if b['type'] == 'duration']
        if duration_blockers:
            return "Update task status or break down into smaller tasks"

        # Check for assignment blockers
        assignment_blockers = [b for b in blockers if b['type'] == 'assignment']
        if assignment_blockers:
            return "Assign task to a team member"

        # Check for dependency blockers
        dependency_blockers = [b for b in blockers if b['type'] == 'dependency']
        if dependency_blockers:
            return "Complete dependent tasks or remove dependency"

        return "Review blockers and take action"
```

#### 3.2.2 Create Blocker Detection API

**File**: `backend/app/api/blockers.py` (create new)

```python
# backend/app/api/blockers.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.app.models.blocker import BlockedTask
from backend.app.services.blocker_detection_service import BlockerDetectionService
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/blockers", tags=["blockers"])
blocker_service = BlockerDetectionService()

@router.get("/workspace/{workspace_id}")
async def get_workspace_blockers(
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
) -> List[BlockedTask]:
    """Get blocked tasks in workspace"""
    # TODO: Check if user is member of workspace
    try:
        return await blocker_service.detect_blockers_in_workspace(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_blockers(
    task_id: str,
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get blockers for specific task"""
    # TODO: Check if user has access to task
    from backend.app.db.database import get_tasks_collection
    collection = get_tasks_collection()
    from bson import ObjectId
    from backend.app.models.task import Task

    task_data = await collection.find_one({"_id": ObjectId(task_id)})
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    task = Task(**task_data)
    blockers = await blocker_service.analyze_task(task)

    return [{
        'task_id': task_id,
        'task_title': task.title,
        'blockers': blockers,
        'confidence': blocker_service._calculate_confidence(blockers),
        'suggested_action': blocker_service._suggest_action(blockers)
    }]
```

**Update backend/app/main.py**:
```python
# Add to backend/app/main.py
from backend.app.api import blockers

app.include_router(blockers.router)
```

#### 3.2.3 Create Blocker Celery Task

**File**: `backend/app/workers/blocker_tasks.py` (update/modify)

```python
# Add to backend/app/workers/blocker_tasks.py
from backend.app.celery_app import celery_app
from backend.app.services.blocker_detection_service import BlockerDetectionService
import socketio

# Initialize service
blocker_detection_service = BlockerDetectionService()

# Socket.IO client for notifications
sio = socketio.Client()

@celery_app.task(name='detect_workspace_blockers')
def detect_workspace_blockers_task(workspace_id: str):
    """
    Detect blockers in workspace (scheduled task)

    - Runs every 5 minutes via Celery Beat
    - Emits notifications to workspace members
    """
    try:
        import asyncio
        blocked_tasks = asyncio.run(
            blocker_detection_service.detect_blockers_in_workspace(workspace_id)
        )

        if blocked_tasks:
            # Connect to Socket.IO server
            sio.connect('http://backend:8000')

            # Emit notifications
            for blocked_task in blocked_tasks:
                sio.emit(
                    'task_blocked',
                    blocked_task,
                    room=workspace_id
                )

            sio.disconnect()

        return {
            'status': 'success',
            'workspace_id': workspace_id,
            'blocked_count': len(blocked_tasks)
        }

    except Exception as e:
        print(f"Blocker detection failed for workspace {workspace_id}: {e}")
        raise detect_workspace_blockers_task.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(name='analyze_single_task')
def analyze_single_task_blockers(task_id: str):
    """
    Analyze single task for blockers

    - Triggered on task update
    - Emits notification if blockers found
    """
    try:
        import asyncio
        from backend.app.db.database import get_tasks_collection
        from bson import ObjectId
        from backend.app.models.task import Task

        collection = get_tasks_collection()
        task_data = asyncio.run(collection.find_one({"_id": ObjectId(task_id)}))

        if not task_data:
            return {'status': 'not_found'}

        task = Task(**task_data)
        blockers = asyncio.run(blocker_detection_service.analyze_task(task))

        if blockers:
            confidence = blocker_detection_service._calculate_confidence(blockers)

            # Emit notification
            sio.connect('http://backend:8000')
            sio.emit(
                'task_blocked',
                {
                    'task_id': task_id,
                    'task_title': task.title,
                    'workspace_id': task.workspace_id,
                    'blockers': blockers,
                    'confidence': confidence,
                    'suggested_action': blocker_detection_service._suggest_action(blockers)
                },
                room=task.workspace_id
            )
            sio.disconnect()

            return {
                'status': 'blocked',
                'task_id': task_id,
                'blockers': blockers
            }

        return {
            'status': 'success',
            'task_id': task_id,
            'blockers': []
        }

    except Exception as e:
        print(f"Task blocker analysis failed: {e}")
        raise
```

#### 3.2.4 Create Frontend Blocker Components

**File**: `frontend/src/components/blockers/BlockerAlert.tsx` (create new)

```typescript
// frontend/src/components/blockers/BlockerAlert.tsx
import { useState, useEffect } from 'react'
import { useSocket } from '@/hooks/useSocket'
import Button from '@/components/common/Button'
import { AlertTriangle, CheckCircle } from 'lucide-react'

interface BlockerAlertProps {
  task_id: string
  onDismiss?: () => void
}

export default function BlockerAlert({ task_id, onDismiss }: BlockerAlertProps) {
  const { socket } = useSocket()
  const [blockers, setBlockers] = useState<any[]>([])

  useEffect(() => {
    if (!socket) return

    // Listen for blocker notifications
    socket.on('task_blocked', (data: any) => {
      if (data.task_id === task_id) {
        setBlockers(data.blockers)
      }
    })

    return () => {
      socket.off('task_blocked')
    }
  }, [socket, task_id])

  if (blockers.length === 0) {
    return null
  }

  return (
    <div className="card p-4 mb-4 border-l-4 border-l-warning bg-yellow-50">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="font-semibold text-warning mb-2">
            Task Blocked
          </h4>

          <ul className="space-y-1 mb-3">
            {blockers.map((blocker, index) => (
              <li key={index} className="text-sm text-text-secondary">
                • {blocker.description}
              </li>
            ))}
          </ul>

          <p className="text-sm font-medium mb-3">
            Suggested: {blockers[0]?.suggested_action}
          </p>

          <div className="flex gap-2">
            <Button variant="primary" size="sm">
              Resolve Blockers
            </Button>
            {onDismiss && (
              <Button variant="secondary" size="sm" onClick={onDismiss}>
                Dismiss
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

**Deliverables**:
- ✅ Blocker detection service
- ✅ Blocker detection API
- ✅ Scheduled blocker detection task
- ✅ Frontend blocker alert component
- ✅ Real-time blocker notifications

**Acceptance Criteria**:
```bash
# Test 1: Detect keyword blockers
# Create task with title "Waiting for approval"
# Expected: Blocker detected, confidence > 0.7

# Test 2: Detect duration blockers
# Create task, set status IN_PROGRESS, wait 8 days
# Expected: Blocker detected for stuck task

# Test 3: Notifications work
# Trigger blocker detection
# Expected: Socket.IO notification emitted

# Test 4: Scheduled detection works
# Wait for scheduled task (5 min)
# Expected: Blockers detected periodically
```

**Dependencies**:
- Backend (Phase 1)
- Celery workers (Phase 1, Task 1.4)

**Estimated Time**: 8-12 hours

---

### Task 3.3: Time-aware Prioritization (6-10 hours) 🟢 MEDIUM

**Current State**:
- No calendar integration
- No velocity tracking
- No prioritization logic

**What's Missing**:

#### 3.3.1 Create Prioritization Service

**File**: `backend/app/services/prioritization_service.py` (create new)

```python
# backend/app/services/prioritization_service.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.app.models.task import Task

class PrioritizationService:
    """Time-aware task prioritization"""

    def __init__(self):
        # Weight configuration (sums to 1.0)
        self.weights = {
            'deadline': 0.40,      # 40% - deadline urgency
            'calendar': 0.30,      # 30% - calendar availability
            'velocity': 0.20,      # 20% - team velocity
            'load': 0.10          # 10% - team load
        }

    async def prioritize_tasks(
        self,
        task_ids: List[str],
        workspace_id: str,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Prioritize tasks based on multiple factors

        Factors:
        - Deadline urgency (due_date proximity)
        - Calendar availability (free time)
        - Team velocity (historical completion rate)
        - Team load (current assignments)
        """
        from backend.app.db.database import get_tasks_collection
        from bson import ObjectId

        collection = get_tasks_collection()

        # Fetch tasks
        cursor = collection.find({
            "_id": {"$in": [ObjectId(tid) for tid in task_ids]}
        })
        tasks = [Task(**task) async for task in cursor]

        prioritized = []

        for task in tasks:
            scores = {}

            # Calculate individual scores
            scores['deadline'] = self._calculate_deadline_score(task)
            scores['calendar'] = await self._calculate_calendar_score(
                task,
                user_id
            )
            scores['velocity'] = await self._calculate_velocity_score(
                task,
                workspace_id
            )
            scores['load'] = await self._calculate_load_score(
                task,
                workspace_id,
                user_id
            )

            # Calculate weighted score
            weighted_score = sum(
                scores[key] * self.weights[key]
                for key in scores.keys()
            )

            prioritized.append({
                'task_id': task.id,
                'task_title': task.title,
                'priority': task.priority,
                'due_date': task.due_date,
                'weighted_score': weighted_score,
                'scores': scores,
                'explanation': self._generate_explanation(scores)
            })

        # Sort by weighted score (descending)
        prioritized.sort(key=lambda x: x['weighted_score'], reverse=True)

        return prioritized

    def _calculate_deadline_score(self, task: Task) -> float:
        """
        Calculate deadline urgency score

        - Overdue: 1.0
        - Due today: 0.9
        - Due in 2 days: 0.7
        - Due in 7 days: 0.5
        - Due in 30 days: 0.3
        - No due date: 0.1
        """
        if not task.due_date:
            return 0.1

        due_date = datetime.fromisoformat(task.due_date)
        now = datetime.utcnow()
        days_until_due = (due_date - now).days

        if days_until_due < 0:
            return 1.0  # Overdue
        elif days_until_due == 0:
            return 0.9  # Due today
        elif days_until_due <= 2:
            return 0.7
        elif days_until_due <= 7:
            return 0.5
        elif days_until_due <= 30:
            return 0.3
        else:
            return 0.1

    async def _calculate_calendar_score(
        self,
        task: Task,
        user_id: Optional[str]
    ) -> float:
        """
        Calculate calendar availability score

        - High availability: 1.0
        - Medium availability: 0.5
        - Low availability: 0.1
        """
        # TODO: Integrate with Google Calendar API
        # For now, return mock score
        return 0.5

    async def _calculate_velocity_score(
        self,
        task: Task,
        workspace_id: str
    ) -> float:
        """
        Calculate team velocity score

        - High velocity: 1.0 (team completes tasks fast)
        - Medium velocity: 0.5
        - Low velocity: 0.1
        """
        # TODO: Calculate actual velocity from task completion history
        # For now, return mock score
        return 0.5

    async def _calculate_load_score(
        self,
        task: Task,
        workspace_id: str,
        user_id: Optional[str]
    ) -> float:
        """
        Calculate team load score

        - Low load: 1.0 (team has capacity)
        - Medium load: 0.5
        - High load: 0.1 (team overloaded)
        """
        # TODO: Calculate actual load from active tasks
        # For now, return mock score
        return 0.5

    def _generate_explanation(self, scores: Dict[str, float]) -> str:
        """Generate explanation for prioritization"""
        factors = []

        for factor, score in scores.items():
            if score >= 0.7:
                factors.append(f"{factor.capitalize()} (high)")
            elif score >= 0.4:
                factors.append(f"{factor.capitalize()} (medium)")
            else:
                factors.append(f"{factor.capitalize()} (low)")

        return "Prioritized based on: " + ", ".join(factors)
```

#### 3.3.2 Create Prioritization API

**File**: `backend/app/api/prioritization.py` (create new)

```python
# backend/app/api/prioritization.py
from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from backend.app.services.prioritization_service import PrioritizationService
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/prioritize", tags=["prioritization"])
prioritization_service = PrioritizationService()

class PrioritizeRequest(BaseModel):
    task_ids: List[str]
    workspace_id: str
    user_id: str = None

@router.post("/tasks")
async def prioritize_tasks(
    request: PrioritizeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Prioritize tasks based on context"""
    # TODO: Check if user is member of workspace
    try:
        return await prioritization_service.prioritize_tasks(
            task_ids=request.task_ids,
            workspace_id=request.workspace_id,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scores")
async def get_priority_explanation(
    task_id: str,
    workspace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed priority breakdown for task"""
    # TODO: Implement detailed scoring breakdown
    return {
        'task_id': task_id,
        'workspace_id': workspace_id,
        'scores': {
            'deadline': 0.7,
            'calendar': 0.5,
            'velocity': 0.5,
            'load': 0.5
        },
        'weighted_score': 0.58,
        'explanation': 'Prioritized based on: Deadline (high), Calendar (medium), Velocity (medium), Load (medium)'
    }
```

**Update backend/app/main.py**:
```python
# Add to backend/app/main.py
from backend.app.api import prioritization

app.include_router(prioritization.router)
```

**Deliverables**:
- ✅ Prioritization service
- ✅ Prioritization API
- ✅ Weighted scoring algorithm
- ✅ Detailed breakdown endpoint

**Acceptance Criteria**:
```bash
# Test 1: Prioritize tasks works
curl -X POST http://localhost:8000/api/v1/prioritize/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"task_ids":["1","2","3"],"workspace_id":"xyz"}'
# Expected: Tasks prioritized with scores

# Test 2: Deadline urgency calculated
# Create task due yesterday
# Prioritize tasks
# Expected: Task has high deadline score (> 0.9)

# Test 3: Explanation generated
# Get priority scores
# Expected: Explanation of weight breakdown
```

**Third-Party Credentials Required**:
```env
# Google Calendar API (optional)
GOOGLE_CALENDAR_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CALENDAR_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:3000/auth/callback/google-calendar

# Get from: https://console.cloud.google.com/
# 1. Create project
# 2. Enable Calendar API
# 3. Create OAuth 2.0 credentials
# 4. Get client ID and secret
```

**Dependencies**:
- Backend (Phase 1)
- Google Calendar API credentials (optional)

**Estimated Time**: 6-10 hours

---

## 📝 Document Continuation Note

Due to length constraints, this document includes the first 3 major tasks of Phase 3. The remaining tasks should be documented in a separate file:

**Remaining Tasks for Phase 3**:

4. **Task 3.4: Analytics Dashboard** (8-12 hours)
   - Metrics collection service
   - Analytics API endpoints
   - Frontend dashboard components
   - Business metrics tracking

5. **Task 3.5: OAuth2 Integration** (4-6 hours)
   - Google OAuth2 implementation
   - OAuth2 API endpoints
   - Frontend OAuth flow
   - Account linking

6. **Task 3.6: Security & Compliance** (8-12 hours)
   - RBAC implementation
   - Audit trail system
   - GDPR data export tools
   - Security middleware

7. **Task 3.7: CI/CD Pipeline** (6-10 hours)
   - GitHub Actions workflows
   - Automated testing
   - Deployment scripts
   - Environment configuration

8. **Task 3.8: Monitoring & Observability** (6-10 hours)
   - Prometheus metrics
   - Grafana dashboards
   - Sentry integration
   - Structured logging

9. **Task 3.9: Load Testing** (4-8 hours)
   - Locust test scripts
   - Performance benchmarks
   - Load testing automation
   - Results analysis

---

## 📊 Phase 3 Summary (Partial)

### Estimated Effort for Documented Tasks: 24-36 hours

| Task | Description | Time | Priority |
|------|-------------|------|----------|
| 3.1 | Workspace & member management | 10-14h | 🟢 Medium |
| 3.2 | Blocker detection | 8-12h | 🟢 Medium |
| 3.3 | Time-aware prioritization | 6-10h | 🟢 Medium |

**Remaining Tasks Estimated**: 36-51 hours
**Total Phase 3 Estimated**: 60-87 hours

### Third-Party Services Required

| Service | Purpose | Cost | Setup Time |
|---------|---------|------|------------|
| **SendGrid** | Email invites | Free/Pro | 15 min |
| **Google Calendar API** | Calendar integration | Free | 20 min |
| **Google OAuth2** | SSO integration | Free | 15 min |
| **Sentry** | Error tracking | Free/Pro | 10 min |
| **Prometheus/Grafana** | Monitoring | Free | 30 min |

### Third-Party Credentials Summary

```env
# Email Service (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxx

# Google Calendar API
GOOGLE_CALENDAR_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CALENDAR_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google OAuth2
GOOGLE_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Monitoring
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/xxxxxx
PROMETHEUS_PORT=9090

# Production (Optional)
# Redis Cloud for Celery
CELERY_BROKER_URL=redis://:password@redis-host:port/2

# MongoDB Atlas for production
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/pulsetasks
```

---

**Document Version**: 1.0
**Last Updated**: February 20, 2026
**Next Review**: After Task 3.3 completion
**Owner**: Full-Stack Development Team

**Note**: This document contains the first 3 tasks of Phase 3. Remaining tasks (3.4-3.9) should be documented in a continuation file due to length constraints.
