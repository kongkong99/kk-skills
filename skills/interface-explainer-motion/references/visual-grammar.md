# Visual grammar and patterns

These are adaptable patterns inferred from finished examples, not claims about their production software, keyframes, or exact settings.

## Three useful patterns

- **Operation and result:** begin with the complete interface; show the relevant input, cursor or shortcut; crop toward the target and outline it; reveal the actual resulting state; then return to context or continue. A dimmed surrounding region can help when it does not obscure needed context.
- **Conceptual ladder:** preserve a stable card or diagram while adding one node, relationship or capability at a time. Compare successive levels with consistent placement; introduce color or symbols only where they carry meaning.
- **Concrete-to-abstract:** show the real object or task, simplify it to a card/diagram to explain its role, then return to actual evidence. Distinguish an illustration from an actual interface where unclear; when the user explicitly omits an on-screen badge, explain its simulated nature on delivery.

## Example beat sheet

For the line “Select a project, enter the goal, and the system splits it into steps,” plan against the real audio:

| Cue | Understanding | Visual state and action | Evidence |
| --- | --- | --- | --- |
| Select a project | Which item to choose | Show project list; focus and outline the chosen item. | Recording or verified screenshot |
| Enter the goal | What to enter | Move to the input; reveal the actual example. | Recording or verified reconstruction |
| Splits into steps | What changed | Reveal the result and keep the goal visible; make each step readable. | Actual result, or an illustration identified as such |

Plan cues against word-level time when possible; if no audio exists, mark times as placeholders. Choose screen/presenter balance based on legibility rather than a fixed percentage. Avoid covering the target with subtitles, oversized cursors, or decorative effects.

## Visual direction and implementation

A useful starting direction inspired by the sampled references is a restrained dark canvas, high-contrast labels, a single warm accent, and small interface or diagram elements that build into a clear whole. Some examples instead use light real interfaces or colored backgrounds. Adapt to the footage and user brand; neither the dark palette nor a fixed presenter/screen split is mandatory. Frame the full interface before a close crop when orientation matters; return to the result or context after a detail.

- **Focus:** keyframe position and scale toward the real control; use a thin outline or a dimmed surroundings layer, then settle long enough to read. Keep the target visible throughout.
- **Input:** reveal actual typing or use an accurate layered reconstruction; add a cursor, click pulse, or shortcut label only when it clarifies the operation.
- **Result:** switch to the recorded or otherwise verified result; hold it, highlight what changed, and avoid suggesting a simulated event really happened.
- **Diagram:** create editable text/cards, connectors, and icons; bring them in at their spoken cue, keeping earlier elements stable so the relationship remains clear.
- **Composition:** use separately adjustable presenter, screen, overlays, and captions where the host allows. Ensure crop and captions do not obscure target controls or results.

For general work, an entry can take roughly 0.2–0.4 seconds and a focus move 0.3–0.6 seconds as optional first tests. This user's WorkBuddy shorts instead follow the faster [push/pull timing](jeff-person-openings.md#推拉速度与开头三秒); do not fall back to these general timings for that series. These are production starting values, not measurements of the creator’s project. Animate in seconds and preserve the same timing at different frame rates.

## Sparse star background for this user's series

Use a near-black canvas with sparse white dots that drift slowly or show subtle parallax, not a static wallpaper. Keep brightness steady and motion subordinate to the presenter, text and UI. Initialize positions, sizes and drift speeds once from a fixed random seed, then calculate positions from elapsed seconds; never re-randomize each frame, flash, or visibly jump when looping. A gentle starting drift is 1–4 output pixels per second at 1080-pixel width, adjusted to the shot. Background drift is atmosphere, not an event counted toward the two-second/first-ten-second pacing rules. Check the rendered motion over time, not just a still.

The lightweight [drifting-stars HTML example](../assets/drifting-stars.html) is validated in ChatCut’s HTML Motion Graphic runtime. It exposes speed, timeOffset, backgroundColor and dotColor; register those properties when importing. Drive it with timeSeconds and set each shot’s timeOffset to preserve drift continuity. Adapt or replace it when using another renderer.
