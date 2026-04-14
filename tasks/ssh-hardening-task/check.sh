#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCORE=0
MAX_SCORE=100
RESULTS=()
DETAILS=()

echo ""
echo "========================================="
echo "🔍 SSH Hardening Validation"
echo "========================================="
echo ""

# Проверка 1: Root login disabled
echo -n "1. Checking PermitRootLogin... "
if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config; then
    echo -e "${GREEN}✓ PASSED${NC}"
    SCORE=$((SCORE + 20))
    RESULTS+=("✅ PermitRootLogin is disabled")
    DETAILS+=("  ✓ Found: PermitRootLogin no")
else
    echo -e "${RED}✗ FAILED${NC}"
    RESULTS+=("❌ PermitRootLogin should be set to 'no'")
    DETAILS+=("  ✗ Current: $(grep '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null || echo 'not set')")
fi

# Проверка 2: Password authentication disabled
echo -n "2. Checking PasswordAuthentication... "
if grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config; then
    echo -e "${GREEN}✓ PASSED${NC}"
    SCORE=$((SCORE + 20))
    RESULTS+=("✅ Password authentication is disabled")
    DETAILS+=("  ✓ Found: PasswordAuthentication no")
else
    echo -e "${RED}✗ FAILED${NC}"
    RESULTS+=("❌ PasswordAuthentication should be set to 'no'")
    DETAILS+=("  ✗ Current: $(grep '^PasswordAuthentication' /etc/ssh/sshd_config 2>/dev/null || echo 'not set')")
fi

# Проверка 3: SSH port changed to 2222
echo -n "3. Checking SSH Port... "
if grep -q "^Port 2222" /etc/ssh/sshd_config; then
    echo -e "${GREEN}✓ PASSED${NC}"
    SCORE=$((SCORE + 20))
    RESULTS+=("✅ SSH port changed to 2222")
    DETAILS+=("  ✓ Found: Port 2222")
else
    echo -e "${RED}✗ FAILED${NC}"
    RESULTS+=("❌ SSH port should be changed to 2222")
    DETAILS+=("  ✗ Current: $(grep '^Port' /etc/ssh/sshd_config 2>/dev/null || echo 'not set')")
fi

# Проверка 4: AllowUsers configured
echo -n "4. Checking AllowUsers... "
if grep -q "^AllowUsers" /etc/ssh/sshd_config; then
    ALLOWED_USERS=$(grep "^AllowUsers" /etc/ssh/sshd_config | cut -d' ' -f2-)
    echo -e "${GREEN}✓ PASSED${NC}"
    SCORE=$((SCORE + 20))
    RESULTS+=("✅ AllowUsers is configured: $ALLOWED_USERS")
    DETAILS+=("  ✓ Found: AllowUsers $ALLOWED_USERS")
else
    echo -e "${RED}✗ FAILED${NC}"
    RESULTS+=("❌ AllowUsers should be configured (e.g., 'AllowUsers student')")
    DETAILS+=("  ✗ Not configured")
fi

# Проверка 5: MaxAuthTries limited to 3 or less
echo -n "5. Checking MaxAuthTries... "
if grep -q "^MaxAuthTries [0-9]" /etc/ssh/sshd_config; then
    MAX_TRIES=$(grep "^MaxAuthTries" /etc/ssh/sshd_config | awk '{print $2}')
    if [ "$MAX_TRIES" -le 3 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        SCORE=$((SCORE + 20))
        RESULTS+=("✅ MaxAuthTries is set to $MAX_TRIES (≤ 3)")
        DETAILS+=("  ✓ Found: MaxAuthTries $MAX_TRIES")
    else
        echo -e "${YELLOW}⚠ PARTIAL${NC}"
        SCORE=$((SCORE + 10))
        RESULTS+=("⚠️ MaxAuthTries is $MAX_TRIES, should be ≤ 3")
        DETAILS+=("  ⚠ Current: $MAX_TRIES, Expected: ≤ 3")
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    RESULTS+=("❌ MaxAuthTries should be configured")
    DETAILS+=("  ✗ Not configured")
fi

# Дополнительная проверка: SSH сервер работает на новом порту
echo ""
echo -n "6. Checking SSH service status... "
if ss -tlnp | grep -q ":2222"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    RESULTS+=("✅ SSH is listening on port 2222")
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    RESULTS+=("⚠️ SSH is NOT listening on port 2222 (restart may be needed)")
    DETAILS+=("  ⚠ Run: sudo systemctl restart ssh")
fi

# Вывод результатов
echo ""
echo "========================================="
echo "📊 VALIDATION RESULTS"
echo "========================================="
for result in "${RESULTS[@]}"; do
    echo "$result"
done

echo ""
echo "========================================="
echo "🔍 DETAILS"
echo "========================================="
for detail in "${DETAILS[@]}"; do
    echo "$detail"
done

echo ""
echo "========================================="
echo "🏆 SCORE"
echo "========================================="
PERCENTAGE=$((SCORE * 100 / MAX_SCORE))
echo "Score: $SCORE / $MAX_SCORE ($PERCENTAGE%)"

# Цветная оценка
if [ $PERCENTAGE -ge 90 ]; then
    echo -e "${GREEN}Excellent! Your SSH configuration is very secure!${NC}"
    EXIT_CODE=0
elif [ $PERCENTAGE -ge 70 ]; then
    echo -e "${YELLOW}Good, but there's room for improvement.${NC}"
    EXIT_CODE=1
else
    echo -e "${RED}Not yet secure. Please review the requirements.${NC}"
    EXIT_CODE=1
fi

echo ""
exit $EXIT_CODE
