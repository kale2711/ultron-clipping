# Editing playbook: raw footage → finished video

Tool: `studio/studio.py` (ffmpeg + faster-whisper). Cross-reference `Viral format.md` (clip-forge brain) for
what performs; this file is about *making* the video.

## Universal rules (short-form)
- **Hook in 0–2s.** Open on the payoff or most striking visual/line, never on a setup or "hey guys".
  Cooking: final plated shot or sizzle. Gym: the heaviest rep / the face. Marketing: the problem or the result.
- **No dead air.** Run `silences` to get keep-segments, then trim by eye. Gaps > 0.3s between lines get cut.
- **Cut every 1.5–3s** in short-form; a shot longer than ~4s needs movement (zoom 1.06–1.12, speed-up, or text).
- **Captions burned in** (most watch muted). Max 2–4 words per line, current word highlighted, at ~70% height
  (clear of the TikTok UI on the right/bottom). Fix misheard names via `captions.fixes`.
- **Text cards** short: ≤ 5 words title, top third (y≈0.2). CTA in last 2s.
- **Audio**: voice always wins. Music 0.15–0.25, ducked. Final loudness −14 LUFS (done automatically).
- **End clean or loop.** Best: last frame flows into first frame so the video loops.
- **Length**: 15–35s for discovery; 45–90s only if every second earns it.

## Reframing horizontal footage to 9:16
- `crop` (default): fills the screen; set `focus_x` (0 = left, 1 = right) to keep the subject in frame.
- `fit`: the whole frame on a blurred copy of itself. Use for wide shots where cropping loses the action.

## Common recipes
| Need | Plan setting |
|---|---|
| Speed through prep / warm-up | segment `"speed": 2`–`4`, `"mute": true` (music carries it) |
| Slow-mo key rep / pour / sizzle | segment `"speed": 0.5` (best if shot at 60fps+) |
| Push-in on a static shot | segment `"zoom": 1.08` |
| Food looks dull | `"grade": "warm"` |
| Gym / energy | `"grade": "punchy"` |
| Brand / product | `"grade": "clean"` |

## Workflow
1. Meeting (`Edit meeting.md`) → brief.
2. Build `plan.json` segment by segment from the transcript timestamps + contact sheets.
3. Render → watch key frames (pull stills at hook, mid, end) before sending.
4. Send to owner; revise; log taste in `Owner taste.md`.

## Higgsfield
See `Higgsfield.md` (plan the AI shots, owner generates, I cut them in).

## Platforms
All videos go to TikTok + Instagram Reels: follow `TikTok and Instagram.md` (safe zones, cover, post copy).
