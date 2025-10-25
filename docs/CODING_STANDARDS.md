# Coding Standards

> Source: https://skmnktl.github.io/blog/code_quality/

Code should be **performant**, easy to **change**, easy to **read**, and easy to **test**.

## PERFORMANT

- **Deep modules over shallow modules** (Ousterhout): Modules should provide deep functionality behind simple interfaces; the user should specify "what" and not have to worry about the "how"
- **Minimize abstraction layers** (Ousterhout): Each layer adds overhead; only create abstractions that provide significant value
- **Avoid premature decomposition** (Ousterhout): Don't split code into tiny pieces until performance demands it
- **Information hiding reduces coupling** (Ousterhout): Well-hidden implementation details allow for performance optimizations without breaking clients; if the user only asks for what they want, you can change the how without them having to change their behavior in turn

## CHANGEABLE

- **Design for change, not current requirements** (Ousterhout): Build systems that can evolve without major rewrites
- **Keep related code together** (Ousterhout): Changes often affect related functionality; co-locate it to minimize change scope
- **Eliminate duplication** (Beck): Change logic in one place rather than hunting down copies
- **Use dependency injection and avoid global state** (Hevery): Ask for what you need rather than creating or looking for it; avoid static methods, singletons, and global state that create hidden dependencies
- **Separate object construction from use** (Hevery): Decouple how objects are created from how they're used
- **Favor composition over inheritance** (Hevery): Composition is more flexible when requirements shift

## READABLE

- **Choose precise, meaningful names** (Ousterhout/Beck): Names should eliminate the need for additional explanation
- **Comments should explain why, not what** (Ousterhout): Code should be self-documenting for mechanics; comments explain reasoning
- **Maintain consistent style and patterns** (Ousterhout): Consistency reduces cognitive load when reading code
- **Write small, focused units** (Beck): Small classes, methods, and functions are easier to understand and modify
- **Express intent clearly** (Beck): Code should read like well-written prose describing the solution
- **Avoid deep nesting** (Beck): Flat code is easier to follow than deeply nested logic
- **Extract explaining variables** (Beck): Break complex expressions into named intermediate steps

## TESTABLE

- **Constructor should not do work** (Hevery): Constructors that perform operations are difficult to test
- **Test behaviors, not implementation** (Hevery): Tests should verify what the code does, not how it does it
- **Make tests independent with one assertion each** (Beck): Each test should run successfully regardless of other tests and document expected behavior clearly
- **Test first forces good design** (Beck): Writing tests first reveals design problems early
- **Tests should be proximate to what they're testing**

## MISCELLANEOUS

- **Exception handling is part of normal flow** (Ousterhout): Design error handling as carefully as happy path code, and define errors out of existence
- **Better to be wrong than vague** (Ousterhout): Specific but incorrect statements can be corrected; vague ones can't
- **Red-Green-Refactor cycle** (Beck): Make it fail, make it work, make it clean
- **Code should tell a story** (Beck): The progression through code should have a logical narrative flow

---

## Application to This Project

### For OCR Scripts
- Create **deep modules**: User specifies page range and desired quality, system handles all OCR details
- **Information hiding**: OCR engine choice, image preprocessing, API calls all hidden behind clean interface
- **Comments explain why**: Why we use multiple OCR engines, why we merge results in a specific way
- **Dependency injection**: Pass in OCR engines and mergers rather than hardcoding them

### For Multi-Pass OCR Architecture
```python
# Good: Deep module with simple interface
ocr = MultiPassOCR(engines=[GoogleVision(), ClaudeVision()])
result = ocr.extract_page(page_num=281)

# Bad: Shallow modules exposing too much
google_result = google_vision_api_call(convert_pdf_to_image(...))
claude_result = claude_vision_api_call(...)
merged = manual_merge_logic(google_result, claude_result)
```

### For Testing
- Each OCR engine is testable in isolation
- Mock external APIs (Google, Claude) for unit tests
- Integration tests verify end-to-end with real APIs on sample pages
- Tests are independent and can run in any order
