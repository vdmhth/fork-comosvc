from pathlib import Path
import math
import numpy as np
import librosa
import pyworld as pw


def median_f0_of_wav(wav_path, sr=16000):
    y, _ = librosa.load(wav_path, sr=sr, mono=True)
    y = y.astype(np.float64)

    f0, t = pw.harvest(y, sr)
    f0 = f0[f0 > 0]

    if len(f0) == 0:
        return None

    return float(np.median(f0))

def median_f0_of_singer(singer_dir, max_files=50):
    wavs = sorted(Path(singer_dir).glob("*.wav"))[:max_files]
    vals = []

    for wav in wavs:
        try:
            m = median_f0_of_wav(wav)
            if m is not None:
                vals.append(m)
        except Exception as e:
            print(f"[WARN] {wav}: {e}")

    if not vals:
        return None

    return float(np.median(vals))


def semitone_shift(source_f0, target_f0, clamp=12):
    shift = 12 * math.log2(target_f0 / source_f0)
    shift = round(shift)
    shift = max(-clamp, min(clamp, shift))
    return shift
source_wav = "raw/test.wav"
target_singer = "TaylorSwift"

target_dir = f"dataset/{target_singer}"

src_f0 = median_f0_of_wav(source_wav)
tgt_f0 = median_f0_of_singer(target_dir, max_files=50)

print("source median f0:", src_f0)
print("target median f0:", tgt_f0)

if src_f0 and tgt_f0:
    k = semitone_shift(src_f0, tgt_f0)
    print("suggested -k:", k)
else:
    print("Could not estimate key.")