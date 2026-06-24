## Purpose

Build new features by writing tests FIRST. Tests define behavior, then code is written to pass the tests.

## When to Use

- New features (code doesn't exist yet)
- Customer-facing behavior
- APIs, auth flows, user interactions
- Anywhere behavior/contract matters

## The TDD Cycle

```
RED → GREEN → REFACTOR → REPEAT

RED:    Write failing test
GREEN:  Write minimal code to pass
REFACTOR: Clean up, keep tests green
REPEAT: Next behavior
```

## Process

### 1. Understand the Feature

Ask the user:
```
What should this feature do?
Who uses it?
What are the inputs/outputs?
What errors can occur?
What are the boundaries/limits?
```

### 2. Break Into Behaviors

List discrete, testable behaviors:
```
Feature: User Query Execution

Behaviors:
1. User can run SELECT queries
2. User cannot run INSERT/UPDATE/DELETE
3. User can only query allowed schemas
4. Results limited to 1M rows
5. Rate limit: 10 queries/minute
```

### 3. Write First Failing Test

```python
# tests/test_query_execution.py

def test_user_can_run_select_query(self, query_service):
    """Users can execute SELECT queries."""
    result = query_service.execute("SELECT * FROM analytics.users LIMIT 10")

    assert result.success is True
```

**Ask user**: "Here's the first test. It will FAIL because the code doesn't exist. Approve? (yes/modify/skip)"

### 4. Write Minimal Code

Only enough to pass the test:

```python
# src/services/query_service.py

class QueryResult:
    def __init__(self, success: bool):
        self.success = success

class QueryService:
    def execute(self, sql: str) -> QueryResult:
        return QueryResult(success=True)
```

### 5. Run Test - Confirm GREEN

```bash
uv run pytest tests/test_query_execution.py -v
```

### 6. Next Test Forces Real Implementation

```python
def test_rejects_delete_statements(self, query_service):
    """Users cannot execute DELETE queries."""
    result = query_service.execute("DELETE FROM analytics.users")

    assert result.success is False
    assert "DELETE not allowed" in result.error
```

Now code must actually validate:

```python
def execute(self, sql: str) -> QueryResult:
    normalized = sql.strip().upper()

    if normalized.startswith("DELETE"):
        return QueryResult(success=False, error="DELETE not allowed")

    return QueryResult(success=True)
```

### 7. Refactor When Needed

After several tests pass, look for:
- Duplicate code → extract method
- Long methods → split
- Magic values → constants

**Rule**: Only refactor when tests are GREEN.

### 8. Repeat Until Feature Complete

Each behavior gets:
1. Failing test
2. Minimal code
3. Passing test
4. Optional refactor

## Output Format

During TDD session:

```
TDD SESSION: Query Execution
============================

Behavior 1: User can run SELECT
  [TEST] test_user_can_run_select_query
  [CODE] QueryService.execute() - basic return
  [PASS]

Behavior 2: Reject DELETE
  [TEST] test_rejects_delete_statements
  [CODE] Added DELETE validation
  [PASS]

Behavior 3: Reject INSERT
  [TEST] test_rejects_insert_statements
  [CODE] Added INSERT validation
  [PASS]
  [REFACTOR] Extracted _is_allowed_statement()

Progress: 3/5 behaviors complete
Next: "User can only query allowed schemas"
```

## Rules

1. NEVER write code before the test
2. NEVER write more code than needed to pass
3. ONE behavior at a time
4. Get user approval on each test
5. Run tests after every change
6. Refactor only when GREEN
7. Small steps - if stuck, write a smaller test
