
## 🚀 
```shell
bash run_prepare.sh

sbatch --partition=<PARTITION> 3_preprocess.sh

sbatch --partition=<PARTITION> 4_train_teacher.sh

sbatch --partition=<PARTITION> 5_train_como.sh
```


## Inference
You should put the audios you want to convert under the `raw` directory firstly.

### Inference by the Teacher Model

```shell
python inference_main.py -ts 50 -tm "logs/teacher/model_800000.pt" -tc "logs/teacher/config.yaml" -n "src.wav" -k 0 -s "target_singer"
```
-ts refers to the total number of iterative steps during inference for the teacher model

-tm refers to the teacher_model_path

-tc refers to the teacher_config_path

-n refers to the source audio

-k refers to the pitch shift, it can be positive and negative (semitone) values

-s refers to the target singer

### Inference by the Consistency Model

```shell
python inference_main.py -ts 1 -cm "logs/como/model_800000.pt" -cc "logs/como/config.yaml" -n "src.wav" -k 0 -s "target_singer" -t
```
-ts refers to the total number of iterative steps during inference for the student model

-cm refers to the como_model_path

-cc refers to the como_config_path

-t means it is not the teacher model and you don't need to specify anything after it 
