import vapoursynth as vs
from awsmfunc import ScreenGen, DynamicTonemap, FrameInfo, zresize
import random
import os
from pathlib import Path
from functools import partial
from typing import Union, List

core = vs.core

def vs_screengn(source: str, encode: Union[str, None], filter_b_frames: bool, num: int, dir: str) -> None:
    """
    Generate screenshots from a video source and its optional encoded version.

    Args:
        source (str): Path to the source video file.
        encode (Union[str, None]): Path to the encoded video file or None if not available.
        filter_b_frames (bool): Whether to filter B-frames from the encoded video.
        num (int): Number of screenshots to generate.
        dir (str): Directory where the screenshots will be saved.
    """
    # Choose source filter based on file extension
    if str(source).endswith(".m2ts"):
        src = core.lsmas.LWLibavSource(source)
    else:
        src = core.ffms2.Source(source, cachefile=f"{os.path.abspath(dir)}/ffms2.ffms2")

    # Handle optional encoding file
    if encode:
        enc = core.ffms2.Source(encode)

    # Determine number of frames in the source
    num_frames = len(src)
    start, end = 1000, num_frames - 10000  # Skip intros/credits

    # Function to filter B-frames
    def filter_ftype(n, f, clip, frame, frames, ftype="B"):
        if f.props["_PictType"].decode() == ftype:
            frames.append(frame)
        return clip

    frames = []
    if filter_b_frames and encode:
        # Filter B-frames from the encoded video
        with open(os.devnull, "wb") as f:
            i = 0
            while len(frames) < num:
                frame = random.randint(start, end)
                enc_f = enc[frame]
                enc_f = enc_f.std.FrameEval(partial(filter_ftype, clip=enc_f, frame=frame, frames=frames), enc_f)
                enc_f.output(f)
                i += 1
                if i > num * 10:
                    raise ValueError("Screen Engine: Encode doesn't seem to contain desired picture type frames.")
    else:
        # Generate random frames
        frames = [random.randint(start, end) for _ in range(num)]

    # Sort and write frame numbers to a file
    frames = sorted(frames)
    with open("screens.txt", "w") as txt:
        txt.writelines(f"{x}\n" for x in frames)

    # Crop and resize if an encoded video is provided
    if encode:
        if src.width != enc.width or src.height != enc.height:
            ref = zresize(enc, preset=src.height)
            crop = [(src.width - ref.width) / 2, (src.height - ref.height) / 2]
            src = src.std.Crop(left=crop[0], right=crop[0], top=crop[1], bottom=crop[1])
            width = enc.width if enc.width / enc.height > 16 / 9 else None
            height = enc.height if enc.width / enc.height <= 16 / 9 else None
            src = zresize(src, width=width, height=height)

    # Tonemap HDR if necessary
    tonemapped = False
    if src.get_frame(0).props["_Primaries"] == 9:
        tonemapped = True
        src = DynamicTonemap(src, src_fmt=False, libplacebo=False, adjust_gamma=True)
        if encode:
            enc = DynamicTonemap(enc, src_fmt=False, libplacebo=False, adjust_gamma=True)

    # Add FrameInfo and generate screenshots
    if tonemapped:
        src = FrameInfo(src, "Tonemapped")
    ScreenGen(src, dir, "a")

    if encode:
        if tonemapped:
            enc = FrameInfo(enc, "Encode (Tonemapped)")
        ScreenGen(enc, dir, "b")