"""
Unit tests for Creator tools
"""
import unittest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from creator_tools import (
    CreatorProfile, CreatorRole, Permission, CreatorManagementService
)


class TestCreatorProfile(unittest.TestCase):
    """Test cases for CreatorProfile"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.profile = CreatorProfile(
            creator_id="creator1",
            username="TestCreator",
            email="test@example.com",
            role=CreatorRole.CREATOR,
            created_date=datetime.now(),
            last_login=datetime.now()
        )
    
    def test_has_permission_role_based(self):
        """Test role-based permissions"""
        self.assertTrue(self.profile.has_permission(Permission.CREATE_CREW))
        self.assertTrue(self.profile.has_permission(Permission.VIEW_CREWS))
        self.assertFalse(self.profile.has_permission(Permission.DELETE_CREW))
    
    def test_has_permission_custom(self):
        """Test custom permissions"""
        self.profile.add_custom_permission(Permission.DELETE_CREW)
        self.assertTrue(self.profile.has_permission(Permission.DELETE_CREW))
    
    def test_inactive_user_no_permissions(self):
        """Test that inactive users have no permissions"""
        self.profile.is_active = False
        self.assertFalse(self.profile.has_permission(Permission.VIEW_CREWS))
    
    def test_admin_has_all_permissions(self):
        """Test that admin has all permissions"""
        admin = CreatorProfile(
            creator_id="admin1",
            username="Admin",
            email="admin@example.com",
            role=CreatorRole.ADMIN,
            created_date=datetime.now(),
            last_login=datetime.now()
        )
        
        self.assertTrue(admin.has_permission(Permission.CREATE_CREW))
        self.assertTrue(admin.has_permission(Permission.DELETE_CREW))
        self.assertTrue(admin.has_permission(Permission.MANAGE_PERMISSIONS))
    
    def test_get_all_permissions(self):
        """Test getting all permissions"""
        self.profile.add_custom_permission(Permission.DELETE_CREW)
        perms = self.profile.get_all_permissions()
        
        self.assertIn(Permission.CREATE_CREW, perms)
        self.assertIn(Permission.DELETE_CREW, perms)


class TestCreatorManagementService(unittest.TestCase):
    """Test cases for CreatorManagementService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = CreatorManagementService(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_creator(self):
        """Test creator creation"""
        profile = self.service.create_creator(
            username="TestCreator",
            email="test@example.com"
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.username, "TestCreator")
        self.assertEqual(profile.role, CreatorRole.CREATOR)
    
    def test_create_duplicate_username(self):
        """Test creating creator with duplicate username"""
        self.service.create_creator(
            username="TestCreator",
            email="test1@example.com"
        )
        
        with self.assertRaises(ValueError):
            self.service.create_creator(
                username="TestCreator",
                email="test2@example.com"
            )
    
    def test_get_creator_by_username(self):
        """Test retrieving creator by username"""
        created = self.service.create_creator(
            username="TestCreator",
            email="test@example.com"
        )
        
        profile = self.service.get_creator_by_username("TestCreator")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.creator_id, created.creator_id)
    
    def test_authorize_action(self):
        """Test action authorization"""
        profile = self.service.create_creator(
            username="TestCreator",
            email="test@example.com"
        )
        
        authorized = self.service.authorize_action(
            profile.creator_id,
            Permission.CREATE_CREW
        )
        self.assertTrue(authorized)
        
        not_authorized = self.service.authorize_action(
            profile.creator_id,
            Permission.DELETE_CREW
        )
        self.assertFalse(not_authorized)
    
    def test_deactivate_creator(self):
        """Test deactivating a creator"""
        profile = self.service.create_creator(
            username="TestCreator",
            email="test@example.com"
        )
        
        result = self.service.deactivate_creator(profile.creator_id)
        self.assertTrue(result)
        
        # Verify creator is inactive
        updated = self.service.get_creator(profile.creator_id)
        self.assertFalse(updated.is_active)
    
    def test_list_creators_by_role(self):
        """Test listing creators by role"""
        self.service.create_creator(
            username="Creator1",
            email="c1@example.com",
            role=CreatorRole.CREATOR
        )
        
        self.service.create_creator(
            username="Admin1",
            email="a1@example.com",
            role=CreatorRole.ADMIN
        )
        
        creators = self.service.list_creators(role=CreatorRole.CREATOR)
        self.assertEqual(len(creators), 1)
        
        admins = self.service.list_creators(role=CreatorRole.ADMIN)
        self.assertEqual(len(admins), 1)


if __name__ == '__main__':
    unittest.main()
