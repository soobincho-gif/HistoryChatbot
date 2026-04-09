# Historical Salon DESIGN.md

Inspired by the warm editorial systems in VoltAgent's [awesome-design-md](https://github.com/VoltAgent/awesome-design-md), especially the Claude design language, this project uses a parchment-toned historical salon aesthetic for grounded character conversations.

## 1. Visual Theme & Atmosphere

The interface should feel like a modern archive reading room rather than a generic AI dashboard. The mood is warm, thoughtful, and quietly scholarly. It should suggest annotated books, museum cards, and polished conversation rather than neon futurism.

Key characteristics:
- parchment and ivory surfaces instead of pure white or dark-mode default glass,
- serif-led headlines that feel editorial and literary,
- warm terracotta as the singular action color,
- soft olive and antique gold as supporting accents,
- translucent cards and ring-like borders rather than harsh panels,
- a sense of calm depth, not loud motion or flashy gradients.

## 2. Color Palette & Roles

Primary:
- Archive Ink: `#1e1914` for primary text
- Parchment: `#f5f1e8` for the page background
- Ivory Veil: `#fbf8f1` for elevated surfaces
- Terracotta Signal: `#b85b37` for CTA buttons and high-signal highlights

Secondary:
- Terracotta Deep: `#8f4328` for stronger emphasis
- Olive Note: `#6f7565` for metadata, captions, and quiet accents
- Antique Gold: `#c9a55b` for subtle highlight moments
- Warm Line: `rgba(39, 28, 21, 0.12)` for borders and dividers

## 3. Typography Rules

Font families:
- Headings: `"Cormorant Garamond", serif`
- Body and UI: `"Manrope", sans-serif`
- Utility labels and technical metadata: `"IBM Plex Mono", monospace`

Hierarchy:
- Hero display: large serif, tight leading, highly expressive
- Section headings: medium-large serif with book-title cadence
- Body text: modern sans, 16px-18px equivalent, comfortable leading
- Labels: small mono uppercase with tracking

## 4. Component Stylings

Buttons:
- full pill buttons,
- terracotta gradient for primary actions,
- subtle ring border and warm shadow,
- no square corners.

Cards:
- ivory or translucent paper surfaces,
- 16px-30px radius,
- whisper-thin borders,
- soft, warm shadow rather than heavy elevation.

Chat messages:
- user messages use a gold-tinted surface,
- assistant messages use a terracotta-tinted surface,
- each message is framed like an annotated note card,
- role labels appear in tracked monospace.

Figure cards:
- headline uses serif,
- metadata remains muted and quiet,
- topic chips are subtle pills, never bright badges.

## 5. Layout Principles

- The top of the page should open with an editorial hero, not a utilitarian form.
- Main content should be split into a conversation area and a contextual rail on desktop.
- Session summary, dossier notes, and starter prompts should sit in the supporting rail.
- The page should breathe: generous spacing, no dense dashboard compression.

## 6. Depth & Elevation

- Use ring-like borders and soft shadows to create depth.
- Prefer translucent layered panels over opaque slabs.
- Use background atmosphere through gentle radial warmth, not strong gradients.

## 7. Do's and Don'ts

Do:
- keep the tone warm, bookish, and composed,
- let headlines feel literary,
- reserve terracotta for action and emphasis,
- keep surfaces soft and readable.

Don't:
- use default Streamlit styling without overrides,
- use cold blue-gray UI chrome,
- turn the interface into a neon AI control panel,
- overanimate or use parody historical motifs.

## 8. Responsive Behavior

- On mobile, collapse the right rail beneath the conversation.
- Maintain generous line height and touch-safe button sizing.
- Keep chat cards readable and avoid squeezing the serif hero too tightly.

## 9. Agent Prompt Guide

When extending the UI:
- build like a historical salon, not a SaaS admin page,
- prefer editorial composition and warm surfaces,
- keep components elegant and legible,
- ensure the interface visually reinforces grounded historical dialogue.
