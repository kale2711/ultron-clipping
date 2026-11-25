# Edit meeting (run this before every edit)

Footage arrives → before touching it, hold a short "meeting" with the owner. Goal: leave with a filled-in brief
so the first cut is close. Look at the footage FIRST (probe + contact sheet + transcript), so questions are specific
("the clip at 2:10 where you flip the steak — is that the hook?") instead of generic.

## 0. Before the meeting (silent prep)
1. `python3 studio/studio.py probe <files>`: lengths, orientation, fps, audio.
2. `python3 studio/studio.py contact <file>`: look at the contact sheet for every file.
3. `python3 studio/studio.py transcribe <file>`: read what's said.
4. Note: best-looking moments, best lines, problems (shaky, dark, noisy audio, vertical vs horizontal).

## 1. The questions (ask in one message, numbered, with my suggested answer for each)
1. **Type**: cooking / gym / marketing / other? (→ pick the preset in `studio/presets/`)
2. **Platform + format**: TikTok/Reels/Shorts 9:16 (default), feed 4:5, YouTube 16:9? More than one?
3. **Length target**: e.g. 20–35s short, 60s, or long-form.
4. **The hook**: the moment/line for the first 2 seconds. Propose 2–3 candidates with timestamps.
5. **Story**: what has to be in it, in order? What must be cut?
6. **Text on screen**: title, step labels, CTA ("Follow for part 2", link, offer code). Exact wording.
7. **Captions**: on/off, style (bold / clean / gym / kitchen), any words Whisper will misspell (names, brands).
8. **Audio**: keep original voice? music (owner supplies track or none; ducked under voice)? trending sound to be added in-app?
9. **Look**: grade (warm for food, punchy for gym, clean for brand), speed-ups, slow-mo moments.
10. **Brand**: logo/handle on screen? colors? things to avoid?
11. **Higgsfield**: any shots worth pulling from their Higgsfield library (B-roll, intro)?

Keep it fast: if the owner says "you choose", use the preset defaults and say what was chosen.

## 2. Write the brief
Save to `studio/projects/<date>-<slug>/brief.md` (answers + chosen hook + outline with timestamps).
Then write `plan.json` (see `Plan format.md`), render, send the video back.

## 3. Review round
Send the render with a short changelog-style note: hook used, length, what was cut. Ask for notes as
timestamps ("0:07 too long"). Apply, re-render. When the owner approves, log what they liked/disliked
in `Owner taste.md` so the next edit starts closer.
