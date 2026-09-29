# ConfigForge — Typed Configuration Migration

**Category:** Legacy Software Modernization — supporting configuration-migration tooling  
**Status:** New independent working project; not a rewrite of a historical customer codebase.

## Description

ConfigForge migrates INI settings into typed JSON through an explicit schema. Users inspect source sections and keys, choose output names and types, review validation and download a complete configuration. A compiled C++17 engine rejects duplicate settings, reports malformed input and preserves documented quoting behavior, including literal path strings.

Required values and types are checked before export. The command-line tool protects source files and existing destinations. Sixteen behavioral tests cover parsing, conflicting settings, invalid types, missing values, UTF-8 and file preservation. The supplied fixture generates eight typed settings through the actual engine.

This independent project demonstrates configuration tooling for modernization work. Verification ran on macOS; Windows compilation and runtime remain unverified. The tool exports a documented INI subset to flat JSON; deployment and application-specific configuration rules remain outside its scope.

**Skills:** C++17, legacy configuration migration, INI parsing, JSON, schema mapping, validation, Python integration, debugging, automated testing.

**Screenshot captions:** See `screenshots/CAPTIONS.md`.
