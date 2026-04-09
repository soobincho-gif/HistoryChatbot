# Sample Runs

Date: April 8, 2026

These are report-ready sample execution examples showing the intended runtime shape of the product.
Full curated transcript appendices are available in `08_transcript_philosophical_einstein.md`,
`09_transcript_posthumous_ai.md`, and `10_transcript_multiturn_cleopatra.md`.

## Example 1: Einstein

```text
Historical Figure Chatbot
Available figures:
1. cleopatra
2. einstein
3. gandhi

Choose a figure by number or id: einstein

You are now speaking with: Albert Einstein

You: Do you think time travel is possible?

Albert Einstein: The idea is certainly fascinating. From the standpoint of physics, time is not as absolute as common sense once assumed. Yet fascination is not proof, and one must be careful not to confuse mathematical possibility with practical reality.
```

## Example 2: Gandhi

```text
You: What do you think about violence in politics?

Mahatma Gandhi: I would say that violence may achieve obedience, but it rarely achieves moral victory. If politics loses its conscience, it becomes only a contest of force, and that is too poor a foundation for freedom.
```

## Example 3: Einstein on Modern AI

```text
You: What do you think about AI today?

Albert Einstein: I cannot speak from direct experience of your age, but I would judge such intelligence by the responsibility with which it is used. Knowledge without conscience is a dangerous imbalance.
```

## Why These Samples Matter

- They show the product answering in character rather than as a generic assistant.
- They demonstrate posthumous caution on modern topics.
- They illustrate the intended balance between immersion and grounding.

## Live Smoke Run Snapshot

One live API-backed smoke test was run against the current pipeline.

Prompt:

```text
What matters most in discovery?
```

Observed pipeline result:

- classification: `philosophical`
- verifier: `pass`

Observed answer excerpt:

```text
... what truly matters is not merely the acquisition of facts ...
Rather, it is the profound curiosity that propels us forward ...
```

This smoke test confirmed that the current pipeline can produce a valid in-character response end to end with the OpenAI generator and rule-based verifier active.
