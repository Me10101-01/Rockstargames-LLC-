# API Documentation

## Crew System API

### Data Models

#### Crew

Main crew entity containing all crew information and members.

**Fields:**
- `crew_id` (str): Unique identifier
- `crew_name` (str): Display name (3-50 characters)
- `crew_tag` (str): 4-letter identifier
- `leader_id` (str): User ID of crew leader
- `created_date` (datetime): Creation timestamp
- `status` (CrewStatus): Current status (active/inactive/suspended/disbanded)
- `members` (List[CrewMember]): List of crew members
- `motto` (str): Crew motto
- `description` (str): Crew description
- `emblem_url` (str, optional): URL to crew emblem
- `color_primary` (str): Primary color (hex)
- `color_secondary` (str): Secondary color (hex)
- `total_reputation` (int): Total crew reputation
- `max_members` (int): Maximum member capacity
- `metadata` (dict): Additional custom data

**Methods:**
```python
add_member(member: CrewMember) -> bool
remove_member(user_id: str) -> bool
get_member(user_id: str) -> Optional[CrewMember]
update_reputation(points: int) -> None
get_members_by_rank(rank: CrewRank) -> List[CrewMember]
is_leader(user_id: str) -> bool
validate() -> List[str]
```

#### CrewMember

Represents an individual member of a crew.

**Fields:**
- `user_id` (str): Unique user identifier
- `username` (str): Display username
- `rank` (CrewRank): Member rank
- `joined_date` (datetime): Join timestamp
- `reputation_points` (int): Individual reputation
- `missions_completed` (int): Number of missions completed

**Methods:**
```python
promote() -> bool  # Promote to next rank
demote() -> bool   # Demote to lower rank
```

#### CrewRank (Enum)

Member rank levels in hierarchical order:
- `LEADER` - Highest authority
- `COMMISSIONER` - Administrative role
- `LIEUTENANT` - Officer role
- `REPRESENTATIVE` - Recruitment role
- `MUSCLE` - Basic member

#### CrewStatus (Enum)

Crew operational status:
- `ACTIVE` - Currently operational
- `INACTIVE` - Temporarily inactive
- `SUSPENDED` - Administratively suspended
- `DISBANDED` - Permanently closed

### CrewCreationService

Service class for managing crew lifecycle.

#### Initialization

```python
from crew_system.services import CrewCreationService

service = CrewCreationService(storage_path="./data/crews")
```

**Parameters:**
- `storage_path` (str, optional): Path for data storage. Default: `./data/crews`

#### Methods

##### create_crew()

Create a new crew.

```python
crew = service.create_crew(
    crew_name="Elite Warriors",
    crew_tag="ELIT",
    leader_id="user123",
    leader_username="CommanderX",
    motto="Victory through unity",
    description="A crew dedicated to excellence",
    color_primary="#FF0000",
    color_secondary="#000000"
)
```

**Parameters:**
- `crew_name` (str): Crew name (3-50 chars)
- `crew_tag` (str): 4-letter tag (must be unique)
- `leader_id` (str): User ID of leader
- `leader_username` (str): Username of leader
- `motto` (str, optional): Crew motto
- `description` (str, optional): Crew description
- `color_primary` (str, optional): Primary color hex
- `color_secondary` (str, optional): Secondary color hex

**Returns:** `Crew` object

**Raises:** `ValueError` if validation fails or tag exists

##### get_crew()

Retrieve a crew by ID.

```python
crew = service.get_crew("crew-uuid-123")
```

**Returns:** `Crew` or `None`

##### get_crew_by_tag()

Retrieve a crew by tag.

```python
crew = service.get_crew_by_tag("ELIT")
```

**Returns:** `Crew` or `None`

##### list_crews()

List all crews, optionally filtered by status.

```python
active_crews = service.list_crews(status=CrewStatus.ACTIVE)
all_crews = service.list_crews()
```

**Returns:** `List[Crew]`

##### add_member_to_crew()

Add a member to a crew.

```python
success = service.add_member_to_crew(
    crew_id="crew-uuid-123",
    user_id="user456",
    username="NewMember",
    rank=CrewRank.MUSCLE
)
```

**Returns:** `bool` indicating success

##### remove_member_from_crew()

Remove a member from a crew (cannot remove leader).

```python
success = service.remove_member_from_crew(
    crew_id="crew-uuid-123",
    user_id="user456"
)
```

**Returns:** `bool` indicating success

##### update_crew()

Update crew information.

```python
crew.motto = "New motto"
success = service.update_crew(crew)
```

**Returns:** `bool` indicating success

##### delete_crew()

Mark a crew as disbanded.

