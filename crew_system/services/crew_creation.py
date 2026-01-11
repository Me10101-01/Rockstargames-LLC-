"""
Crew Creation Service
Handles the creation and management of crews in the Rockstar Creator system
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from ..models import Crew, CrewMember, CrewRank, CrewStatus


class CrewCreationService:
    """Service for creating and managing crews"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the crew creation service
        
        Args:
            storage_path: Path to store crew data (default: ./data/crews)
        """
        self.storage_path = Path(storage_path or "./data/crews")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.crews_cache: Dict[str, Crew] = {}
        self._load_all_crews()
    
    def create_crew(
        self,
        crew_name: str,
        crew_tag: str,
        leader_id: str,
        leader_username: str,
        motto: str = "",
        description: str = "",
        color_primary: str = "#000000",
        color_secondary: str = "#FFFFFF"
    ) -> Crew:
        """
        Create a new crew
        
        Args:
            crew_name: Name of the crew
            crew_tag: 4-letter crew tag
            leader_id: User ID of the crew leader
            leader_username: Username of the crew leader
            motto: Crew motto
            description: Crew description
            color_primary: Primary color (hex)
            color_secondary: Secondary color (hex)
            
        Returns:
            Created Crew object
            
        Raises:
            ValueError: If crew data is invalid
        """
        # Validate crew tag
        if len(crew_tag) != 4:
            raise ValueError("Crew tag must be exactly 4 characters")
        
        # Check if crew tag already exists
        if self._crew_tag_exists(crew_tag):
            raise ValueError(f"Crew tag '{crew_tag}' already exists")
        
        # Generate unique crew ID
        crew_id = str(uuid.uuid4())
        
        # Create leader as first member
        leader = CrewMember(
            user_id=leader_id,
            username=leader_username,
            rank=CrewRank.LEADER,
            joined_date=datetime.now()
        )
        
        # Create crew
        crew = Crew(
            crew_id=crew_id,
            crew_name=crew_name,
            crew_tag=crew_tag.upper(),
            leader_id=leader_id,
            created_date=datetime.now(),
            members=[leader],
            motto=motto,
            description=description,
            color_primary=color_primary,
            color_secondary=color_secondary
        )
        
        # Validate crew
        errors = crew.validate()
        if errors:
            raise ValueError(f"Crew validation failed: {', '.join(errors)}")
        
        # Save crew
        self._save_crew(crew)
        self.crews_cache[crew_id] = crew
        
        return crew
    
    def get_crew(self, crew_id: str) -> Optional[Crew]:
        """Get a crew by ID"""
        return self.crews_cache.get(crew_id)
    
    def get_crew_by_tag(self, crew_tag: str) -> Optional[Crew]:
        """Get a crew by tag"""
        for crew in self.crews_cache.values():
            if crew.crew_tag.upper() == crew_tag.upper():
                return crew
        return None
    
    def list_crews(self, status: Optional[CrewStatus] = None) -> List[Crew]:
        """
        List all crews, optionally filtered by status
        
        Args:
            status: Filter by crew status (optional)
            
        Returns:
            List of crews
        """
        crews = list(self.crews_cache.values())
        if status:
            crews = [c for c in crews if c.status == status]
        return crews
    
    def update_crew(self, crew: Crew) -> bool:
        """
        Update an existing crew
        
        Args:
            crew: Crew object with updated data
            
        Returns:
            True if successful
        """
        if crew.crew_id not in self.crews_cache:
            return False
        
        errors = crew.validate()
        if errors:
            raise ValueError(f"Crew validation failed: {', '.join(errors)}")
        
        self._save_crew(crew)
        self.crews_cache[crew.crew_id] = crew
        return True
    
    def delete_crew(self, crew_id: str) -> bool:
        """
        Delete a crew (mark as disbanded)
        
        Args:
            crew_id: ID of the crew to delete
            
        Returns:
            True if successful
        """
        crew = self.get_crew(crew_id)
        if not crew:
            return False
        
        crew.status = CrewStatus.DISBANDED
        self._save_crew(crew)
        return True
    
    def add_member_to_crew(
        self,
        crew_id: str,
        user_id: str,
        username: str,
        rank: CrewRank = CrewRank.MUSCLE
    ) -> bool:
        """
        Add a member to a crew
        
        Args:
            crew_id: ID of the crew
            user_id: User ID of the member
            username: Username of the member
            rank: Initial rank (default: MUSCLE)
            
        Returns:
            True if successful
        """
        crew = self.get_crew(crew_id)
        if not crew:
            return False
        
        member = CrewMember(
            user_id=user_id,
            username=username,
            rank=rank,
            joined_date=datetime.now()
        )
        
        if crew.add_member(member):
            self._save_crew(crew)
            return True
        return False
    
    def remove_member_from_crew(self, crew_id: str, user_id: str) -> bool:
        """Remove a member from a crew"""
        crew = self.get_crew(crew_id)
        if not crew:
            return False
        
        # Don't allow removing the leader
        if crew.is_leader(user_id):
            return False
        
        if crew.remove_member(user_id):
            self._save_crew(crew)
            return True
        return False
    
    def _crew_tag_exists(self, crew_tag: str) -> bool:
        """Check if a crew tag already exists"""
        for crew in self.crews_cache.values():
            if crew.crew_tag.upper() == crew_tag.upper():
                return True
        return False
    
    def _save_crew(self, crew: Crew):
        """Save crew data to storage"""
        crew_file = self.storage_path / f"{crew.crew_id}.json"
        crew_data = {
            'crew_id': crew.crew_id,
            'crew_name': crew.crew_name,
            'crew_tag': crew.crew_tag,
            'leader_id': crew.leader_id,
            'created_date': crew.created_date.isoformat(),
            'status': crew.status.value,
            'motto': crew.motto,
            'description': crew.description,
            'emblem_url': crew.emblem_url,
            'color_primary': crew.color_primary,
            'color_secondary': crew.color_secondary,
            'total_reputation': crew.total_reputation,
            'max_members': crew.max_members,
            'metadata': crew.metadata,
            'members': [
                {
                    'user_id': m.user_id,
                    'username': m.username,
                    'rank': m.rank.value,
                    'joined_date': m.joined_date.isoformat(),
                    'reputation_points': m.reputation_points,
                    'missions_completed': m.missions_completed
                }
                for m in crew.members
            ]
        }
        
        with open(crew_file, 'w') as f:
            json.dump(crew_data, f, indent=2)
    
    def _load_crew(self, crew_file: Path) -> Optional[Crew]:
        """Load crew data from file"""
        try:
            with open(crew_file, 'r') as f:
                data = json.load(f)
            
            members = [
                CrewMember(
                    user_id=m['user_id'],
                    username=m['username'],
                    rank=CrewRank(m['rank']),
                    joined_date=datetime.fromisoformat(m['joined_date']),
                    reputation_points=m.get('reputation_points', 0),
                    missions_completed=m.get('missions_completed', 0)
                )
                for m in data.get('members', [])
            ]
            
            crew = Crew(
                crew_id=data['crew_id'],
                crew_name=data['crew_name'],
                crew_tag=data['crew_tag'],
                leader_id=data['leader_id'],
                created_date=datetime.fromisoformat(data['created_date']),
                status=CrewStatus(data['status']),
                members=members,
                motto=data.get('motto', ''),
                description=data.get('description', ''),
                emblem_url=data.get('emblem_url'),
                color_primary=data.get('color_primary', '#000000'),
                color_secondary=data.get('color_secondary', '#FFFFFF'),
                total_reputation=data.get('total_reputation', 0),
                max_members=data.get('max_members', 1000),
                metadata=data.get('metadata', {})
            )
            
            return crew
        except Exception as e:
            print(f"Error loading crew from {crew_file}: {e}")
            return None
    
    def _load_all_crews(self):
        """Load all crews from storage"""
        if not self.storage_path.exists():
            return
        
        for crew_file in self.storage_path.glob("*.json"):
            crew = self._load_crew(crew_file)
            if crew:
                self.crews_cache[crew.crew_id] = crew
