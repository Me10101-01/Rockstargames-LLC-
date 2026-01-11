#!/usr/bin/env python3
"""
Crew Validation Script
Validates crew data for compliance with Rockstar Creator standards
"""
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


class CrewValidator:
    """Validates crew configurations"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_crew_file(self, crew_file: Path) -> bool:
        """
        Validate a single crew file
        
        Args:
            crew_file: Path to crew JSON file
            
        Returns:
            True if validation passes
        """
        try:
            with open(crew_file, 'r') as f:
                crew_data = json.load(f)
            
            return self.validate_crew_data(crew_data)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {crew_file}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading {crew_file}: {e}")
            return False
    
    def validate_crew_data(self, crew_data: Dict[str, Any]) -> bool:
        """
        Validate crew data structure
        
        Args:
            crew_data: Crew data dictionary
            
        Returns:
            True if validation passes
        """
        is_valid = True
        
        # Required fields
        required_fields = [
            'crew_id', 'crew_name', 'crew_tag', 'leader_id',
            'created_date', 'status', 'members'
        ]
        
        for field in required_fields:
            if field not in crew_data:
                self.errors.append(f"Missing required field: {field}")
                is_valid = False
        
        # Validate crew name
        if 'crew_name' in crew_data:
            if not crew_data['crew_name'] or len(crew_data['crew_name']) < 3:
                self.errors.append("Crew name must be at least 3 characters")
                is_valid = False
            if len(crew_data['crew_name']) > 50:
                self.errors.append("Crew name must not exceed 50 characters")
                is_valid = False
        
        # Validate crew tag
        if 'crew_tag' in crew_data:
            if len(crew_data['crew_tag']) != 4:
                self.errors.append("Crew tag must be exactly 4 characters")
                is_valid = False
            if not crew_data['crew_tag'].isalnum():
                self.errors.append("Crew tag must be alphanumeric")
                is_valid = False
        
        # Validate members
        if 'members' in crew_data:
            members = crew_data['members']
            if not isinstance(members, list):
                self.errors.append("Members must be a list")
                is_valid = False
            elif len(members) == 0:
                self.errors.append("Crew must have at least one member")
                is_valid = False
            else:
                # Validate leader is in members
                leader_id = crew_data.get('leader_id')
                leader_found = any(
                    m.get('user_id') == leader_id for m in members
                )
                if not leader_found:
                    self.errors.append("Leader must be a member of the crew")
                    is_valid = False
                
                # Validate only one leader
                leader_count = sum(
                    1 for m in members if m.get('rank') == 'leader'
                )
                if leader_count == 0:
                    self.errors.append("Crew must have exactly one leader")
                    is_valid = False
                elif leader_count > 1:
                    self.errors.append("Crew can only have one leader")
                    is_valid = False
                
                # Check for duplicate members
                user_ids = [m.get('user_id') for m in members]
                if len(user_ids) != len(set(user_ids)):
                    self.errors.append("Duplicate members found")
                    is_valid = False
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'suspended', 'disbanded']
        if 'status' in crew_data:
            if crew_data['status'] not in valid_statuses:
                self.errors.append(f"Invalid status: {crew_data['status']}")
                is_valid = False
        
        # Validate colors
        if 'color_primary' in crew_data:
            if not self._is_valid_hex_color(crew_data['color_primary']):
                self.warnings.append(
                    f"Invalid primary color format: {crew_data['color_primary']}"
                )
        
        if 'color_secondary' in crew_data:
            if not self._is_valid_hex_color(crew_data['color_secondary']):
                self.warnings.append(
                    f"Invalid secondary color format: {crew_data['color_secondary']}"
                )
        
        # Validate max members
        if 'max_members' in crew_data:
            max_members = crew_data['max_members']
            if not isinstance(max_members, int) or max_members < 1:
                self.errors.append("max_members must be a positive integer")
                is_valid = False
            if max_members > 10000:
                self.warnings.append("max_members exceeds recommended limit of 10000")
        
        return is_valid
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if string is a valid hex color"""
        if not isinstance(color, str):
            return False
        if not color.startswith('#'):
            return False
        if len(color) != 7:
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def print_report(self):
        """Print validation report"""
        if self.errors:
            print("\n❌ VALIDATION ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")


def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_crew.py <crew_file_or_directory>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    validator = CrewValidator()
    
    if path.is_file():
        # Validate single file
        success = validator.validate_crew_file(path)
        validator.print_report()
        sys.exit(0 if success else 1)
    
    elif path.is_dir():
        # Validate all JSON files in directory
        crew_files = list(path.glob("*.json"))
        if not crew_files:
            print(f"No JSON files found in {path}")
            sys.exit(1)
        
        print(f"Validating {len(crew_files)} crew files...\n")
        
        all_valid = True
        for crew_file in crew_files:
            print(f"Validating {crew_file.name}...")
            file_validator = CrewValidator()
            if not file_validator.validate_crew_file(crew_file):
                all_valid = False
                file_validator.print_report()
                print()
        
        if all_valid:
            print("✅ All crew files are valid!")
            sys.exit(0)
        else:
            print("❌ Some crew files have validation errors")
            sys.exit(1)
    
    else:
        print(f"Error: {path} is not a file or directory")
        sys.exit(1)


if __name__ == '__main__':
    main()
