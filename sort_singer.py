import argparse
import glob
import os
import re
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract_dir",     type=str, required=True)
    parser.add_argument("--dataset_raw_dir", type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    all_wavs = glob.glob(os.path.join(args.extract_dir, "**", "*.wav"), recursive=True)
    all_wavs += glob.glob(os.path.join(args.extract_dir, "*.wav"))
    all_wavs = list(set(all_wavs))

    if not all_wavs:
        print(f"[WARN] No .wav files in: {args.extract_dir}")
        return

    moved, skipped, failed = 0, 0, 0

    for wav_path in sorted(all_wavs):
        filename    = os.path.basename(wav_path)
        name_no_ext = os.path.splitext(filename)[0]

        match = re.match(r'^(.+)_(\d+)$', name_no_ext)
        if not match:
            print(f"  [FAIL] Cannot parse: {filename}")
            failed += 1
            continue

        singer_raw   = match.group(1)
        segment_id   = match.group(2)
        singer_name  = singer_raw.replace(" ", "")
        new_filename = f"{singer_name}_{segment_id}.wav"
        dest_dir  = os.path.join(args.dataset_raw_dir, singer_name)
        os.makedirs(dest_dir, exist_ok=True)

        dest_path = os.path.join(dest_dir, new_filename)
        if not os.path.exists(dest_path):
            shutil.copy2(wav_path, dest_path)
            moved += 1
        else:
            skipped += 1

    print(f"\n  Result: {moved} moved | {skipped} already exist | {failed} failed")
    print(f"\n  Singer breakdown:")
    for singer in sorted(os.listdir(args.dataset_raw_dir)):
        singer_dir = os.path.join(args.dataset_raw_dir, singer)
        if os.path.isdir(singer_dir):
            count = len(glob.glob(os.path.join(singer_dir, "*.wav")))
            print(f"    {singer}: {count} files")


if __name__ == "__main__":
    main()