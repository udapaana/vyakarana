#!/bin/bash
# Verification script for Claude AI Wrapper

echo "=================================================="
echo "Claude AI Wrapper - Installation Verification"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
checks_passed=0
checks_total=0

# Check function
check() {
    ((checks_total++))
    if eval "$2"; then
        echo -e "${GREEN}✓${NC} $1"
        ((checks_passed++))
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        if [ ! -z "$3" ]; then
            echo -e "  ${YELLOW}→${NC} $3"
        fi
        return 1
    fi
}

# 1. Check Python
check "Python 3 installed" "command -v python3 > /dev/null" "Install Python 3.7+"

# 2. Check Python version
check "Python 3.7+" "python3 -c 'import sys; exit(0 if sys.version_info >= (3,7) else 1)'" "Upgrade Python"

# 3. Check modules exist
check "Module files exist" "[ -f scripts/ai/__init__.py ] && [ -f scripts/ai/client.py ]" "Run: ls scripts/ai/"

# 4. Check imports
check "Python imports working" "python3 -c 'from scripts.ai import ClaudeClient' 2>/dev/null" "Check PYTHONPATH"

# 5. Check API key
check "API key set" "[ ! -z \"\$ANTHROPIC_API_KEY\" ]" "Run: export ANTHROPIC_API_KEY='sk-ant-...'"

# 6. Check anthropic package
check "anthropic package installed" "python3 -c 'import anthropic' 2>/dev/null" "Run: pip install anthropic"

# 7. Check data directory
check "structured_pages/ exists" "[ -d structured_pages ]" "Run Phase 2 first"

# 8. Check data files
if [ -d "structured_pages" ]; then
    page_count=$(ls structured_pages/page_*.md 2>/dev/null | wc -l | tr -d ' ')
    check "Page files present ($page_count/729)" "[ $page_count -gt 0 ]" "Run Phase 2 OCR"
fi

# 9. Check CLI
check "CLI executable" "python3 -m scripts.ai --help >/dev/null 2>&1" "Check module installation"

# 10. Check documentation
check "Documentation exists" "[ -f scripts/ai/README.md ] && [ -f scripts/ai/QUICKSTART.md ]"

echo ""
echo "=================================================="
echo "Results: $checks_passed/$checks_total checks passed"
echo "=================================================="

if [ $checks_passed -eq $checks_total ]; then
    echo -e "${GREEN}✓ Installation verified! Ready to use.${NC}"
    echo ""
    echo "Next steps:"
    echo "  python3 -m scripts.ai extract-one 77 --output rules_test --start-page 50"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. See messages above.${NC}"
    echo ""
    echo "Installation guide: scripts/ai/INSTALLATION.md"
    exit 1
fi
