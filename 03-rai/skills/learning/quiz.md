---
name: quiz
description: Retrieval practice on recent lessons. Tests understanding, flags weak retention
allowed-tools: Read, AskUserQuestion
---

# Quiz

Test recall and application of recent lessons. Honest feedback. No empty praise.

## Instructions

### Step 1: Identify scope

Ask John which topic. Then ask:
- **Last N lessons** (default: last 3 completed per progress.md), OR
- **Specific lesson numbers** (e.g., "004 and 007"), OR
- **Full topic** (every completed lesson).

### Step 2: Load lessons + weak areas

Read each in-scope lesson file from `~/helm/06-learning/{topic}/`. Also read the **weak-areas log** in `progress.md`: prioritize what John missed in past drills. This is the spacing that catches decay, the piece missing in Feb that let the old fundamentals evaporate.

### Step 3: Generate questions

Per lesson, generate 2-4 questions. For `review`-method topics, lean on the same modality as the live drills (this is a re-rep of the lesson, not a new format):
- **Predict the output** — show code, "what does this print / return?"
- **Spot the bug** — show code with a planted defect, "what's wrong?"
- **Explain it back** — "why does this work / when use X over Y?"

Plus the classics:
- **Recall** — a specific term, number, or name from the lesson.
- **Application** — a scenario where John must apply the concept.
- **Tradeoff** — for mid/expert depth: "When would you NOT apply this?"

Weight toward logged weak areas. Aim for 8-12 questions total per session. More is fatigue.

### Step 4: Ask one at a time

Use AskUserQuestion with free-form text for each (single-choice if the question is naturally multiple-choice).

### Step 5: Grade each answer

- **Correct** — say so, one sentence. Move on.
- **Partial** — name what's missing. Offer the correction.
- **Wrong** — honest. Give the right answer with its mechanism. No "good try."

### Step 6: Report at end

Summary:
- Score: `{correct}/{total}`.
- Weak areas (low recall): list them, and write them to the weak-areas log in `progress.md`.
- Suggestion: re-drill the weak concept (a short live `/learning teach` mini-session on it), OR move on.

If score < 60%, re-drill the weakest concepts before progressing. Do NOT suggest re-reading the lesson doc: re-reading is the weakest tool and is what decayed last time. The remedy for a missed drill is another drill.

## Rules

- Never ask "does this make sense?" — ask a real question.
- Never accept vague answers. Push for specifics.
- Record weak areas in progress.md's "Stuck on" line if the pattern persists.
