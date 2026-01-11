"""
Crew data model for Rockstar Creator Development System
Defines the structure and validation for crew entities
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class CrewRank(Enum):
    """Crew member rank levels"""
    LEADER = "leader"
    COMMISSIONER = "commissioner"
    LIEUTENANT = "lieutenant"
    REPRESENTATIVE = "representative"
    MUSCLE = "muscle"


class CrewStatus(Enum):
    """Crew status states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISBANDED = "disbanded"


@dataclass
class CrewMember:
    """Represents a member of a crew"""
    user_id: str
    username: str
    rank: CrewRank
    joined_date: datetime
    reputation_points: int = 0
    missions_completed: int = 0
    
    def promote(self) -> bool:
        """Promote member to next rank level"""
        ranks = list(CrewRank)
        current_index = ranks.index(self.rank)
        if current_index > 0:
            self.rank = ranks[current_index - 1]
            return True
        return False
    
    def demote(self) -> bool:
        """Demote member to lower rank level"""
        ranks = list(CrewRank)
        current_index = ranks.index(self.rank)
        if current_index < len(ranks) - 1:
            self.rank = ranks[current_index + 1]
            return True
        return False


@dataclass
class Crew:
    """Main crew entity for the Rockstar Creator system"""
    crew_id: str
    crew_name: str
    crew_tag: str  # Short 4-letter tag
    leader_id: str
    created_date: datetime
    status: CrewStatus = CrewStatus.ACTIVE
    members: List[CrewMember] = field(default_factory=list)
    motto: str = ""
    description: str = ""
    emblem_url: Optional[str] = None
    color_primary: str = "#000000"
    color_secondary: str = "#FFFFFF"
    total_reputation: int = 0
    max_members: int = 1000
    metadata: Dict = field(default_factory=dict)
    
    def add_member(self, member: CrewMember) -> bool:
        """Add a new member to the crew"""
        if len(self.members) >= self.max_members:
            return False
        if any(m.user_id == member.user_id for m in self.members):
            return False
        self.members.append(member)
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the crew"""
        initial_count = len(self.members)
        self.members = [m for m in self.members if m.user_id != user_id]
        return len(self.members) < initial_count
    
    def get_member(self, user_id: str) -> Optional[CrewMember]:
        """Get a member by user ID"""
        for member in self.members:
            if member.user_id == user_id:
                return member
        return None
    
    def update_reputation(self, points: int):
        """Update crew's total reputation"""
        self.total_reputation += points
        if self.total_reputation < 0:
            self.total_reputation = 0
    
    def get_members_by_rank(self, rank: CrewRank) -> List[CrewMember]:
        """Get all members of a specific rank"""
        return [m for m in self.members if m.rank == rank]
    
    def is_leader(self, user_id: str) -> bool:
        """Check if user is the crew leader"""
        return self.leader_id == user_id
    
    def validate(self) -> List[str]:
        """Validate crew data and return list of errors"""
        errors = []
        
        if not self.crew_name or len(self.crew_name) < 3:
            errors.append("Crew name must be at least 3 characters")
        
        if not self.crew_tag or len(self.crew_tag) != 4:
            errors.append("Crew tag must be exactly 4 characters")
        
        if not any(m.user_id == self.leader_id for m in self.members):
            errors.append("Leader must be a member of the crew")
        
        leader_count = len([m for m in self.members if m.rank == CrewRank.LEADER])
        if leader_count > 1:
            errors.append("Crew can only have one leader")
        
        return errors
