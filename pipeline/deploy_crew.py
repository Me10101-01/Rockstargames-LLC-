#!/usr/bin/env python3
"""
Crew Deployment Script
Deploys crew configurations to production environment
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class CrewDeployer:
    """Handles crew deployment operations"""
    
    def __init__(self, source_dir: Path, target_dir: Path):
        """
        Initialize the crew deployer
        
        Args:
            source_dir: Source directory containing crew files
            target_dir: Target deployment directory
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.deployment_log: List[Dict] = []
    
    def deploy(self) -> bool:
        """
        Deploy all crews from source to target
        
        Returns:
            True if deployment successful
        """
        print(f"Starting deployment from {self.source_dir} to {self.target_dir}")
        
        # Create target directory if it doesn't exist
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup directory
        backup_dir = self.target_dir.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Backup existing files
        if self.target_dir.exists() and list(self.target_dir.glob("*.json")):
            print(f"Creating backup at {backup_dir}")
            shutil.copytree(self.target_dir, backup_dir)
        
        # Get all crew files to deploy
        crew_files = list(self.source_dir.glob("*.json"))
        if not crew_files:
            print("No crew files found to deploy")
            return False
        
        print(f"Found {len(crew_files)} crew files to deploy")
        
        # Deploy each file
        success_count = 0
        for crew_file in crew_files:
            if self._deploy_file(crew_file):
                success_count += 1
            else:
                print(f"Failed to deploy {crew_file.name}")
        
        # Save deployment log
        self._save_deployment_log()
        
        print(f"\nDeployment complete: {success_count}/{len(crew_files)} files deployed")
        
        return success_count == len(crew_files)
    
    def _deploy_file(self, crew_file: Path) -> bool:
        """Deploy a single crew file"""
        try:
            target_file = self.target_dir / crew_file.name
            
            # Read and validate crew data
            with open(crew_file, 'r') as f:
                crew_data = json.load(f)
            
            # Copy file to target
            shutil.copy2(crew_file, target_file)
            
            # Log deployment
            self.deployment_log.append({
                'file': crew_file.name,
                'crew_id': crew_data.get('crew_id'),
                'crew_name': crew_data.get('crew_name'),
                'deployed_at': datetime.now().isoformat(),
                'status': 'success'
            })
            
            print(f"  ✅ Deployed {crew_file.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error deploying {crew_file.name}: {e}")
            self.deployment_log.append({
                'file': crew_file.name,
                'deployed_at': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def _save_deployment_log(self):
        """Save deployment log to file"""
        log_file = self.target_dir / "deployment_log.json"
        
        # Load existing log if it exists
        existing_log = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    existing_log = json.load(f)
            except:
                pass
        
        # Append new entries
        existing_log.extend(self.deployment_log)
        
        # Save updated log
        with open(log_file, 'w') as f:
            json.dump(existing_log, f, indent=2)
        
        print(f"Deployment log saved to {log_file}")


def main():
    """Main deployment function"""
    if len(sys.argv) < 3:
        print("Usage: python deploy_crew.py <source_directory> <target_directory>")
        sys.exit(1)
    
    source_dir = Path(sys.argv[1])
    target_dir = Path(sys.argv[2])
    
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Error: Source directory {source_dir} does not exist")
        sys.exit(1)
    
    deployer = CrewDeployer(source_dir, target_dir)
    success = deployer.deploy()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
