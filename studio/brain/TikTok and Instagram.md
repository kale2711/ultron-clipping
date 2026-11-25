# TikTok + Instagram Reels: delivery standard

Every video we make is posted to BOTH. Edit once so it works on both.

## Export (render does this automatically)
- 1080x1920 (9:16), 30 fps, H.264 High, yuv420p, AAC 48 kHz 192k, faststart. Loudness -14 LUFS, peak -1.5 dB.
- A `_cover.jpg` is saved next to every render (frame at `"cover"` seconds, default 0.5s). Use it as the Reels
  cover / TikTok cover. Choose a frame with the title card + the best visual, so set `"cover"` deliberately.

## Safe zones (1080x1920): keep ALL text and faces out of these
| | top | bottom | right |
|---|---|---|---|
| TikTok | 130 px | 420 px (caption, username, sound) | 140 px (like/comment/share) |
| Reels | 220 px | 380 px | 120 px |
- Title cards: y 0.18 to 0.30. Burned-in captions: y 0.62 to 0.72. CTA/end card: y about 0.6 (NOT 0.8: that's under the UI).
- Check every render: `python3 studio/studio.py safe out/final.mp4 -t 1 <mid> <end>` (red = TikTok UI, blue lines = Reels).
- Instagram grid crops the cover to 3:4 / 1:1 in the middle: keep the cover's title near the centre.

## Length
- Discovery sweet spot 15 to 35s. Both platforms allow longer (Reels up to 3 min for reach; TikTok longer), but
  only go past 60s when the owner asks or the content holds attention every second.

## Sound
- Music we add is baked in. Trending sounds can't be added from here: if the owner wants one, export a version with
  voice only (no music) so they can add the sound in-app with the original-audio volume turned down.
  (Plan: drop `"music"` and render to `final_nomusic.mp4`.)
- Copyrighted commercial music baked into the file can get muted, especially on business accounts. Prefer the owner's
  licensed tracks or in-app sounds.

## Posting copy (deliver alongside every video)
For each video, write a `post.md` with: TikTok caption (short, hook-first, 3 to 5 hashtags), Instagram caption
(can be longer, 3 to 5 hashtags), on-screen keyword ideas, and cover-frame time. The owner posts; we don't.
