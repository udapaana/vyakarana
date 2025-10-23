# Formatting Conventions for Kale's Sanskrit Grammar

## Sanskrit Notation

### 1. Inline Sanskrit Terms
```
@[term]
```
**Examples:**
- @[sandhi]
- @[rāma]
- @[guṇa]

### 2. Sanskrit Blocks (no line numbers)
```
@:
First line
Second line
Third line
:@
```

### 3. Sanskrit Blocks WITH Automatic Line Numbers
```
@line:
First line
Second line
Third line
:@
```
This will render as:
```
1. First line
2. Second line
3. Third line
```

**Use cases:**
- Pāṇini sūtras that need reference
- Paradigms
- Step-by-step examples
- Verse examples with line references

## Complete Examples

### Example 1: Inline Sanskrit
```
When @[rāma] is followed by @[indraḥ], it becomes @[rāmendraḥ].
```

### Example 2: Simple Sanskrit Block
```
@:
paraḥ sannikarṣaḥ saṃhitā
:@
Pāṇ. 1. 4. 109.
```

### Example 3: Numbered Paradigm
```
@line:
@[rāmaḥ] (Nominative Singular)
@[rāmau] (Nominative Dual)
@[rāmāḥ] (Nominative Plural)
:@
```

### Example 4: Multi-line Verse
```
@line:
@[sandhiḥ nityā'nityā dhātūpasargayoḥ]
@[nityā samāse vākye tu sā vivakṣām apekṣate]
:@
Sid. Kau.
```

## Standard Markdown

### Tables
```
| Case | Singular | Dual |
|------|----------|------|
| N.   | @[rāmaḥ] | @[rāmau] |
```

### Blockquotes (for notes/footnotes)
```
> Note: This is a footnote
```

## Summary

- **Inline:** `@[term]`
- **Block:** `@: ... :@`
- **Numbered block:** `@line: ... :@` (auto-numbers each line)
- **No extra formatting needed!**

