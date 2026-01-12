# Rockstar Creator Development / Crew Creation Pipeline
## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rockstar Creator Pipeline                     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌───────────┐   ┌───────────┐   ┌───────────┐
      │   Crew    │   │ Creator   │   │ Pipeline  │
      │  System   │   │   Tools   │   │Automation │
      └───────────┘   └───────────┘   └───────────┘
              │               │               │
              │               │               │
      ┌───────┴───────┐       │       ┌───────┴───────┐
      │               │       │       │               │
      ▼               ▼       ▼       ▼               ▼
  ┌────────┐    ┌─────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
  │ Models │    │Services │ │Profiles│ │Validate │ │ Deploy  │
  └────────┘    └─────────┘ └────────┘ └─────────┘ └─────────┘
      │              │           │           │           │
      │              │           │           │           │
      ▼              ▼           ▼           ▼           ▼
  ┌────────────────────────────────────────────────────────┐
  │                     Data Storage                        │
  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │
  │  │   Crews    │  │  Creators  │  │ Production │      │
  │  │   (JSON)   │  │   (JSON)   │  │   Deploy   │      │
  │  └────────────┘  └────────────┘  └────────────┘      │
  └────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Crew System
**Models:**
- `Crew`: Main crew entity
- `CrewMember`: Individual member
- `CrewRank`: Hierarchical ranks (5 levels)
- `CrewStatus`: Crew operational states

**Services:**
- `CrewCreationService`: Complete crew lifecycle management
  - Create, read, update, delete operations
  - Member management
  - Reputation tracking
  - Validation and persistence

### 2. Creator Tools
**Profiles:**
- `CreatorProfile`: User profile with permissions
- `CreatorRole`: Role types (Admin, Creator, Moderator, Viewer)
- `Permission`: Fine-grained permission types

**Services:**
- `CreatorManagementService`: Creator profile management
  - Account creation and management
  - Role-based access control
  - Permission authorization
  - Activity tracking

### 3. Pipeline Automation
**Build:**
- `build.sh`: Complete system validation
  - Directory structure check
  - Syntax validation
  - Crew file validation
  - Build info generation

**Validation:**
- `validate_crew.py`: Crew data validation
  - Schema validation
  - Business rule checks
  - Detailed error reporting

**Deployment:**
- `deploy_crew.py`: Safe deployment
  - Automatic backups
  - File copying
  - Deployment logging

**CLI:**
- `crew_cli.py`: Command-line interface
  - Crew management commands
  - Creator management commands
  - Interactive operations

## Data Flow

```
1. Creation Flow:
   Creator Profile → Authorization Check → Crew Creation → Validation → Storage

2. Deployment Flow:
   Source Crews → Validation → Backup → Deploy → Production → Log

3. Management Flow:
   CLI/API → Service Layer → Model Validation → Data Persistence
```

## Permission System

```
Admin
  ├─ CREATE_CREW
  ├─ DELETE_CREW
  ├─ MANAGE_MEMBERS
  ├─ UPDATE_CREW
  ├─ VIEW_CREWS
  └─ MANAGE_PERMISSIONS

Creator
  ├─ CREATE_CREW
  ├─ MANAGE_MEMBERS
  ├─ UPDATE_CREW
  └─ VIEW_CREWS

Moderator
  ├─ MANAGE_MEMBERS
  ├─ UPDATE_CREW
  └─ VIEW_CREWS

Viewer
  └─ VIEW_CREWS
```

## Rank Hierarchy

```
Leader (Highest Authority)
  ↓
Commissioner (Administrative)
  ↓
Lieutenant (Officer)
  ↓
Representative (Recruitment)
  ↓
Muscle (Basic Member)
```

## Testing Architecture

```
Unit Tests (28 tests)
  ├─ Crew System Tests (17 tests)
  │    ├─ Model Tests (8 tests)
  │    ├─ Member Tests (3 tests)
  │    └─ Service Tests (6 tests)
  │
  └─ Creator Tools Tests (11 tests)
       ├─ Profile Tests (5 tests)
       └─ Service Tests (6 tests)
```

## Configuration Management

```
Environment Configs
  ├─ development.conf
  │    ├─ Local paths
  │    ├─ Debug logging
  │    └─ No approval required
  │
  └─ production.conf
       ├─ System paths
       ├─ Warning logging
       └─ Approval required
```

## Usage Examples

### Python API
```python
from crew_system.services import CrewCreationService
service = CrewCreationService()
crew = service.create_crew("Warriors", "WARR", "user1", "Leader1")
```

### Command Line
```bash
python3 pipeline/crew_cli.py create --name "Warriors" --tag "WARR" \
    --leader-id "user1" --leader-username "Leader1"
```

### Validation
```bash
python3 pipeline/validate_crew.py data/crews/
```

### Deployment
```bash
python3 pipeline/deploy_crew.py data/crews/ data/production/crews/
```