```python
success = service.delete_crew("crew-uuid-123")
```

**Returns:** `bool` indicating success

## Creator Tools API

### Data Models

#### CreatorProfile

User profile for crew creators.

**Fields:**
- `creator_id` (str): Unique identifier
- `username` (str): Username
- `email` (str): Email address
- `role` (CreatorRole): User role
- `created_date` (datetime): Account creation date
- `last_login` (datetime): Last login timestamp
- `is_active` (bool): Account status
- `crews_created` (List[str]): Created crew IDs
- `crews_managed` (List[str]): Managed crew IDs
- `custom_permissions` (List[Permission]): Additional permissions
- `metadata` (dict): Custom data

**Methods:**
```python
has_permission(permission: Permission) -> bool
add_custom_permission(permission: Permission) -> None
remove_custom_permission(permission: Permission) -> None
get_all_permissions() -> List[Permission]
```

#### CreatorRole (Enum)

User role types:
- `ADMIN` - Full system access
- `CREATOR` - Can create and manage crews
- `MODERATOR` - Can manage existing crews
- `VIEWER` - Read-only access

#### Permission (Enum)

Permission types:
- `CREATE_CREW` - Create new crews
- `DELETE_CREW` - Delete crews
- `MANAGE_MEMBERS` - Add/remove members
- `UPDATE_CREW` - Modify crew data
- `VIEW_CREWS` - View crew information
- `MANAGE_PERMISSIONS` - Grant/revoke permissions

### CreatorManagementService

Service class for managing creator accounts.

#### Initialization

```python
from creator_tools import CreatorManagementService, CreatorRole

service = CreatorManagementService(storage_path="./data/creators")
```

#### Methods

##### create_creator()

Create a new creator profile.

```python
creator = service.create_creator(
    username="john_creator",
    email="john@example.com",
    role=CreatorRole.CREATOR
)
```

**Returns:** `CreatorProfile` object

**Raises:** `ValueError` if username exists

##### get_creator()

Retrieve creator by ID.

```python
creator = service.get_creator("creator-uuid-123")
```

**Returns:** `CreatorProfile` or `None`

##### get_creator_by_username()

Retrieve creator by username.

```python
creator = service.get_creator_by_username("john_creator")
```

**Returns:** `CreatorProfile` or `None`

##### list_creators()

List all creators, optionally filtered by role.

```python
admins = service.list_creators(role=CreatorRole.ADMIN)
all_creators = service.list_creators()
```

**Returns:** `List[CreatorProfile]`

##### authorize_action()

Check if creator has permission for an action.

```python
authorized = service.authorize_action(
    creator_id="creator-uuid-123",
    permission=Permission.CREATE_CREW
)
```

**Returns:** `bool`

##### update_creator()

Update creator profile.

```python
creator.email = "newemail@example.com"
success = service.update_creator(creator)
```

**Returns:** `bool`

##### deactivate_creator()

Deactivate a creator account.

```python
success = service.deactivate_creator("creator-uuid-123")
```

**Returns:** `bool`

## Example Usage

### Complete Workflow

```python
from crew_system.services import CrewCreationService
from crew_system.models import CrewRank
from creator_tools import CreatorManagementService, CreatorRole, Permission

# Initialize services
crew_service = CrewCreationService()
creator_service = CreatorManagementService()

# Create a creator
creator = creator_service.create_creator(
    username="game_master",
    email="master@example.com",
    role=CreatorRole.CREATOR
)

# Check if creator can create crews
if creator.has_permission(Permission.CREATE_CREW):
    # Create a crew
    crew = crew_service.create_crew(
        crew_name="Alpha Squad",
        crew_tag="ALPH",
        leader_id=creator.creator_id,
        leader_username=creator.username,
        motto="First in, last out",
        description="Elite tactical unit"
    )
    
    # Add the crew to creator's list
    creator.crews_created.append(crew.crew_id)
    creator_service.update_creator(creator)
    
    # Add more members
    crew_service.add_member_to_crew(
        crew_id=crew.crew_id,
        user_id="user789",
        username="Recruit1",
        rank=CrewRank.MUSCLE
    )
    
    # Update crew reputation
    crew.update_reputation(500)
    crew_service.update_crew(crew)
    
    print(f"Crew '{crew.crew_name}' created successfully!")
    print(f"Members: {len(crew.members)}")
    print(f"Reputation: {crew.total_reputation}")
```

### Error Handling

```python
try:
    crew = crew_service.create_crew(
        crew_name="Test",
        crew_tag="TOOLONG",  # Invalid: more than 4 chars
        leader_id="user1",
        leader_username="Leader"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```
