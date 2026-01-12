"""
Creator Management Service
Handles creator profiles and authentication
"""
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from .creator_profile import CreatorProfile, CreatorRole, Permission


class CreatorManagementService:
    """Service for managing creator profiles"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the creator management service
        
        Args:
            storage_path: Path to store creator data (default: ./data/creators)
        """
        self.storage_path = Path(storage_path or "./data/creators")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.creators_cache: Dict[str, CreatorProfile] = {}
        self._load_all_creators()
    
    def create_creator(
        self,
        username: str,
        email: str,
        role: CreatorRole = CreatorRole.CREATOR
    ) -> CreatorProfile:
        """
        Create a new creator profile
        
        Args:
            username: Creator username
            email: Creator email
            role: Creator role (default: CREATOR)
            
        Returns:
            Created CreatorProfile object
        """
        # Check if username already exists
        if self._username_exists(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Generate unique creator ID
        creator_id = str(uuid.uuid4())
        
        # Create profile
        profile = CreatorProfile(
            creator_id=creator_id,
            username=username,
            email=email,
            role=role,
            created_date=datetime.now(),
            last_login=datetime.now()
        )
        
        # Save profile
        self._save_creator(profile)
        self.creators_cache[creator_id] = profile
        
        return profile
    
    def get_creator(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get a creator by ID"""
        return self.creators_cache.get(creator_id)
    
    def get_creator_by_username(self, username: str) -> Optional[CreatorProfile]:
        """Get a creator by username"""
        for creator in self.creators_cache.values():
            if creator.username.lower() == username.lower():
                return creator
        return None
    
    def list_creators(self, role: Optional[CreatorRole] = None) -> List[CreatorProfile]:
        """
        List all creators, optionally filtered by role
        
        Args:
            role: Filter by creator role (optional)
            
        Returns:
            List of creator profiles
        """
        creators = list(self.creators_cache.values())
        if role:
            creators = [c for c in creators if c.role == role]
        return creators
    
    def update_creator(self, profile: CreatorProfile) -> bool:
        """
        Update an existing creator profile
        
        Args:
            profile: CreatorProfile object with updated data
            
        Returns:
            True if successful
        """
        if profile.creator_id not in self.creators_cache:
            return False
        
        self._save_creator(profile)
        self.creators_cache[profile.creator_id] = profile
        return True
    
    def deactivate_creator(self, creator_id: str) -> bool:
        """
        Deactivate a creator
        
        Args:
            creator_id: ID of the creator to deactivate
            
        Returns:
            True if successful
        """
        creator = self.get_creator(creator_id)
        if not creator:
            return False
        
        creator.is_active = False
        self._save_creator(creator)
        return True
    
    def authorize_action(
        self,
        creator_id: str,
        permission: Permission
    ) -> bool:
        """
        Check if a creator is authorized to perform an action
        
        Args:
            creator_id: ID of the creator
            permission: Required permission
            
        Returns:
            True if authorized
        """
        creator = self.get_creator(creator_id)
        if not creator:
            return False
        
        return creator.has_permission(permission)
    
    def _username_exists(self, username: str) -> bool:
        """Check if a username already exists"""
        for creator in self.creators_cache.values():
            if creator.username.lower() == username.lower():
                return True
        return False
    
    def _save_creator(self, profile: CreatorProfile):
        """Save creator profile to storage"""
        creator_file = self.storage_path / f"{profile.creator_id}.json"
        profile_data = {
            'creator_id': profile.creator_id,
            'username': profile.username,
            'email': profile.email,
            'role': profile.role.value,
            'created_date': profile.created_date.isoformat(),
            'last_login': profile.last_login.isoformat(),
            'is_active': profile.is_active,
            'crews_created': profile.crews_created,
            'crews_managed': profile.crews_managed,
            'custom_permissions': [p.value for p in profile.custom_permissions],
            'metadata': profile.metadata
        }
        
        with open(creator_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
    
    def _load_creator(self, creator_file: Path) -> Optional[CreatorProfile]:
        """Load creator profile from file"""
        try:
            with open(creator_file, 'r') as f:
                data = json.load(f)
            
            profile = CreatorProfile(
                creator_id=data['creator_id'],
                username=data['username'],
                email=data['email'],
                role=CreatorRole(data['role']),
                created_date=datetime.fromisoformat(data['created_date']),
                last_login=datetime.fromisoformat(data['last_login']),
                is_active=data.get('is_active', True),
                crews_created=data.get('crews_created', []),
                crews_managed=data.get('crews_managed', []),
                custom_permissions=[
                    Permission(p) for p in data.get('custom_permissions', [])
                ],
                metadata=data.get('metadata', {})
            )
            
            return profile
        except Exception as e:
            print(f"Error loading creator from {creator_file}: {e}")
            return None
    
    def _load_all_creators(self):
        """Load all creators from storage"""
        if not self.storage_path.exists():
            return
        
        for creator_file in self.storage_path.glob("*.json"):
            profile = self._load_creator(creator_file)
            if profile:
                self.creators_cache[profile.creator_id] = profile
