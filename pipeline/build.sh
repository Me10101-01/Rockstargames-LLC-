#!/bin/bash
# Crew Creation Pipeline Build Script
# Builds and validates the entire crew creation system

set -e  # Exit on error

echo "========================================="
echo "Rockstar Creator Crew Creation Pipeline"
echo "Build & Validation Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found"

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p data/crews
mkdir -p data/creators
mkdir -p data/production/crews
mkdir -p logs

echo -e "${GREEN}✓${NC} Directories created"

# Validate crew system structure
echo ""
echo "Validating crew system structure..."
if [ -d "crew_system" ] && [ -d "creator_tools" ] && [ -d "pipeline" ]; then
    echo -e "${GREEN}✓${NC} All required modules present"
else
    echo -e "${RED}✗${NC} Missing required modules"
    exit 1
fi

# Check for required files
echo ""
echo "Checking required files..."
required_files=(
    "crew_system/models/crew.py"
    "crew_system/services/crew_creation.py"
    "creator_tools/creator_profile.py"
    "creator_tools/creator_management.py"
    "pipeline/validate_crew.py"
    "pipeline/deploy_crew.py"
)

all_files_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        all_files_present=false
    fi
done

if [ "$all_files_present" = false ]; then
    echo -e "${RED}Build failed: Missing required files${NC}"
    exit 1
fi

# Run Python syntax check on all Python files
echo ""
echo "Running syntax validation..."
find . -name "*.py" -not -path "./.*" -exec python3 -m py_compile {} \; 2>&1 | tee logs/syntax_check.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All Python files have valid syntax"
else
    echo -e "${RED}✗${NC} Syntax errors found. Check logs/syntax_check.log"
    exit 1
fi

# Validate existing crew files if any
echo ""
echo "Validating existing crew files..."
if [ -d "data/crews" ] && [ "$(ls -A data/crews/*.json 2>/dev/null)" ]; then
    python3 pipeline/validate_crew.py data/crews
    echo -e "${GREEN}✓${NC} Crew files validated"
else
    echo -e "${YELLOW}⚠${NC} No crew files to validate"
fi

# Create build info file
echo ""
echo "Creating build info..."
cat > build_info.json << EOF
{
  "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "1.0.0",
  "status": "success",
  "modules": {
    "crew_system": "enabled",
    "creator_tools": "enabled",
    "pipeline": "enabled"
  }
}
EOF

echo -e "${GREEN}✓${NC} Build info created"

echo ""
echo "========================================="
echo -e "${GREEN}BUILD SUCCESSFUL${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Run tests: ./pipeline/run_tests.sh"
echo "  2. Deploy crews: python3 pipeline/deploy_crew.py <source> <target>"
echo ""

exit 0
