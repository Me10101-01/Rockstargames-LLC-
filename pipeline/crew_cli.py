#!/usr/bin/env python3
"""
Crew System CLI Tool
Command-line interface for crew creation and management
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew_system.services import CrewCreationService
from crew_system.models import CrewRank, CrewStatus
from creator_tools import CreatorManagementService, CreatorRole


def cmd_create_crew(args):
    """Create a new crew"""
    service = CrewCreationService()
    
    try:
        crew = service.create_crew(
            crew_name=args.name,
            crew_tag=args.tag,
            leader_id=args.leader_id,
            leader_username=args.leader_username,
            motto=args.motto or "",
            description=args.description or ""
        )
        
        print(f"✅ Crew created successfully!")
        print(f"   ID: {crew.crew_id}")
        print(f"   Name: {crew.crew_name}")
        print(f"   Tag: {crew.crew_tag}")
        print(f"   Leader: {crew.leader_id}")
        
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_crews(args):
    """List all crews"""
    service = CrewCreationService()
    
    status_filter = None
    if args.status:
        status_filter = CrewStatus(args.status)
    
    crews = service.list_crews(status=status_filter)
    
    print(f"Found {len(crews)} crew(s):\n")
    
    for crew in crews:
        print(f"🎮 {crew.crew_name} [{crew.crew_tag}]")
        print(f"   ID: {crew.crew_id}")
        print(f"   Status: {crew.status.value}")
        print(f"   Members: {len(crew.members)}")
        print(f"   Reputation: {crew.total_reputation}")
        if crew.motto:
            print(f"   Motto: \"{crew.motto}\"")
        print()


def cmd_show_crew(args):
    """Show detailed crew information"""
    service = CrewCreationService()
    
    if args.tag:
        crew = service.get_crew_by_tag(args.tag)
    else:
        crew = service.get_crew(args.id)
    
    if not crew:
        print(f"❌ Crew not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"🎮 {crew.crew_name} [{crew.crew_tag}]")
    print(f"   ID: {crew.crew_id}")
    print(f"   Status: {crew.status.value}")
    print(f"   Created: {crew.created_date}")
    print(f"   Leader: {crew.leader_id}")
    print(f"   Members: {len(crew.members)}/{crew.max_members}")
    print(f"   Reputation: {crew.total_reputation}")
    
    if crew.motto:
        print(f"   Motto: \"{crew.motto}\"")
    if crew.description:
        print(f"   Description: {crew.description}")
    
    print(f"\n   Colors:")
    print(f"   Primary: {crew.color_primary}")
    print(f"   Secondary: {crew.color_secondary}")
    
    print(f"\n   Members:")
    for member in crew.members:
        print(f"   - {member.username} ({member.rank.value})")
        print(f"     Reputation: {member.reputation_points}")
        print(f"     Missions: {member.missions_completed}")


def cmd_add_member(args):
    """Add a member to a crew"""
    service = CrewCreationService()
    
    rank = CrewRank(args.rank) if args.rank else CrewRank.MUSCLE
    
    success = service.add_member_to_crew(
        crew_id=args.crew_id,
        user_id=args.user_id,
        username=args.username,
        rank=rank
    )
    
    if success:
        print(f"✅ Member '{args.username}' added successfully!")
    else:
        print(f"❌ Failed to add member", file=sys.stderr)
        sys.exit(1)


def cmd_create_creator(args):
    """Create a new creator profile"""
    service = CreatorManagementService()
    
    role = CreatorRole(args.role) if args.role else CreatorRole.CREATOR
    
    try:
        creator = service.create_creator(
            username=args.username,
            email=args.email,
            role=role
        )
        
        print(f"✅ Creator created successfully!")
        print(f"   ID: {creator.creator_id}")
        print(f"   Username: {creator.username}")
        print(f"   Email: {creator.email}")
        print(f"   Role: {creator.role.value}")
        
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_creators(args):
    """List all creators"""
    service = CreatorManagementService()
    
    role_filter = None
    if args.role:
        role_filter = CreatorRole(args.role)
    
    creators = service.list_creators(role=role_filter)
    
    print(f"Found {len(creators)} creator(s):\n")
    
    for creator in creators:
        status = "✓ Active" if creator.is_active else "✗ Inactive"
        print(f"👤 {creator.username} ({status})")
        print(f"   ID: {creator.creator_id}")
        print(f"   Email: {creator.email}")
        print(f"   Role: {creator.role.value}")
        print(f"   Crews Created: {len(creator.crews_created)}")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Rockstar Creator Crew Management CLI"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create crew command
    create_parser = subparsers.add_parser('create', help='Create a new crew')
    create_parser.add_argument('--name', required=True, help='Crew name')
    create_parser.add_argument('--tag', required=True, help='4-letter crew tag')
    create_parser.add_argument('--leader-id', required=True, help='Leader user ID')
    create_parser.add_argument('--leader-username', required=True, help='Leader username')
    create_parser.add_argument('--motto', help='Crew motto')
    create_parser.add_argument('--description', help='Crew description')
    create_parser.set_defaults(func=cmd_create_crew)
    
    # List crews command
    list_parser = subparsers.add_parser('list', help='List crews')
    list_parser.add_argument('--status', choices=['active', 'inactive', 'suspended', 'disbanded'])
    list_parser.set_defaults(func=cmd_list_crews)
    
    # Show crew command
    show_parser = subparsers.add_parser('show', help='Show crew details')
    show_group = show_parser.add_mutually_exclusive_group(required=True)
    show_group.add_argument('--id', help='Crew ID')
    show_group.add_argument('--tag', help='Crew tag')
    show_parser.set_defaults(func=cmd_show_crew)
    
    # Add member command
    add_parser = subparsers.add_parser('add-member', help='Add member to crew')
    add_parser.add_argument('--crew-id', required=True, help='Crew ID')
    add_parser.add_argument('--user-id', required=True, help='User ID')
    add_parser.add_argument('--username', required=True, help='Username')
    add_parser.add_argument('--rank', choices=['leader', 'commissioner', 'lieutenant', 'representative', 'muscle'])
    add_parser.set_defaults(func=cmd_add_member)
    
    # Create creator command
    creator_parser = subparsers.add_parser('create-creator', help='Create a creator profile')
    creator_parser.add_argument('--username', required=True, help='Username')
    creator_parser.add_argument('--email', required=True, help='Email address')
    creator_parser.add_argument('--role', choices=['admin', 'creator', 'moderator', 'viewer'])
    creator_parser.set_defaults(func=cmd_create_creator)
    
    # List creators command
    list_creators_parser = subparsers.add_parser('list-creators', help='List creators')
    list_creators_parser.add_argument('--role', choices=['admin', 'creator', 'moderator', 'viewer'])
    list_creators_parser.set_defaults(func=cmd_list_creators)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
