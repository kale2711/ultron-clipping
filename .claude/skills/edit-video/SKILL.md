---
name: edit-video
description: Edit the owner's own raw footage (cooking, gym, marketing, anything) into finished videos. Use whenever videos are uploaded for editing or the owner asks to make/edit/cut a video. Not for Twitch clipping or posting (that's clip-forge).
---

# Edit video

1. Read the brain first: `studio/brain/Style references.md` (the owner's standard; match it), `Owner taste.md`, `Editing playbook.md`, `Edit meeting.md`, `Plan format.md`, `TikTok and Instagram.md`, `Higgsfield.md`
   (and `Viral format.md` in the clip-forge brain if available).
2. Put uploads in `studio/projects/<YYYY-MM-DD>-<slug>/raw/` (projects/ is git-ignored: footage never gets committed).
3. Prep: `python3 studio/studio.py probe|contact|transcribe|silences` on each file. Look at every contact sheet.
4. Hold the edit meeting (`Edit meeting.md`). Write `brief.md`. If AI shots would help, write `higgsfield.md` (see `Higgsfield.md`).
5. Start from `studio/presets/<type>.json`, write `plan.json`, `python3 studio/studio.py render plan.json`.
6. Check `studio.py safe` frames (hook, middle, end): no text in the TikTok/Reels UI zones. Send the MP4 + `_cover.jpg`
   + `post.md` (captions/hashtags for TikTok and Instagram) to the owner (SendUserFile).
7. Revise from timestamped notes. On approval, log likes/dislikes in `Owner taste.md` and commit brain changes.
8. Owner sends a reference video → `studio.py ref` it, write it up in `Style references.md`, update the preset.
9. New technique or lesson learned → add it to the brain (playbook, a preset, or a new note). The brain is the memory.

Needs: ffmpeg, `pip install faster-whisper` (model downloads from Hugging Face on first run).
