import sys
print(sys.executable)

import torch
import librosa
import soundfile
import pyworld
import fairseq

print("all ok")
print("cuda:", torch.cuda.is_available())