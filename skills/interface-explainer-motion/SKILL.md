---
name: interface-explainer-motion
description: Plan and create speech-synchronized software demos and explanatory motion graphics using screen recordings, interface details, diagrams, and talking-head footage. Use for 界面演示动画、口播配界面、软件教程动画, or Jeff Su–inspired visual explanation. Excludes caption-only styling and generic visual effects with no explanatory role.
---

# Interface explainer motion

Turn each spoken idea into a visual state that makes it easier to understand: establish the object, direct attention, show an action or relationship, reveal its result, then move on. Use motion to explain, not to decorate every sentence. The creator reference is a source of expressive principles, not a fixed layout, color palette, effect recipe, or claim about the creator's tools.

## Scope and inputs

Identify the requested deliverable: analysis/storyboard, editable graphic, timeline edit, or finished video. Gather only inputs needed for that outcome: narration and verified transcript/timing, available screen recordings/screenshots and result states, presenter footage, output format, and any brand or style constraints. Inspect existing project/media first when present. If material is missing, use reasonable assumptions for planning; for production, clearly distinguish a proposed/illustrative interface from verified real operation and ask only for information that blocks the requested result. Do not imply a simulated click, feature, or result actually occurred. When a simulation could be mistaken for real operation or evidence, label it visibly in the video as an illustration or simulation.

Use existing word-level timing when available; generate or obtain a transcript when needed and check uncertain words/timing. Track source and timeline times separately. If there is no spoken audio yet, mark storyboard timing as provisional rather than pretending to have sync.

## From speech to visual action

1. Break the narration into meaningful beats, not one effect per sentence. For each beat determine: the single thing the audience needs to understand, the visual evidence or state change, the focus, and its corresponding spoken cue.
2. Choose the simplest form that makes the beat legible:

   | Meaning | Visual choice |
   | --- | --- |
   | Establish object or context | Show enough of the original interface to orient the viewer before cropping. |
   | Point to a control | Move attention with a crop/zoom, cursor, outline, or subdued surroundings; preserve the target and context. |
   | Show an operation | Keep the real action readable; use a click/shortcut/input cue when it clarifies an otherwise invisible step. |
   | Show consequence | Hold a verifiable result; highlight the changed area or compare before and after. |
   | Explain a relationship | Reveal only needed cards, nodes, and arrows in the order of the explanation; retain common elements across changes. |
   | Compare alternatives | Keep the shared structure stable; reveal meaningful differences in position, labels, or color. |

3. Choose the appropriate material: real screen recording for accurate operations; real screenshot plus separately recreated moving details where that improves clarity; or an explicitly illustrative UI/diagram for concepts. Match actual interface features and avoid fabricating results. Use the user's own palette and content where supplied.
4. Assign composition according to the beat: presenter plus interface can introduce or conclude; a full-frame screen detail or diagram gives complex information space; a small presenter inset can maintain presence if it does not obstruct. Do not force split-screen throughout. Keep a single clear focal point, legible phone-sized text, uncluttered context, and room for captions/platform controls.
5. Build a beat sheet appropriate to the task with speech cue/time, intended understanding, source/real-or-illustrative status, visible before/after state, layout, focal action, and expected result. Align reveals and actions to actual speech cues and allow enough time to read. Use durations and easing as adjustable starting choices, never as measured facts about the reference.

For examples and reusable visual patterns, read [visual grammar](references/visual-grammar.md).

## Execute the requested deliverable

For a storyboard, give enough detail to produce each beat. For an editable animation or finished video, carry the plan through using the available host's editing, screen, caption, motion-graphic and export tools; follow their applicable instructions. Discover and use an available product-specific workflow when the task concerns a supported product or simulator. Do not stop at a plan when the user requested production. Preserve original source files while editing and arranging copies or timeline occurrences within the requested scope. Keep presenter, interface, graphics and captions separately editable where the host permits. Parameterize reusable text, colors, media, layout, and cues when practical.

When authoring graphics, use the host's actual runtime contract. Drive motion by time in seconds, or derive seconds from the timeline frame rate; do not assume a fixed fps. Design the readable settled frame before animating it. A reusable skill guides decisions; it is not itself a renderer or a substitute for unavailable source footage.

## Verify

Inspect the composed output, not just isolated graphic assets: representative entry, readable hold, operation/result, exit, and the most crowded or zoomed frame. Where possible also review the sequence with sound. Check that the target remains visible, real and simulated content are represented honestly, cues match speech, text reads at final size, and the presenter/captions/platform controls do not cover the important content. Correct problems and recheck; say what could not be verified. For planning-only requests, check the storyboard against these same criteria without claiming a render was tested.
