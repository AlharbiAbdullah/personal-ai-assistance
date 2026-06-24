---
name: teach
description: Run a live, interactive review-based lesson. Concept + worked code, then drills (predict / spot-bug / explain-back / decide) answered before the reveal. Writes the lesson doc as a record afterward.
allowed-tools: Read, Write, AskUserQuestion, Bash, WebSearch, WebFetch
---

# Teach

A lesson is a **live session**, not a document John reads. He learns by *reviewing* code, not writing it: predicting output, spotting planted bugs, explaining mechanisms back, deciding tradeoffs. The doc is written *after* the session as a record, and feeds `/learning quiz` later.

Why this shape: read-through curricula decayed to ~0 for him (33 lessons read in 6 days, "back at zero" 3.5 months later). The fix is active engagement: retrieval, generation, feedback, spacing. In the modality that matches his real job, directing and reviewing AI-written code. See [[john-learns-by-building]].

## The session, step by step

### Step 1: Identify topic, method, depth

Read `~/helm/06-learning/{topic}/progress.md`:
- `method` — `review` (this flow) or `build` (legacy; only if a topic explicitly opts in).
- `mode` — the depth dial (see below). NOT a separate lesson shape.
- `floor` — whether this topic includes hands-on floor reps.
- Next lesson number, what's covered (lesson table), and the weak-areas log.

### Step 2: Pick the subtopic

Propose the next subtopic from the curriculum overview, or take John's. Specific, not generic.

### Step 3: Run the live session

Deliver these in order, in the conversation (not as a file he reads):

1. **Concept.** Plain-English idea. Define every term on first use. One analogy max. Short.
2. **Worked code.** The full, correct implementation. This is the "show me everything." Annotate what each part does.
3. **Drills — the active core. This IS the lesson.** Pose each drill, WAIT for John's answer, THEN reveal and grade. Never reveal before he answers. 4 to 8 drills, mixed:
   - **Predict the output.** Show code. "What does this print / return?" He answers, then reveal and explain why.
   - **Spot the bug.** Show code with 1 to 3 planted defects (bad SQL, wrong YAML, off-by-one, wrong async, injection, mutable default). "What's wrong?" He answers, then reveal each.
   - **Explain it back.** "In your words: why does this work / when use X over Y?" He answers, then grade and fill gaps.
   - **Decide.** "You need Z. List or dict? Index or scan? Sync or async?" He picks and justifies, then reveal the tradeoff.

   Grade honestly: correct (one line, move on), partial (name what's missing), wrong (right answer + mechanism, no "good try").
4. **Floor rep (only if `floor: yes` AND it's a true foundation).** One "type this yourself" rep. The stuff that needs muscle memory, not boilerplate. Sparingly. Skip it for most lessons.

### Step 4: Write the lesson doc as a record

AFTER the session, write the doc. It is a RECORD of what happened, not a textbook to re-read.

File: `~/helm/06-learning/{topic}/Lesson {NNN} - {Subtopic}.md`

```yaml
---
type: learning
topic: {topic-slug}
lesson: {NNN}
method: review
mode: {beginner | mid | expert}
status: done
date: {YYYY-MM-DD}
---
```

Body:
1. **Concept** — the idea, as covered.
2. **Worked code** — the implementation shown.
3. **Drills** — for each: the code, the planted bug or expected output, John's answer, the reveal.
4. **Weak spots** — what he missed or got partial. This is what `/quiz` re-tests.

### Step 5: Update progress.md

- Mark the lesson ✅ done (🔄 if cut short), date it.
- Move "Current" to the next lesson.
- Append any weak spots to the weak-areas log.

## The depth dial (mode)

One lesson shape (concept → code → drills). `mode` only changes how much to assume:
- **beginner** — define all jargon, slower concept, more predict-output drills, simpler bugs.
- **mid** — assume the basics. Drills lean spot-the-bug + decide-tradeoff. Short concept. Add a "when would you NOT do this" angle.
- **expert** — minimal concept (he knows the field). Drills are subtle bugs, edge cases, design tradeoffs. Cite real failure modes. Short.

If the dial feels wrong mid-session (he's lost, or bored), switch it and note it in the lesson frontmatter.

## Writing rules (for the recorded doc)

1. **Mobile-first diagrams.** Max 30 chars wide. Vertical layouts. `↓` arrows, not horizontal chains.
2. **No em dashes.** Use periods, commas, or colons.
3. **No AI-typical words.** Leverage, utilize, streamline, robust, comprehensive, seamless, holistic, cutting-edge, facilitate, empower, enhance, furthermore, moreover, additionally, delve, dive into, ensure, enable, vast, foster.
4. **Short is better.** A 6-sentence paragraph is probably two paragraphs.
5. **Every number concrete.**
6. **From, not about.** Any sentence that could describe a hundred different things says nothing. Delete it.

## Anti-Patterns

1. **Revealing a drill answer before John attempts it.** This kills the method. Always wait for his answer.
2. **Read-through walls.** Long prose the lesson expects him to absorb passively. The doc is a record, not a textbook. The learning happened live.
3. **Empty praise** ("great try!"). Grade honestly.
4. **Boilerplate floor reps** (`for _ in range(15)`). The floor is for foundations, not typing practice.
5. **Drills with no single defensible answer.** Every drill must have a gradeable answer.
6. Meta-sections explaining why the lesson exists.

## Rules

- The drills ARE the lesson. Concept + code only set them up. Without the drills it is just reading, which is the thing that failed.
- Never reveal before he answers.
- Write the doc as a record AFTER, never a textbook he reads BEFORE.
- If John breezes through, harden the bugs and raise the dial. If he's stuck, lower it.
