#!/usr/bin/env python3
"""
Chay SAU khi preprocessing2_flist.py da sinh filelists/.
Dat file nay o thu muc goc cua repo CoMoSVC (canh segment_manifest_mapping.csv) roi chay:

    python make_val_small_and_verify.py

Lam 2 viec:
  1) Tao filelists/val_small.txt  -> stratified theo ca si, seed co dinh (de chon ckpt + theo doi val loss).
  2) Verify split: kiem tra khong co song_id nao roi vao >1 split (chong leak), dem unknown, in n_spk.
"""

import os
import re
import csv
import random
import collections

# ---- cau hinh ----
SEED            = 42
FILES_PER_SPK   = 3                          # so file moi ca si trong val_small
MANIFEST        = "segment_manifest_mapping.csv"
CONFIG          = "configs/diffusion.yaml"
VAL_LIST        = "filelists/val.txt"
VAL_SMALL_LIST  = "filelists/val_small.txt"
ALL_LISTS       = ["filelists/train.txt", "filelists/val.txt", "filelists/test.txt"]
# -------------------


def seg_id_from_path(path):
    m = re.search(r'(\d+)\.wav$', path.strip())
    return int(m.group(1)) if m else None


def load_manifest():
    seg_to_song = {}
    with open(MANIFEST, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            seg_to_song[int(row['segment_id'])] = int(row['song_id'])
    return seg_to_song


# ============ 1) TAO val_small.txt ============
def make_val_small():
    if not os.path.exists(VAL_LIST):
        print(f"[!] Khong thay {VAL_LIST}")
        return
    random.seed(SEED)
    by_spk = collections.defaultdict(list)
    for line in open(VAL_LIST):
        line = line.strip()
        if not line:
            continue
        spk = line.split('/')[-2]            # ./dataset/{spk}/{file}.wav
        by_spk[spk].append(line)

    picked = []
    for spk, files in sorted(by_spk.items()):
        picked += random.sample(files, min(FILES_PER_SPK, len(files)))

    os.makedirs(os.path.dirname(VAL_SMALL_LIST), exist_ok=True)
    with open(VAL_SMALL_LIST, 'w') as f:
        f.write('\n'.join(picked) + '\n')

    print(f"[val_small] {len(picked)} file tu {len(by_spk)} ca si "
          f"(<= {FILES_PER_SPK}/ca si) -> {VAL_SMALL_LIST}")


# ============ 2) VERIFY SPLIT ============
def verify_split():
    seg_to_song = load_manifest()
    print(f"[manifest] {len(seg_to_song)} segment, "
          f"{len(set(seg_to_song.values()))} bai")

    # song_id (hoac 'unknown_{seg}') -> tap cac split chua no
    song_in_splits = collections.defaultdict(set)
    counts   = {}
    unknowns = {}
    for fl in ALL_LISTS:
        if not os.path.exists(fl):
            print(f"[!] Thieu {fl}")
            continue
        split = os.path.basename(fl).replace('.txt', '')
        n = u = 0
        for line in open(fl):
            line = line.strip()
            if not line:
                continue
            n += 1
            sid = seg_id_from_path(line)
            song = seg_to_song.get(sid)
            if song is None:
                u += 1
                key = f"unknown_{sid}"
            else:
                key = song
            song_in_splits[key].add(split)
        counts[split]   = n
        unknowns[split] = u

    print("[counts]   " + " | ".join(f"{k}: {v}" for k, v in counts.items()))
    print("[unknown]  " + " | ".join(f"{k}: {v}" for k, v in unknowns.items())
          + "   (nen = 0)")
    leaked = {k: s for k, s in song_in_splits.items() if len(s) > 1}
    if leaked:
        print(f"[LEAK] {len(leaked)} bai xuat hien o >1 split! Vi du:")
        for k, s in list(leaked.items())[:10]:
            print(f"        {k}: {sorted(s)}")
    else:
        print("done split by song-id")

    if os.path.exists(CONFIG):
        for line in open(CONFIG):
            if 'n_spk' in line:
                print(f"[config]   {line.strip()} ")
                break


if __name__ == "__main__":
    print("=" * 60)
    make_val_small()
    print("-" * 60)
    verify_split()
    print("=" * 60)