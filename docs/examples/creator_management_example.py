#!/usr/bin/env python3
"""
Example: Managing creator profiles and permissions
Demonstrates the creator management workflow
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from creator_tools import (
    CreatorManagementService, CreatorRole, Permission
)


def main():
    print("=== Rockstar Creator Management Example ===\n")
    
    # Initialize the creator management service
    service = CreatorManagementService(storage_path="./data/creators")
    
    # Example 1: Create different types of creators
    print("1. Creating creator profiles...")
    
    admin = service.create_creator(
        username="admin_boss",
        email="admin@rockstar.com",
        role=CreatorRole.ADMIN
    )
    print(f"   ✅ Created admin: {admin.username}")
    
    creator1 = service.create_creator(
        username="crew_creator_1",
        email="creator1@example.com",
        role=CreatorRole.CREATOR
    )
    print(f"   ✅ Created creator: {creator1.username}")
    
    moderator = service.create_creator(
        username="mod_vigilant",
        email="mod@example.com",
        role=CreatorRole.MODERATOR
    )
    print(f"   ✅ Created moderator: {moderator.username}")
    
    # Example 2: Check permissions
    print(f"\n2. Checking permissions...")
    
    permissions_to_check = [
        Permission.CREATE_CREW,
        Permission.DELETE_CREW,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_PERMISSIONS
    ]
    
    for perm in permissions_to_check:
        admin_has = admin.has_permission(perm)
        creator_has = creator1.has_permission(perm)
        mod_has = moderator.has_permission(perm)
        
        print(f"\n   {perm.value}:")
        print(f"   - Admin: {'✅' if admin_has else '❌'}")
        print(f"   - Creator: {'✅' if creator_has else '❌'}")
        print(f"   - Moderator: {'✅' if mod_has else '❌'}")
    
    # Example 3: Add custom permissions
    print(f"\n3. Adding custom permission to creator...")
    creator1.add_custom_permission(Permission.DELETE_CREW)
    service.update_creator(creator1)
    print(f"   ✅ Added DELETE_CREW permission")
    print(f"   Can now delete crews: {creator1.has_permission(Permission.DELETE_CREW)}")
    
    # Example 4: List all permissions for a user
    print(f"\n4. Listing all permissions for admin...")
    all_perms = admin.get_all_permissions()
    print(f"   Total permissions: {len(all_perms)}")
    for perm in all_perms:
        print(f"   - {perm.value}")
    
    # Example 5: Authorize actions
    print(f"\n5. Authorizing actions...")
    
    can_create = service.authorize_action(
        creator1.creator_id,
        Permission.CREATE_CREW
    )
    print(f"   Creator can create crews: {'✅' if can_create else '❌'}")
    
    can_manage_perms = service.authorize_action(
        creator1.creator_id,
        Permission.MANAGE_PERMISSIONS
    )
    print(f"   Creator can manage permissions: {'✅' if can_manage_perms else '❌'}")
    
    # Example 6: List creators by role
    print(f"\n6. Listing creators by role...")
    
    for role in CreatorRole:
        creators = service.list_creators(role=role)
        print(f"   {role.value}: {len(creators)} creator(s)")
        for c in creators:
            print(f"     - {c.username}")
    
    # Example 7: Deactivate a creator
    print(f"\n7. Deactivating a creator...")
    success = service.deactivate_creator(moderator.creator_id)
    if success:
        print(f"   ✅ Deactivated {moderator.username}")
        
        # Verify inactive user has no permissions
        can_view = moderator.has_permission(Permission.VIEW_CREWS)
        print(f"   Inactive user can view crews: {'✅' if can_view else '❌'}")
    
    print("\n=== Example Complete ===")
    print(f"Creator data saved to: ./data/creators/")


if __name__ == '__main__':
    main()
