# Higgsfield (AI video) as an editing skill

## What the connector can and can't do (checked 2026-11-25)
- CAN: read credits (`balance`; Ultra plan, about 3,000 credits at setup), list models + their settings
  (`models_list`, `models_get`), list finished generations with result URLs (`show_generations`), import a
  Claude Motion MP4 into Higgsfield.
- CAN'T: start a generation, upload our footage. The owner presses Generate in Higgsfield.

## The skill: I plan, owner generates, I edit it in
1. During the edit meeting, spot shots Higgsfield would improve (see "When to use").
2. Write a **Higgsfield shot list** in the project's `higgsfield.md`: for each shot the model, aspect 9:16,
   duration, resolution, settings, the exact prompt, and which frame from our footage to use as `start_image`
   (export it with ffmpeg so the owner can upload it). Keep prompts concrete: subject, action, camera move,
   lighting, lens, mood; match the grade of our footage.
3. Owner generates in Higgsfield.
4. I find the results with `show_generations` (type video/image/marketing_studio), download the result URL
   into `raw/`, and use it as a normal segment in `plan.json`.
   (The CDN host of result URLs may need adding to the environment's allowed hosts the first time.)

## When to use (and which model)
| Need | Model | Notes |
|---|---|---|
| Scroll-stopping intro / B-roll from text | `seedance_2_5` (t2v) or `cinematic_studio_3_0` | 9:16, 4 to 8s, 1080p. Cinema Studio 3.0 = most premium look. |
| Animate one of OUR stills (plated dish, product shot) | `seedance_2_5` omni_reference with start_image, or `minimax_hailuo` | Keeps it looking like our real food/product. |
| Product ad / UGC-style marketing video | `marketing_studio_video` | 12 to 15s, TikTok/Reels-ready; uses Higgsfield products/avatars. |
| Restyle or fix a real clip (up to 15s) | `flux_3_video_edit`, `seedance_2_5` video_edit | e.g. clean background, change lighting. |
| Make a clip longer (end card, loop) | `seedance_2_5` video_extension | forward/backward. |
| Cut out the background (gym/product on brand colour) | Video Background Remover | |
| Spanish (etc.) version of a talking video | `dubbing` (+ `sync_so` lipsync) | Good for marketing reach. |

## Rules
- Real footage is the star; AI shots are seasoning (hook, transition, end card). Never fake a result the owner
  didn't make (e.g. fake food or fake physique transformations): that hurts trust and can break platform rules.
- TikTok and Instagram want AI-generated content labelled. When a video contains realistic AI shots, tell the
  owner to switch on the "AI-generated" label when posting.
- Always quote the credit cost / settings before the owner generates.
