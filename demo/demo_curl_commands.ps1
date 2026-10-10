# ==============================================================================
# cerberus</> Enterprise Multi-Agent Code Review — Live Demo PowerShell Scripts
# ==============================================================================

$BaseUrl = "http://localhost:8000"
$ApiKey = "cvai_dev_key_123"
$Headers = @{
    "Authorization" = "Bearer $ApiKey"
    "Content-Type" = "application/json"
}

Write-Host "`n=== 1. Health & Cluster Status Check ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$BaseUrl/api/v1/health" -Method Get | ConvertTo-Json -Depth 3

Write-Host "`n=== 2. Active Agent Ecosystem Inspection ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$BaseUrl/api/v1/agents" -Method Get -Headers $Headers | ConvertTo-Json -Depth 3

Write-Host "`n=== 3. Scenario 1: Critical Security Audit (SQL Injection + Secrets) ===" -ForegroundColor Yellow
$SecBody = @{
    code = "API_KEY = `"sk-live-98213847291038291029381`"`ndef get_user(uid):`n    return db.execute(f`"SELECT * FROM users WHERE id = {uid}`")"
    language = "python"
    agents = @("security", "compliance")
} | ConvertTo-Json
$SecResp = Invoke-RestMethod -Uri "$BaseUrl/api/v1/review" -Method Post -Headers $Headers -Body $SecBody
Write-Host "Review ID:" $SecResp.review_id "Score:" $SecResp.overall_score
$SecResp.critical_issues | Format-Table -Property severity, category, title, recommendation -AutoSize

Write-Host "`n=== 4. Scenario 2: Algorithmic & DB Bottlenecks (O(n²) + N+1) ===" -ForegroundColor Yellow
$PerfBody = @{
    code = "def process(items):`n    for i in items:`n        for j in items:`n            pass`n    for item in items:`n        cursor.execute(`"SELECT * FROM t WHERE id = `" + str(item))"
    language = "python"
    agents = @("performance")
} | ConvertTo-Json
$PerfResp = Invoke-RestMethod -Uri "$BaseUrl/api/v1/review" -Method Post -Headers $Headers -Body $PerfBody
Write-Host "Review ID:" $PerfResp.review_id "Score:" $PerfResp.overall_score
$PerfResp.warnings | Format-Table -Property severity, category, title -AutoSize

Write-Host "`n=== 5. Scenario 3: Healthcare HIPAA & Privacy Compliance ===" -ForegroundColor Yellow
$CompBody = @{
    code = "import logging`nlogger = logging.getLogger(`"audit`")`ndef export(ssn, name):`n    logger.info(f`"Record: {name}, SSN: {ssn}`")`n    return f`"http://api.health.org/sync?ssn={ssn}`""
    language = "python"
    agents = @("compliance")
} | ConvertTo-Json
$CompResp = Invoke-RestMethod -Uri "$BaseUrl/api/v1/review" -Method Post -Headers $Headers -Body $CompBody
Write-Host "Review ID:" $CompResp.review_id "Score:" $CompResp.overall_score
$CompResp.critical_issues + $CompResp.warnings | Format-Table -Property severity, title -AutoSize

Write-Host "`n=== 6. Scenario 4: Concurrent Batch Code Review ===" -ForegroundColor Green
$BatchBody = @{
    files = @(
        @{ filename = "auth.py"; code = "import os`ndef login(): pass"; language = "python" },
        @{ filename = "db.py"; code = "def query(): return db.execute(`"SELECT * FROM users`")"; language = "python" },
        @{ filename = "calc.py"; code = "def add(a, b): return a + b"; language = "python" }
    )
} | ConvertTo-Json
$BatchResp = Invoke-RestMethod -Uri "$BaseUrl/api/v1/review/batch" -Method Post -Headers $Headers -Body $BatchBody
Write-Host "Batch ID:" $BatchResp.batch_id "Total Files Reviewed:" $BatchResp.total_files
