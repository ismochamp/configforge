# ConfigForge — Verification Results

Verified on 2026-09-28 against the included source and compiled engine.

- **Result:** PASS — 16 behavioral tests
- **Host:** macOS-15.7.8-x86_64-i386-64bit-Mach-O
- **Architecture:** x86_64
- **Compiler:** Apple Clang 17.0.0; C++17 with `-O2 -Wall -Wextra -Wpedantic`; compilation completed without warnings.
- **Python:** 3.14.7; standard library only.
- **Interface checks:** Python module compilation and JavaScript syntax checks passed. Browser interaction and screenshot QA are recorded separately by the portfolio assembly process.
- **Windows status:** Not compiled or run on Windows. Windows build instructions are guidance only.

The tests invoke the real C++ executable with temporary source/output files. They also invoke the same Python adapter used by the dashboard. They verify preservation of originals and rejection of existing output destinations. Fixtures are deliberately constructed verification inputs, not customer data.

## Actual test output

```text
test_bom_crlf_unicode (__main__.MigrationTests.test_bom_crlf_unicode) ... ok
test_comments_quoted_hash_and_escapes (__main__.MigrationTests.test_comments_quoted_hash_and_escapes) ... ok
test_dashboard_adapter_runs_real_engine (__main__.MigrationTests.test_dashboard_adapter_runs_real_engine) ... ok
test_dashboard_rejects_bad_required_type (__main__.MigrationTests.test_dashboard_rejects_bad_required_type) ... ok
test_duplicate_json_target (__main__.MigrationTests.test_duplicate_json_target) ... ok
test_duplicate_key_is_an_error (__main__.MigrationTests.test_duplicate_key_is_an_error) ... ok
test_duplicate_section_is_an_error (__main__.MigrationTests.test_duplicate_section_is_an_error) ... ok
test_existing_output_is_not_replaced (__main__.MigrationTests.test_existing_output_is_not_replaced) ... ok
test_input_cannot_be_output (__main__.MigrationTests.test_input_cannot_be_output) ... ok
test_invalid_types_block_entire_export (__main__.MigrationTests.test_invalid_types_block_entire_export) ... ok
test_invalid_utf8 (__main__.MigrationTests.test_invalid_utf8) ... ok
test_malformed_section_and_missing_equals (__main__.MigrationTests.test_malformed_section_and_missing_equals) ... ok
test_optional_empty_and_omitted_settings (__main__.MigrationTests.test_optional_empty_and_omitted_settings) ... ok
test_quoted_value_errors_block_export (__main__.MigrationTests.test_quoted_value_errors_block_export) ... ok
test_required_missing_source (__main__.MigrationTests.test_required_missing_source) ... ok
test_typed_fixture_preserves_windows_path (__main__.MigrationTests.test_typed_fixture_preserves_windows_path) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.504s

OK
```
