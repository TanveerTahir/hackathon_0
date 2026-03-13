@echo off
REM Silver Tier End-to-End Test - Batch Version
cd /d "%~dp0"

echo ============================================================
echo SILVER TIER END-TO-END TEST
echo ============================================================
echo.

echo TEST 1: Vault Structure
echo ------------------------------------------------------------
if exist "ai_employee_vault\Dashboard.md" (echo   [OK] Dashboard.md) else (echo   [FAIL] Dashboard.md)
if exist "ai_employee_vault\Company_Handbook.md" (echo   [OK] Company_Handbook.md) else (echo   [FAIL] Company_Handbook.md)
if exist "ai_employee_vault\Business_Goals.md" (echo   [OK] Business_Goals.md) else (echo   [FAIL] Business_Goals.md)
if exist "ai_employee_vault\Needs_Action" (echo   [OK] Needs_Action/) else (echo   [FAIL] Needs_Action/)
if exist "ai_employee_vault\Pending_Approval" (echo   [OK] Pending_Approval/) else (echo   [FAIL] Pending_Approval/)
if exist "ai_employee_vault\Approved" (echo   [OK] Approved/) else (echo   [FAIL] Approved/)
echo.

echo TEST 2: Watchers (2+ Required)
echo ------------------------------------------------------------
if exist "src\watchers\gmail_watcher.py" (echo   [OK] gmail_watcher.py) else (echo   [FAIL] gmail_watcher.py)
if exist "src\watchers\filesystem_watcher.py" (echo   [OK] filesystem_watcher.py) else (echo   [FAIL] filesystem_watcher.py)
if exist ".qwen\skills\whatsapp-watcher" (echo   [OK] whatsapp-watcher/) else (echo   [FAIL] whatsapp-watcher/)
if exist ".qwen\skills\linkedin-poster" (echo   [OK] linkedin-poster/) else (echo   [FAIL] linkedin-poster/)
echo.

echo TEST 3: LinkedIn Auto-Post
echo ------------------------------------------------------------
if exist ".qwen\skills\linkedin-poster\scripts\linkedin_poster.py" (echo   [OK] linkedin_poster.py) else (echo   [FAIL] linkedin_poster.py)
if exist ".qwen\skills\linkedin-poster\SKILL.md" (echo   [OK] SKILL.md) else (echo   [FAIL] SKILL.md)
echo.

echo TEST 4: Plan Generator
echo ------------------------------------------------------------
if exist ".qwen\skills\plan-generator\SKILL.md" (echo   [OK] SKILL.md) else (echo   [FAIL] SKILL.md)
echo.

echo TEST 5: MCP Server
echo ------------------------------------------------------------
if exist ".qwen\skills\email-mcp\SKILL.md" (echo   [OK] email-mcp/) else (echo   [FAIL] email-mcp/)
echo.

echo TEST 6: HITL Approval
echo ------------------------------------------------------------
if exist ".qwen\skills\hitl-approval\SKILL.md" (echo   [OK] hitl-approval/) else (echo   [FAIL] hitl-approval/)
echo.

echo TEST 7: Scheduler
echo ------------------------------------------------------------
if exist ".qwen\skills\scheduler\SKILL.md" (echo   [OK] scheduler/) else (echo   [FAIL] scheduler/)
echo.

echo TEST 8: Agent Skills
echo ------------------------------------------------------------
dir /b .qwen\skills | findstr /v "^\." 
echo.

echo ============================================================
echo BONUS TEST: Create LinkedIn Draft Post
echo ============================================================
python .qwen\skills\linkedin-poster\scripts\linkedin_poster.py -d -c "Silver Tier Test - AI Employee is operational! #Hackathon #SilverTier"
echo.

echo ============================================================
echo TEST COMPLETE
echo ============================================================
pause
