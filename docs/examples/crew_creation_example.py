#!/usr/bin/env python3
"""
Example: Creating and managing crews
Demonstrates the basic crew creation workflow
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crew_system.services import CrewCreationService
from crew_system.models import CrewRank


def main():
    print("=== Rockstar Creator Crew Creation Example ===\n")
    
    # Initialize the crew creation service
    service = CrewCreationService(storage_path="./data/crews")
    
    # Example 1: Create a new crew
    print("1. Creating a new crew...")
    crew = service.create_crew(
        crew_name="Shadow Warriors",
        crew_tag="SHDW",
        leader_id="user_12345",
        leader_username="DarkCommander",
        motto="Silent but deadly",
        description="Elite tactical unit specializing in stealth operations",
        color_primary="#000000",
        color_secondary="#FF0000"
    )
    print(f"   ✅ Created crew: {crew.crew_name} [{crew.crew_tag}]")
    print(f"   ID: {crew.crew_id}\n")
    
    # Example 2: Add members to the crew
    print("2. Adding members to the crew...")
    members_to_add = [
        ("user_12346", "StealthyNinja", CrewRank.LIEUTENANT),
        ("user_12347", "SilentSniper", CrewRank.REPRESENTATIVE),
        ("user_12348", "QuickRecon", CrewRank.MUSCLE),
        ("user_12349", "TacticalExpert", CrewRank.MUSCLE),
    ]
    
    for user_id, username, rank in members_to_add:
        success = service.add_member_to_crew(
            crew_id=crew.crew_id,
            user_id=user_id,
            username=username,
            rank=rank
        )
        if success:
            print(f"   ✅ Added {username} as {rank.value}")
    
    # Example 3: Update crew reputation
    print(f"\n3. Updating crew reputation...")
    crew.update_reputation(1500)
    service.update_crew(crew)
    print(f"   ✅ Crew reputation: {crew.total_reputation}")
    
    # Example 4: Retrieve and display crew
    print(f"\n4. Retrieving crew by tag...")
    retrieved_crew = service.get_crew_by_tag("SHDW")
    if retrieved_crew:
        print(f"   ✅ Found: {retrieved_crew.crew_name}")
        print(f"   Members: {len(retrieved_crew.members)}")
        print(f"   Status: {retrieved_crew.status.value}")
    
    # Example 5: List all crews
    print(f"\n5. Listing all crews...")
    all_crews = service.list_crews()
    print(f"   Total crews: {len(all_crews)}")
    for c in all_crews:
        print(f"   - {c.crew_name} [{c.crew_tag}] ({len(c.members)} members)")
    
    # Example 6: Get crew members by rank
    print(f"\n6. Listing members by rank...")
    leaders = retrieved_crew.get_members_by_rank(CrewRank.LEADER)
    print(f"   Leaders: {[m.username for m in leaders]}")
    
    muscle = retrieved_crew.get_members_by_rank(CrewRank.MUSCLE)
    print(f"   Muscle: {[m.username for m in muscle]}")
    
    print("\n=== Example Complete ===")
    print(f"Crew data saved to: ./data/crews/{crew.crew_id}.json")


if __name__ == '__main__':
    main()
