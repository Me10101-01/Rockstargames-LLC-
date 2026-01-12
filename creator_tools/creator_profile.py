"""
Creator Profile Model
Manages creator user profiles and permissions
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from enum import Enum


class CreatorRole(Enum):
    """Creator role types"""
    ADMIN = "admin"
    CREATOR = "creator"
    MODERATOR = "moderator"
    VIEWER = "viewer"


class Permission(Enum):
    """Permission types for creators"""
    CREATE_CREW = "create_crew"
    DELETE_CREW = "delete_crew"
    MANAGE_MEMBERS = "manage_members"
    UPDATE_CREW = "update_crew"
    VIEW_CREWS = "view_crews"
    MANAGE_PERMISSIONS = "manage_permissions"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    CreatorRole.ADMIN: [
        Permission.CREATE_CREW,
        Permission.DELETE_CREW,
        Permission.MANAGE_MEMBERS,
        Permission.UPDATE_CREW,
        Permission.VIEW_CREWS,
        Permission.MANAGE_PERMISSIONS
    ],
    CreatorRole.CREATOR: [
        Permission.CREATE_CREW,
        Permission.MANAGE_MEMBERS,
        Permission.UPDATE_CREW,
        Permission.VIEW_CREWS
    ],
    CreatorRole.MODERATOR: [
        Permission.MANAGE_MEMBERS,
        Permission.UPDATE_CREW,
        Permission.VIEW_CREWS
    ],
    CreatorRole.VIEWER: [
        Permission.VIEW_CREWS
    ]
}


@dataclass
class CreatorProfile:
    """Creator user profile"""
    creator_id: str
    username: str
    email: str
    role: CreatorRole
    created_date: datetime
    last_login: datetime
    is_active: bool = True
    crews_created: List[str] = field(default_factory=list)
    crews_managed: List[str] = field(default_factory=list)
    custom_permissions: List[Permission] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if creator has a specific permission"""
        if not self.is_active:
            return False
        
        # Check role-based permissions
        role_perms = ROLE_PERMISSIONS.get(self.role, [])
        if permission in role_perms:
            return True
        
        # Check custom permissions
        if permission in self.custom_permissions:
            return True
        
        return False
    
    def add_custom_permission(self, permission: Permission):
        """Add a custom permission to the creator"""
        if permission not in self.custom_permissions:
            self.custom_permissions.append(permission)
    
    def remove_custom_permission(self, permission: Permission):
        """Remove a custom permission from the creator"""
        if permission in self.custom_permissions:
            self.custom_permissions.remove(permission)
    
    def get_all_permissions(self) -> List[Permission]:
        """Get all permissions for this creator"""
        role_perms = ROLE_PERMISSIONS.get(self.role, [])
        all_perms = set(role_perms + self.custom_permissions)
        return list(all_perms)
