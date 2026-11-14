# Jeff-style sound cues and prompt card

## Sound design for visual actions

Make a cue sheet from actual visual events and place sounds on separate editable tracks. Assign each event its sound role; do not cover the whole video with variations of the same click.

| Visual event | Sound and timing |
| --- | --- |
| Camera push/pull, zoom or lateral move | Align the audible whoosh/swish body to movement; retain its natural short release even when the camera has already settled. No low humming tail. |
| Image/result becomes clear or is revealed | Light pop/chime at the payoff; keep it distinct from the movement cue. |
| Visible pointer press or UI interaction | Crisp mouse click on the actual press/change. |
| This user's chat-record reveal/switch | Crisp mouse click, not a humming whoosh. This editorial cue may have no pointer and does not prove a real operation; it takes precedence over the generic result-reveal sound. |
| Visible prompt/text entry | Real keyboard recording, starting/stopping with entry and pauses; no synthetic tick or continuous filler loop. |

Use only cues justified by the action; a single moment does not need every sound layered together. Inspect or audition the source transient before trimming: a library clip may begin with near-silence. Align its audible body to the action and preserve a short release; never assume the first 0.2 seconds contains the whoosh. Verify the rendered mix, not just that a sound item exists. Chinese input or pasted text may not map one sound to every displayed character. Follow the visible action with a natural rhythm.

Use the bundled production audio below first. Resolve paths relative to this Skill directory and import the files into the current project; do not depend on old project asset IDs or a previous computer's cache. [The audio catalog](../assets/sfx/catalog.json) records source titles, hashes, technical properties and reusable source windows. These are the actual files used in this user's videos, not audio extracted from Jeff's videos; their presence does not establish a match to Jeff's recordings.

| Role | Bundled source | Starting edit |
| --- | --- | --- |
| Camera push/pull | [Simple Whoosh](../assets/sfx/simple-whoosh.mp3) | Source 0.30–1.07s at 1.1× gives 0.70s. Keep the body and release. |
| Lighter camera movement | [Airy Short Whoosh](../assets/sfx/airy-short-whoosh.mp3) | Source 0.30–0.70s at 1.0× gives 0.40s. |
| UI press or chat-record switch | [Mouse Click](../assets/sfx/mouse-click-library.mp3) | Source 0–0.167s is a short starting cue; align the audible click to the event. |
| Result reveal | [Tiny Bubble Pop](../assets/sfx/tiny-bubble-pop.mp3) | Full source is only 0.168s; at 30fps use up to 5 frames unless the host explicitly supports padding. |
| Visible typing | [Slow Dell Keyboard Typing](../assets/sfx/keyboard-slow-dell.mp3) | Natural recording; select a short active window, never run all 68.352s under the video. |

For typing, the user rejected the former synthetic tick: use the bundled real keyboard recording with natural variation in key tone and rhythm. Two dense short examples are source **18.14–18.606667s** and **22.54–23.006667s**, each about 0.467s. In the previous mix, +6.7/+7.4 dB on these quiet sources made the taps audible; these are source-specific starting values, not defaults for other recordings. Match the actual narration and check the mixed output. Start and stop with visible entry, and leave typing pauses silent. If the bundled source is unavailable or unsuitable, search the host library for `library:sound:keyboard-typing-loop` or `library:sound:slow-dell-keyboard-typing`, or use a suitable licensed/user recording; do not silently fall back to synthetic ticks. Only the five listed library files are bundled; other library sounds still require acquisition.

Legacy starter files [mouse-click](../assets/sfx/mouse-click.wav) and [zoom-whoosh](../assets/sfx/zoom-whoosh.wav) remain as original synthetic alternatives, not the preferred production recordings above. `python3 scripts/make_sfx.py` regenerates only these two WAVs, not the five bundled MP3s. Its 0.38-second whoosh is source material, not a camera-duration setting. Retain the usable body and release rather than truncating it when the faster camera settles. Balance ordinary body cues below narration; use the opening exception below. Apply short fades after the sound body, and keep headroom to prevent clipping. Do not mute the narration or add effects solely to create activity. The effects must be present in the final mix, not only described in a storyboard; review with audio and confirm synchronization.

## Whoosh duration and source window

For this user's series, use **0.35–0.60 seconds as the normal placed duration**, and flag a whoosh shorter than 0.35 seconds for review. This is an implementation guardrail, not a universal duration for every sound. A deliberately shorter complete sound can be used only after checking its attack, body and release; never call a weak 0.2-second lead-in a complete whoosh. Do not stretch a tiny fragment just to pass the duration check. Keep a naturally longer useful sound when needed, or choose another short source if it masks narration.

