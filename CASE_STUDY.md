# ConfigForge — Typed Configuration Migration

**Category:** Legacy Software Modernization — supporting configuration-migration tooling  
**Project type:** New independent software project for Ismail Habib  
**Stack:** C++17, Python standard library, HTML, CSS, JavaScript  
**Delivery:** Working local application, command-line engine, source code, verification fixtures, and tests

## The challenge

Existing applications commonly store settings as strings in INI files. When a newer system expects typed JSON, migration can introduce subtle errors: repeated settings can silently override values, a string can be mistaken for a boolean, and path escaping can change a Windows directory. A useful migration workflow must expose these decisions before export.

## What was built

ConfigForge turns INI settings into a flat JSON object through an explicit schema. The user opens a local file or pastes its contents, discovers sections and keys, chooses output names and types, reviews validation, and downloads a complete configuration file. The browser interface is backed by a real C++17 parser and converter through a Python standard-library adapter.

The parser rejects duplicate sections and keys, reports malformed settings, handles documented quoting and comment rules, and preserves literal single-quoted paths. Required settings and value types are validated before any export succeeds. The command-line tool protects originals and existing output files, and publishes complete exports atomically on filesystems supporting hard links.

## Verified outcomes

- The verification fixture produced eight JSON settings, including integer worker and port values, a decimal timeout, boolean options, and a preserved Windows path string.
- Sixteen behavioral tests passed against the real engine and local adapter. Checks include duplicate settings, malformed quoting, optional and missing values, invalid types, UTF-8, and prevention of input/output overwrite.
- C++ compilation completed using Apple Clang 17 on macOS 15.7.8. Python and browser-script syntax checks passed.

The Windows path assertion verifies string preservation on the macOS host; it does not prove Windows application compatibility. The settings shown are a labeled verification fixture, not a client system.

## Scope and limits

ConfigForge is a new independent migration utility. It does not claim to be a rewrite of an existing customer codebase. Its INI dialect and limits are explicitly documented: no interpolation, includes, multiline continuation, nested JSON generation, or implicit duplicate overrides. It does not deploy the exported settings or validate domain rules such as a network port range. Windows builds and runtime behavior remain unverified.

## Portfolio screenshot captions

1. **Configuration workspace:** local INI source and explicit section/key mappings, with integer and boolean conversion choices.
2. **Typed export:** a successful engine result with the complete JSON preview and downloadable output.
3. **Conflict detection:** a deliberate duplicate setting blocks export with a source-line diagnostic.
