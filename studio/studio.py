#!/usr/bin/env python3
"""Ultron Studio: turn raw footage into finished videos from one edit plan (JSON).

Commands
  probe FILE...                 length, size, fps, audio for each file
  transcribe FILE [-o out.json] word-level transcript (faster-whisper)
  silences FILE [--db -32 --min 0.45]
                                suggest keep-segments with dead air removed
  contact FILE [-n 16]          contact sheet JPG of frames, to review footage visually
  render PLAN.json              build the final video described by the plan

The plan format is documented in studio/brain/Plan format.md.
Pipeline: segments (trim, speed, reframe) -> join -> transcribe the joined cut
(so captions always line up with the edit) -> captions + text cards + music + loudness -> final.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

FORMATS = {"9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "16:9": (1920, 1080)}
FPS = 30


def run(cmd, binary=False):
    r = subprocess.run(cmd, capture_output=True, text=not binary)
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace") if binary else r.stderr
        sys.stderr.write(err[-4000:])
        raise SystemExit(f"command failed: {' '.join(cmd[:6])} ...")
    return r


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    info = {"file": path, "duration": round(float(d["format"].get("duration", 0)), 2), "has_audio": a is not None}
    if v:
        w, h = int(v["width"]), int(v["height"])
        rot = 0
        for sd in v.get("side_data_list", []):
            rot = int(sd.get("rotation", 0) or 0)
        rot = int(v.get("tags", {}).get("rotate", rot))
        if abs(rot) in (90, 270):
            w, h = h, w
        num, den = (v.get("avg_frame_rate") or "0/1").split("/")
        info.update(width=w, height=h, fps=round(int(num) / max(int(den), 1), 2))
    return info


# ---------------------------------------------------------------- transcription
_model = None


def transcribe(path, model_size=None):
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel(model_size or os.environ.get("STUDIO_WHISPER", "small"), device="cpu", compute_type="int8")
    import numpy as np  # decode with ffmpeg ourselves: avoids PyAV version clashes
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], binary=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    segs, _ = _model.transcribe(audio, word_timestamps=True, vad_filter=True)
    words = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if t:
                words.append({"w": t, "s": round(w.start, 3), "e": round(w.end, 3)})
    return words


# ---------------------------------------------------------------- dead-air finder
def silences(path, db=-32, min_len=0.45, pad=0.12):
    info = probe(path)
    if not info["has_audio"]:
        return [{"src": path, "in": 0, "out": info["duration"]}]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={db}dB:d={min_len}",
                        "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    keep, cur = [], 0.0
    for s, e in zip(starts, ends + [info["duration"]] * (len(starts) - len(ends))):
        if s - cur > 0.25:
            keep.append({"src": path, "in": round(max(cur - pad, 0), 2), "out": round(s + pad, 2)})
        cur = e
    if info["duration"] - cur > 0.25:
        keep.append({"src": path, "in": round(max(cur - pad, 0), 2), "out": info["duration"]})
    return keep


def contact_sheet(path, n=16, out=None):
    info = probe(path)
    out = out or os.path.splitext(path)[0] + "_sheet.jpg"
    step = max(info["duration"] / n, 0.1)
    cols = 4
    rows = (n + cols - 1) // cols
    run(["ffmpeg", "-y", "-i", path, "-vf",
         f"fps=1/{step:.3f},scale=480:-2,drawtext=text='%{{pts\\:hms}}':x=8:y=8:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}",
         "-frames:v", "1", out])
    return out


# ---------------------------------------------------------------- video building blocks
def reframe_filter(fmt, mode, focus_x=0.5):
    W, H = FORMATS[fmt]
    if mode == "fit":  # letterbox onto blurred copy of itself
        return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.08[bg];"
                f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    # crop: fill the frame, choose horizontal focus point 0..1
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:(iw-{W})*{focus_x}:(ih-{H})/2")


def atempo_chain(speed):
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0"); s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5"); s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


def render_segment(seg, fmt, default_reframe, out, grade=None):
    info = probe(seg["src"])
    t_in, t_out = float(seg.get("in", 0)), float(seg.get("out", info["duration"]))
    speed = float(seg.get("speed", 1.0))
    mode = seg.get("reframe", default_reframe)
    vf = reframe_filter(fmt, mode, seg.get("focus_x", 0.5))
    if seg.get("zoom"):  # slow push-in, e.g. 1.08 = 8% over the shot
        z = float(seg["zoom"]); dur = (t_out - t_in) / speed
        W, H = FORMATS[fmt]
        src_dur = t_out - t_in
        vf += (f",scale=w='2*trunc({W}*(1+({z}-1)*t/{src_dur:.3f})/2)':h=-2:eval=frame,"
               f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2")
    g = seg.get("grade", grade)
    if g == "warm":
        vf += ",eq=saturation=1.15:contrast=1.05,colorbalance=rs=0.04:bs=-0.04"
    elif g == "punchy":
        vf += ",eq=saturation=1.25:contrast=1.12"
    elif g == "clean":
        vf += ",eq=saturation=1.08:contrast=1.04"
    vf += f",setpts=(PTS-STARTPTS)/{speed},fps={FPS},format=yuv420p,setsar=1"
    keep_audio = info["has_audio"] and not seg.get("mute")
    vol = float(seg.get("volume", 1.0))
    cmd = ["ffmpeg", "-y", "-ss", f"{t_in}", "-to", f"{t_out}", "-i", seg["src"]]
    if keep_audio:
        af = f"asetpts=PTS-STARTPTS,{atempo_chain(speed)},volume={vol},aresample=48000"
        cmd += ["-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]", "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ac", "2", out]
    run(cmd)


# ---------------------------------------------------------------- captions & text cards (ASS)
def ass_time(t):
    t = max(t, 0)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def ass_color(hexstr, alpha="00"):
    h = hexstr.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}"


CAPTION_STYLES = {
    # name: font, size, text colour, highlight colour, outline, uppercase, words per line
    "bold":    dict(font="Inter Display Black", size=98, color="FFFFFF", hi="FFE600", outline=6, upper=True, words=3),
    "clean":   dict(font="Inter Display SemiBold", size=78, color="FFFFFF", hi="FFFFFF", outline=4, upper=False, words=4),
    "gym":     dict(font="Inter Display Black", size=110, color="FFFFFF", hi="FF3B30", outline=7, upper=True, words=2),
    "kitchen": dict(font="Inter Display ExtraBold", size=90, color="FFFFFF", hi="FFB020", outline=5, upper=False, words=3),
}


def chunk_words(words, per_line, max_gap=0.6, max_len=1.6):
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= per_line or w["s"] - cur[-1]["e"] > max_gap or w["e"] - cur[0]["s"] > max_len
                    or re.search(r"[.!?]$", cur[-1]["w"])):
            chunks.append(cur); cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(path, fmt, words, cap, cards):
    W, H = FORMATS[fmt]
    st = dict(CAPTION_STYLES[cap.get("style", "bold")])
    st.update({k: v for k, v in cap.items() if k in st})
    y_cap = int(H * cap.get("y", 0.70))
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,{st['font']},{st['size']},{ass_color(st['color'])},&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,{st['outline']},2,5,60,60,0,1",
        f"Style: Card,Inter Display Black,{int(W*0.085)},&H00FFFFFF,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,70,70,0,1",
        f"Style: Box,Inter Display ExtraBold,{int(W*0.055)},&H00111111,&H000000FF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,3,18,0,5,70,70,0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    hi = ass_color(st["hi"]); base = ass_color(st["color"])
    if cap.get("on", True):
        for ch in chunk_words(words, st["words"]):
            toks = [(w["w"].upper() if st["upper"] else w["w"]) for w in ch]
            for i, w in enumerate(ch):
                end = ch[i + 1]["s"] if i + 1 < len(ch) else w["e"] + 0.25
                txt = " ".join((f"{{\\c{hi}}}{t}{{\\c{base}}}" if j == i else t) for j, t in enumerate(toks))
                pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if i == 0 else ""
                lines.append(f"Dialogue: 1,{ass_time(w['s'])},{ass_time(end)},Cap,,0,0,0,,{{\\pos({W//2},{y_cap})}}{pop}{txt}")
    for c in cards:
        style = "Box" if c.get("style") == "box" else "Card"
        y = int(H * c.get("y", 0.22))
        fade = "{\\fad(120,120)}"
        txt = c["text"].replace("\n", "\\N")
        lines.append(f"Dialogue: 2,{ass_time(c['start'])},{ass_time(c['end'])},{style},,0,0,0,,{{\\pos({W//2},{y})}}{fade}{txt}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- render
def render(plan_path):
    plan = json.load(open(plan_path))
    if plan.get("preset"):  # preset supplies defaults; the plan overrides them
        pre = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets", plan["preset"] + ".json")))
        for k, v in pre.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict) and isinstance(plan.get(k), dict):
                plan[k] = {**v, **plan[k]}
            elif k not in plan and k not in ("text", "music"):
                plan[k] = v
    base = os.path.dirname(os.path.abspath(plan_path))
    absp = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    fmt = plan.get("format", "9:16")
    out = absp(plan["output"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    work = tempfile.mkdtemp(prefix="studio_")
    try:
        parts = []
        for i, seg in enumerate(plan["segments"]):
            seg = dict(seg, src=absp(seg["src"]))
            p = os.path.join(work, f"seg{i:03d}.mp4")
            render_segment(seg, fmt, plan.get("reframe", "crop"), p, plan.get("grade"))
            parts.append(p)
            print(f"  segment {i+1}/{len(plan['segments'])} done", flush=True)
        lst = os.path.join(work, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        joined = os.path.join(work, "joined.mp4")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
        dur = probe(joined)["duration"]

        cap = plan.get("captions", {"on": True, "style": "bold"})
        words = []
        if cap.get("on", True):
            print("  transcribing the cut for captions...", flush=True)
            words = transcribe(joined)
            for fix in cap.get("fixes", []):  # [["wrong","right"], ...]
                for w in words:
                    if w["w"].strip(".,!?").lower() == fix[0].lower():
                        w["w"] = w["w"].lower().replace(fix[0].lower(), fix[1])
            json.dump(words, open(os.path.splitext(out)[0] + ".words.json", "w"), indent=0)
        cards = [dict(c, end=(dur + c["end"]) if c["end"] < 0 else c["end"],
                      start=(dur + c["start"]) if c["start"] < 0 else c["start"]) for c in plan.get("text", [])]
        ass = os.path.join(work, "subs.ass")
        build_ass(ass, fmt, words, cap, cards)

        inputs = ["-i", joined]
        fc = [f"[0:v]subtitles='{ass}':fontsdir=/usr/share/fonts[v]"]
        voice = "[0:a]volume=1.0[voice]"
        music = plan.get("music")
        if music:
            inputs += ["-stream_loop", "-1", "-i", absp(music["file"])]
            mv = float(music.get("volume", 0.22))
            fade_out = max(dur - 1.5, 0)
            fc.append(f"[1:a]atrim=start={music.get('start', 0)},asetpts=PTS-STARTPTS,atrim=0:{dur},volume={mv},"
                      f"afade=t=in:d=0.6,afade=t=out:st={fade_out}:d=1.5,aresample=48000[m]")
            if music.get("duck", True):
                fc.append("[0:a]asplit[voice][sc]")
                fc.append("[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md]")
                fc.append("[voice][md]amix=inputs=2:duration=first:normalize=0[mix]")
            else:
                fc.append(f"{voice};[voice][m]amix=inputs=2:duration=first:normalize=0[mix]")
        else:
            fc.append("[0:a]anull[mix]")
        fc.append("[mix]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
        run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur}", out])
        print(f"done: {out} ({dur:.1f}s, {fmt})")
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe"); p.add_argument("files", nargs="+")
    p = sub.add_parser("transcribe"); p.add_argument("file"); p.add_argument("-o")
    p = sub.add_parser("silences"); p.add_argument("file"); p.add_argument("--db", type=float, default=-32); p.add_argument("--min", type=float, default=0.45)
    p = sub.add_parser("contact"); p.add_argument("file"); p.add_argument("-n", type=int, default=16); p.add_argument("-o")
    p = sub.add_parser("render"); p.add_argument("plan")
    a = ap.parse_args()
    if a.cmd == "probe":
        for f in a.files:
            print(json.dumps(probe(f)))
    elif a.cmd == "transcribe":
        words = transcribe(a.file)
        out = a.o or os.path.splitext(a.file)[0] + ".words.json"
        json.dump(words, open(out, "w"), indent=0)
        print(" ".join(w["w"] for w in words)); print(f"\nsaved {out}")
    elif a.cmd == "silences":
        print(json.dumps(silences(a.file, a.db, a.min), indent=1))
    elif a.cmd == "contact":
        print(contact_sheet(a.file, a.n, a.o))
    elif a.cmd == "render":
        render(a.plan)


if __name__ == "__main__":
    main()