Before placing each new source, identify its audible onset, strongest useful body and release by audition and waveform/level inspection. Record source ID/file, source in/out, peak/body time, placed duration, playback rate and gain. The selected source window must include the body; its effective timeline duration is `(source_out - source_in) / playback_rate`. Convert the minimum to frames using ceiling (at 30fps, 0.35s needs at least 11 frames), not a fixed frame count at every fps.

Align the audible onset or main transient with the visual accent, rather than aligning the file's silent beginning. Keep a brief natural release after the move if needed; fades must not erase the main body. Verify the final mixed clip is audible and does not compete with the first words. A duration check alone is insufficient: 0.5 seconds of silence still fails. With no reliable audition, report the listening limitation and use measurements only as technical evidence.

Known failure: the previously used Simple Whoosh's main peak was near source 0.624s; taking only source 0–0.2s discarded that body. Re-inspect the actual asset/version before reusing this measurement; names do not prove identical audio. Never reuse the old first-0.2s trim recipe.

For the two audited library files, compare the source hash with [whoosh-profiles.json](../assets/sfx/whoosh-profiles.json) before reusing its trim recipe. **Simple Whoosh: use about 0.70s on the timeline (21 frames at 30fps), source 0.30–1.07s at 1.1×; do not shorten it below about 0.667s without choosing/reviewing another source. Airy Short Whoosh: use 0.367–0.40s, starting at source 0.30s.** Re-align the actual transient after changing sourceIn; for a desired peak at timeline T, place the clip at `T - (source_peak - source_in) / playback_rate`. Check neighboring cues and keep fades after the main body. Source duration metadata can differ slightly from decoded length; validate the usable source range. Other files with the same names require inspection rather than inheriting these measurements.

## Opening accent for this user's series

The first three seconds are a deliberate attention beat. Add one prominent accent with the first presenter frame or opening motion; its main transient must land within 0–0.1 seconds, not wait for the later employee-introduction animation. Start with a 0.12–0.30-second pop/short impact, or a short swish matching an opening camera move, with fast attack and short release. Reserve clicks for the interaction/chat roles above. Avoid a low humming swell. If a supplied opening cue already serves this role, emphasize it instead of stacking duplicate hits.

Make this accent audibly stronger than routine body clicks: after matching source levels, start about 4–6 dB higher than the ordinary cue setting, then adjust against the actual narration. This is a starting mix difference, not a promise of twice the perceived loudness. Keep the first spoken words clear; control the effect's tail or choose another transient if it masks consonants. Do not raise the entire soundtrack to make this one cue louder. Keep a separate editable sound clip and record its onset, duration and gain in the cue sheet. Check the exported mix for a clear early accent and no clipping, aiming for at least 1 dB of peak headroom; measure true peak when supported. If listening is unavailable, report that the audible balance remains unverified.

Retiming a camera move requires re-aligning its sound, not automatically trimming it to the new motion interval. Preserve the whoosh body and release using the duration/source-window checks above. Chat-record changes still use crisp mouse clicks; this stronger opening rule does not restore humming chat transitions or increase every effect. Apply the [post-opening camera limit](jeff-person-openings.md#10秒后的运镜频次) before placing camera cues: when an excess move is removed, also remove its camera-only whoosh. Stable framing does not need replacement sounds to simulate movement or maintain an opening-only effect quota.

## Standalone prompt window

The user-provided reference frame comes from [Google’s advice for jobseekers](https://www.youtube.com/shorts/UBZIe0RQnaE), around 17–35 seconds. It is a different video from the Claude Cowork reference: a near-black dotted background, round product mark above a large dark rounded and outlined card, white left-aligned prompt in paragraphs, and a small light send-arrow button at bottom right. The card shows text appearing over time; it is a designed illustration rather than verified software capture. Do not transfer this source's unrelated captions to the Claude Cowork style by default.

For WorkBuddy use the workbuddy-simulator's `assets/workbuddy-prompt.html` as an editable starting point, with the green WorkBuddy mark and this series' [drifting star background](visual-grammar.md#sparse-star-background-for-this-users-series). Replace the sample prompt with the user's script and time its reveal to narration. Use a large font and readable hold; split lengthy prompts into states instead of cropping text. When the user requests no simulation badge, remove it from the copied render source and disclose the simulation on delivery. The illustrated send button did not operate WorkBuddy. Render with the simulator or editor, then synchronize and mix the action-specific sounds; the HTML renderer alone is silent.
