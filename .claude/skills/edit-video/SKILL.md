---
name: edit-video
description: Edit the owner's own raw footage (cooking, gym, marketing, anything) into finished videos. Use whenever videos are uploaded for editing or the owner asks to make/edit/cut a video. Not for Twitch clipping or posting (that's clip-forge).
---

# Edit video

1. Read the brain first: `studio/brain/Owner taste.md`, `Editing playbook.md`, `Edit meeting.md`, `Plan format.md`
   (and `Viral format.md` in the clip-forge brain if available).
2. Put uploads in `studio/projects/<YYYY-MM-DD>-<slug>/raw/` (projects/ is git-ignored: footage never gets committed).
3. Prep: `python3 studio/studio.py probe|contact|transcribe|silences` on each file. Look at every contact sheet.
4. Hold the edit meeting (`Edit meeting.md`). Write `brief.md`.
5. Start from `studio/presets/<type>.json`, write `plan.json`, `python3 studio/studio.py render plan.json`.
6. Check stills at the hook, the middle and the end before sending. Send the MP4 to the owner (SendUserFile).
7. Revise from timestamped notes. On approval, log likes/dislikes in `Owner taste.md` and commit brain changes.
8. New technique or lesson learned → add it to the brain (playbook, a preset, or a new note). The brain is the memory.

Needs: ffmpeg, `pip install faster-whisper` (model downloads from Hugging Face on first run).
