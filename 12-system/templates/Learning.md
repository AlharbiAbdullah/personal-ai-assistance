---
type: learning
created: <% tp.file.creation_date("YYYY-MM-DD HH:mm") %>
category: <% await tp.system.suggester(["tool", "framework", "concept", "book", "course", "language"], ["tool", "framework", "concept", "book", "course", "language"]) %>
status: <% await tp.system.suggester(["queued", "in-progress", "completed", "paused"], ["queued", "in-progress", "completed", "paused"]) %>
priority: <% await tp.system.suggester(["high", "medium", "low"], ["high", "medium", "low"]) %>
---

**Tags:** [[learning]] [[<% tp.frontmatter.category %>]]

---

# <% tp.file.title %>

<!--
DESTINATION: 06_learning/
When completed, extract key insights to 03_knowledge/ as atomic notes
-->

## What Is It?
<% tp.file.cursor() %>

## Why Learn This?


## Learning Goals
- [ ]

## Resources
-

## Progress Log

### <% tp.date.now("YYYY-MM-DD") %>
- Started:

## Key Takeaways
<!-- Move these to 03_knowledge/ as atomic notes when done -->

