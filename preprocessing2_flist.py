import argparse
import csv
import os
import re
import wave
from collections import defaultdict
from random import shuffle, seed
from loguru import logger
from tqdm import tqdm
import utils

MIN_SONGS = 3  # Singer có ít hơn số này thì train only


def get_wav_duration(file_path):
    try:
        with wave.open(file_path, 'rb') as f:
            return f.getnframes() / float(f.getframerate())
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return 0.0


def load_manifest(manifest_path):
    seg_to_song = {}
    with open(manifest_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            seg_to_song[int(row['segment_id'])] = int(row['song_id'])
    logger.info(f"Loaded manifest: {len(seg_to_song)} segments, "
                f"{len(set(seg_to_song.values()))} unique songs")
    return seg_to_song


def extract_segment_id(filename):
    match = re.search(r'(\d+)\.wav$', filename)
    if match:
        return int(match.group(1))
    return None


def split_songs_per_singer(songs, val_ratio, test_ratio, min_songs):
    n = len(songs)
    if n < min_songs:
        return songs, [], []

    n_val  = max(1, int(n * val_ratio))   # >=1 bai val moi ca si (giu coverage)
    n_test = max(1, int(n * test_ratio))  # >=1 bai test moi ca si

    test  = songs[:n_test]
    val   = songs[n_test:n_test + n_val]
    train = songs[n_test + n_val:]

    if not train:
        train = songs[:1]
        val   = songs[1:2] if len(songs) > 1 else []
        test  = songs[2:3] if len(songs) > 2 else []

    return train, val, test


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_list",  type=str, default="./filelists/train.txt")
    parser.add_argument("--val_list",    type=str, default="./filelists/val.txt")
    parser.add_argument("--test_list",   type=str, default="./filelists/test.txt")
    parser.add_argument("--source_dir",  type=str, default="./dataset")
    parser.add_argument("--manifest",    type=str, default="./segment_manifest_mapping.csv")
    parser.add_argument("--val_ratio",   type=float, default=0.05)  # 5% bai/ca si -> val
    parser.add_argument("--test_ratio",  type=float, default=0.10)  # 10% bai/ca si -> test
    parser.add_argument("--seed",        type=int,   default=42)     # train = phan con lai (~85%)
    args = parser.parse_args()

    seed(args.seed)

    # Load manifest
    if not os.path.exists(args.manifest):
        logger.error(f"Manifest not found: {args.manifest}")
        logger.error("cannot find mapping file.")
        exit(1)

    seg_to_song = load_manifest(args.manifest)

    train_files, val_files, test_files = [], [], []
    spk_dict = {}
    spk_id   = 0

    for speaker in tqdm(sorted(os.listdir(args.source_dir))):
        speaker_dir = os.path.join(args.source_dir, speaker)
        if not os.path.isdir(speaker_dir):
            continue

        spk_dict[speaker] = spk_id
        spk_id += 1

        song_to_wavs = defaultdict(list)
        skipped = 0

        for file_name in sorted(os.listdir(speaker_dir)):
            if not file_name.endswith(".wav") or file_name.startswith("."):
                continue

            file_path = os.path.join(args.source_dir, speaker, file_name)

            if get_wav_duration(file_path) < 0.3:
                skipped += 1
                continue

            seg_id = extract_segment_id(file_name)
            if seg_id is None:
                logger.warning(f"Cannot extract segment_id from: {file_name}")
                continue

            song_id = seg_to_song.get(seg_id)
            if song_id is None:
                # Segment không có trong manifest → cho vào train
                song_to_wavs[f"unknown_{seg_id}"].append(file_path)
            else:
                song_to_wavs[song_id].append(file_path)

        # Split theo song_id
        all_songs = list(song_to_wavs.keys())
        shuffle(all_songs)

        train_songs, val_songs, test_songs = split_songs_per_singer(
            all_songs, args.val_ratio, args.test_ratio, MIN_SONGS
        )

        n_train_seg = sum(len(song_to_wavs[s]) for s in train_songs)
        n_val_seg   = sum(len(song_to_wavs[s]) for s in val_songs)
        n_test_seg  = sum(len(song_to_wavs[s]) for s in test_songs)

        for s in train_songs:
            train_files.extend(song_to_wavs[s])
        for s in val_songs:
            val_files.extend(song_to_wavs[s])
        for s in test_songs:
            test_files.extend(song_to_wavs[s])

        logger.info(
            f"  {speaker}: {len(all_songs)} songs, {len(train_songs)} train / "
            f"{len(val_songs)} val / {len(test_songs)} test songs "
            f"→ {n_train_seg} / {n_val_seg} / {n_test_seg} segments"
            + (f" ({skipped} skipped)" if skipped else "")
        )

    shuffle(train_files)
    shuffle(val_files)
    shuffle(test_files)

    os.makedirs("filelists", exist_ok=True)

    for path, name in [
        (args.train_list, train_files),
        (args.val_list,   val_files),
        (args.test_list,  test_files),
    ]:
        logger.info(f"Writing {path} ({len(name)} segments)")
        with open(path, "w") as f:
            f.write("\n".join(name) + "\n")

    logger.info(f"\nTotal: {len(train_files)} train | {len(val_files)} val | {len(test_files)} test segments")
    logger.info(f"Singers: {spk_id}")

    # Ghi config
    d_config_template = utils.load_config("configs_template/diffusion_template.yaml")
    d_config_template["model"]["n_spk"] = spk_id
    d_config_template["spk"] = spk_dict

    logger.info("Writing configs/diffusion.yaml")
    utils.save_config("configs/diffusion.yaml", d_config_template)