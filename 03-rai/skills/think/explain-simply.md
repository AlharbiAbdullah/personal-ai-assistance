# Explain Simply

Make complex ideas land. Use analogies, diagrams, and simple language.

## Structure

1. **One-sentence summary** - What is it in plain English?
2. **Analogy** - Compare to something familiar
3. **Diagram** - Visualize it
4. **Step-by-step** - Walk through how it works
5. **Check** - "Does this make sense?" or "Want me to go deeper?"

## Diagram Types

Pick the right diagram for the concept:

### Flow (for processes)
```
Input → Process → Output

Request → Validate → Save → Response
```

### Layers (for stacks/hierarchy)
```
┌─────────────────┐
│   Frontend      │
├─────────────────┤
│   API Layer     │
├─────────────────┤
│   Database      │
└─────────────────┘
```

### Relationship (for connections)
```
    ┌───────┐
    │ User  │
    └───┬───┘
        │ has many
        ▼
    ┌───────┐
    │ Posts │
    └───────┘
```

### Before/After (for transformations)
```
BEFORE          AFTER
───────         ─────
[1,2,3]   →    [2,4,6]
 raw           doubled
```

### Timeline (for sequences)
```
1. User clicks login
       ↓
2. Frontend sends credentials
       ↓
3. Backend validates
       ↓
4. Token returned
       ↓
5. User redirected
```

## Analogy Patterns

| Concept | Analogy |
|---------|---------|
| API | Waiter between you and the kitchen |
| Database index | Book index - jump to page instead of reading everything |
| Cache | Keeping milk on counter instead of fridge - faster but expires |
| Queue | Line at coffee shop - first in, first out |
| Stack | Plates - last on, first off |
| Recursion | Russian nesting dolls - same thing inside itself |
| Docker | Shipping container - same box works everywhere |
| Git branch | Parallel universe - experiment without affecting main timeline |

## Rules

1. **No jargon** - If you must use a technical term, define it immediately
2. **Concrete over abstract** - Use specific examples, not general descriptions
3. **Build up, one concept at a time** - Start with one concept (one thing at a time). Then build up by adding one more concept at a time, checking understanding as you go.
4. **Check understanding** - Pause and ask before going deeper

## Example

**User:** "How does async/await work?"

**Response:**

Async/await lets your code do other things while waiting, instead of just sitting there.

**Analogy:** It's like ordering food at a restaurant. You don't stand at the kitchen door waiting - you sit down, chat, check your phone. When the food's ready, the waiter brings it to you.

```
SYNC (blocking)           ASYNC (non-blocking)
─────────────────         ──────────────────────
Start request             Start request
   ↓                         ↓
Wait... wait...           Do other stuff
   ↓                         ↓
Wait... wait...           Do more stuff
   ↓                         ↓
Response arrives          Response arrives ← notified
   ↓                         ↓
Continue                  Continue
```

**How it works:**
1. `await` marks "I'm waiting for something"
2. While waiting, Python handles other tasks
3. When the result is ready, it picks up where it left off

Does this make sense, or want me to show a code example?

## Failure Mode

If the user is still confused after an analogy, the analogy doesn't fit. Try a different one — don't double down on the same analogy with more detail.
