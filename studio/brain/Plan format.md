# plan.json: the edit, as data

Paths are relative to the plan file. Render with `python3 studio/studio.py render plan.json`.

```json
{
  "format": "9:16",              // 9:16 | 1:1 | 4:5 | 16:9
  "reframe": "crop",             // default per segment: crop | fit
  "grade": "warm",               // warm | punchy | clean | (omit)
  "output": "out/final.mp4",
  "segments": [
    {"src": "raw/IMG_0412.MOV", "in": 83.2, "out": 85.0},
    {"src": "raw/IMG_0412.MOV", "in": 12.0, "out": 30.0, "speed": 3, "mute": true},
    {"src": "raw/IMG_0415.MOV", "in": 4.1, "out": 7.9, "zoom": 1.08, "focus_x": 0.35},
    {"src": "raw/IMG_0415.MOV", "in": 40, "out": 42, "speed": 0.5, "volume": 0.6, "reframe": "fit"}
  ],
  "captions": {"on": true, "style": "kitchen", "y": 0.70, "fixes": [["gnocci", "gnocchi"]]},
  "music": {"file": "music/track.mp3", "volume": 0.2, "start": 12, "duck": true},
  "text": [
    {"text": "15-MIN\nGARLIC PASTA", "start": 0, "end": 2.2},
    {"text": "Follow for part 2", "start": -2.0, "end": -0.1, "style": "box", "y": 0.6}
  ]
}
```

- Segment times are in the **source** file; text times are on the **final** timeline (negative = from the end).
- Captions are transcribed from the finished cut, so they always line up after speed changes.
- A `.words.json` is saved next to the output so caption wording can be checked and fixed.
- Caption styles: `bold` (yellow highlight, caps), `clean` (no highlight, sentence case), `gym` (red, caps, 2 words),
  `kitchen` (amber, sentence case).
