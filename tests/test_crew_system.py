"""
Unit tests for Crew models and services
"""
import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew_system.models import Crew, CrewMember, CrewRank, CrewStatus
from crew_system.services import CrewCreationService


class TestCrewModel(unittest.TestCase):
    """Test cases for Crew model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.leader = CrewMember(
            user_id="user1",
            username="TestLeader",
            rank=CrewRank.LEADER,
            joined_date=datetime.now()
        )
        
        self.crew = Crew(
            crew_id="crew1",
            crew_name="Test Crew",
            crew_tag="TEST",
            leader_id="user1",
            created_date=datetime.now(),
            members=[self.leader]
        )
    
    def test_add_member(self):
        """Test adding a member to crew"""
        new_member = CrewMember(
            user_id="user2",
            username="TestMember",
            rank=CrewRank.MUSCLE,
            joined_date=datetime.now()
        )
        
        result = self.crew.add_member(new_member)
        self.assertTrue(result)
        self.assertEqual(len(self.crew.members), 2)
    
    def test_add_duplicate_member(self):
        """Test adding a duplicate member"""
        duplicate = CrewMember(
            user_id="user1",
            username="Duplicate",
            rank=CrewRank.MUSCLE,
            joined_date=datetime.now()
        )
        
        result = self.crew.add_member(duplicate)
        self.assertFalse(result)
        self.assertEqual(len(self.crew.members), 1)
    
    def test_remove_member(self):
        """Test removing a member from crew"""
        new_member = CrewMember(
            user_id="user2",
            username="TestMember",
            rank=CrewRank.MUSCLE,
            joined_date=datetime.now()
        )
        self.crew.add_member(new_member)
        
        result = self.crew.remove_member("user2")
        self.assertTrue(result)
        self.assertEqual(len(self.crew.members), 1)
    
    def test_get_member(self):
        """Test retrieving a member"""
        member = self.crew.get_member("user1")
        self.assertIsNotNone(member)
        self.assertEqual(member.username, "TestLeader")
    
    def test_is_leader(self):
        """Test leader check"""
        self.assertTrue(self.crew.is_leader("user1"))
        self.assertFalse(self.crew.is_leader("user2"))
    
    def test_update_reputation(self):
        """Test reputation updates"""
        self.crew.update_reputation(100)
        self.assertEqual(self.crew.total_reputation, 100)
        
        self.crew.update_reputation(-50)
        self.assertEqual(self.crew.total_reputation, 50)
    
    def test_validate_valid_crew(self):
        """Test validation of a valid crew"""
        errors = self.crew.validate()
        self.assertEqual(len(errors), 0)
    
    def test_validate_short_name(self):
        """Test validation with short name"""
        self.crew.crew_name = "AB"
        errors = self.crew.validate()
        self.assertGreater(len(errors), 0)
    
    def test_validate_invalid_tag(self):
        """Test validation with invalid tag"""
        self.crew.crew_tag = "TOOLONG"
        errors = self.crew.validate()
        self.assertGreater(len(errors), 0)


class TestCrewMember(unittest.TestCase):
    """Test cases for CrewMember model"""
    
    def test_promote_member(self):
        """Test member promotion"""
        member = CrewMember(
            user_id="user1",
            username="TestUser",
            rank=CrewRank.MUSCLE,
            joined_date=datetime.now()
        )
        
        result = member.promote()
        self.assertTrue(result)
        self.assertEqual(member.rank, CrewRank.REPRESENTATIVE)
    
    def test_demote_member(self):
        """Test member demotion"""
        member = CrewMember(
            user_id="user1",
            username="TestUser",
            rank=CrewRank.LIEUTENANT,
            joined_date=datetime.now()
        )
        
        result = member.demote()
        self.assertTrue(result)
        self.assertEqual(member.rank, CrewRank.REPRESENTATIVE)
    
    def test_promote_leader(self):
        """Test that leader cannot be promoted further"""
        member = CrewMember(
            user_id="user1",
            username="TestLeader",
            rank=CrewRank.LEADER,
            joined_date=datetime.now()
        )
        
        result = member.promote()
        self.assertFalse(result)
        self.assertEqual(member.rank, CrewRank.LEADER)


class TestCrewCreationService(unittest.TestCase):
    """Test cases for CrewCreationService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = CrewCreationService(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_crew(self):
        """Test crew creation"""
        crew = self.service.create_crew(
            crew_name="Test Crew",
            crew_tag="TEST",
            leader_id="user1",
            leader_username="TestLeader"
        )
        
        self.assertIsNotNone(crew)
        self.assertEqual(crew.crew_name, "Test Crew")
        self.assertEqual(crew.crew_tag, "TEST")
        self.assertEqual(len(crew.members), 1)
    
    def test_create_duplicate_tag(self):
        """Test creating crew with duplicate tag"""
        self.service.create_crew(
            crew_name="First Crew",
            crew_tag="TEST",
            leader_id="user1",
            leader_username="Leader1"
        )
        
        with self.assertRaises(ValueError):
            self.service.create_crew(
                crew_name="Second Crew",
                crew_tag="TEST",
                leader_id="user2",
                leader_username="Leader2"
            )
    
    def test_get_crew_by_tag(self):
        """Test retrieving crew by tag"""
        created = self.service.create_crew(
            crew_name="Test Crew",
            crew_tag="TEST",
            leader_id="user1",
            leader_username="TestLeader"
        )
        
        crew = self.service.get_crew_by_tag("TEST")
        self.assertIsNotNone(crew)
        self.assertEqual(crew.crew_id, created.crew_id)
    
    def test_add_member_to_crew(self):
        """Test adding member to crew"""
        crew = self.service.create_crew(
            crew_name="Test Crew",
            crew_tag="TEST",
            leader_id="user1",
            leader_username="TestLeader"
        )
        
        result = self.service.add_member_to_crew(
            crew_id=crew.crew_id,
            user_id="user2",
            username="NewMember"
        )
        
        self.assertTrue(result)
        updated_crew = self.service.get_crew(crew.crew_id)
        self.assertEqual(len(updated_crew.members), 2)
    
    def test_list_crews(self):
        """Test listing crews"""
        self.service.create_crew(
            crew_name="Crew 1",
            crew_tag="CRW1",
            leader_id="user1",
            leader_username="Leader1"
        )
        
        self.service.create_crew(
            crew_name="Crew 2",
            crew_tag="CRW2",
            leader_id="user2",
            leader_username="Leader2"
        )
        
        crews = self.service.list_crews()
        self.assertEqual(len(crews), 2)


if __name__ == '__main__':
    unittest.main()
