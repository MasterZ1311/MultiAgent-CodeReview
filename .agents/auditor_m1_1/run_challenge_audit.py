import sys
sys.path.insert(0, ".")
import asyncio
from tests.test_m1_security_challenge import (
    TestAuthenticationNegativeCases,
    TestBoundaryAndAdversarialTokens,
    TestCORSBehaviorAndSecurity,
    TestProductionSecurityValidation,
)
from cerberus.core.database import init_db

async def run_all_challenge_tests():
    await init_db()
    
    t1 = TestAuthenticationNegativeCases()
    await t1.test_missing_authorization_header()
    await t1.test_empty_authorization_header()
    for h in [' ', '   ', 'Bearer', 'Bearer ', 'Bearer   ', 'Token test', 'Basic dXNl', 'Bearer a b']:
        await t1.test_malformed_authorization_headers(h)
    for tok in ['cvai_', 'cvai_attacker', 'cvai_admin', 'cvai_root', 'cvai_dev_key_1234']:
        await t1.test_arbitrary_cvai_tokens_rejected(tok)
    await t1.test_inactive_api_key_rejected()
    await t1.test_expired_api_key_with_utc_timezone_rejected()
    await t1.test_expired_api_key_with_naive_datetime_rejected()
    await t1.test_valid_active_unexpired_key_accepted()
    await t1.test_bearer_case_insensitivity()
    print('Category 1 (Authentication Negative Cases): ALL PASSED')

    t2 = TestBoundaryAndAdversarialTokens()
    for sqli in ["' OR '1'='1", "cvai_' OR '1'='1' --", "'; DROP TABLE api_keys; --"]:
        await t2.test_sql_injection_in_token(sqli)
    for s in [1000, 10000, 50000]:
        await t2.test_extreme_length_tokens(s)
    for st in ['cvai_<script>alert(1)</script>', 'cvai_${7*7}', 'cvai_../../../../etc/passwd']:
        await t2.test_special_characters_and_script_payloads(st)
    await t2.test_unauthenticated_requests_do_not_pollute_rate_limiter()
    print('Category 2 (Boundary and Adversarial Tokens): ALL PASSED')

    t3 = TestCORSBehaviorAndSecurity()
    for o in ['http://localhost:3000', 'http://localhost:8000', 'http://127.0.0.1:8000', 'http://127.0.0.1:3000']:
        await t3.test_cors_whitelisted_origins_simple_request(o)
        await t3.test_cors_whitelisted_origins_preflight(o)
    for u in ['http://evil.com', 'https://google.com', 'http://attacker.org']:
        await t3.test_cors_non_whitelisted_origins_rejected(u)
    for m in ['http://localhost:3000.evil.com', 'http://localhost:3001', 'null']:
        await t3.test_cors_adversarial_origins_rejected(m)
    print('Category 3 (CORS Behavior & Stress Tests): ALL PASSED')

    t4 = TestProductionSecurityValidation()
    t4.test_production_rejects_insecure_defaults()
    t4.test_production_rejects_short_secrets()
    t4.test_production_accepts_strong_secret()
    t4.test_prod_alias_triggers_same_validation()
    print('Category 4 (Production Security Validation): ALL PASSED')

    print('\n[RESULT] ALL CHALLENGE AUDIT CHECKS PASSED EMPIRICALLY AGAINST CODEBASE!')

if __name__ == '__main__':
    asyncio.run(run_all_challenge_tests())
