# BFC comming soon
Energy-efficient Brain-like Forgetting computing via tunable relaxation for linear-time scientific solving and training-free creativity

## 🌤️ Highlights
- 🏆 Collected and curated the largest medical image segmentation dataset (4.6M images and 19.7M masks) to date for training models.
- 🏆 The most comprehensive fine-tuning based on Segment Anything Model (SAM).
- 🏆 Comprehensive evaluation of SAM-Med2D on large-scale datasets.

## 🔥 Updates
- (2023.12.05) We open the download of the dataset on the [Hugging Face](https://huggingface.co/datasets/OpenGVLab/SA-Med2D-20M) platform 
- (2023.11.23) We have released the [SA-Med2D-20M](https://openxlab.org.cn/datasets/GMAI/SA-Med2D-20M) dataset 
- (2023.11.21) We have released article introducing the [SA-Med2D-20M](https://arxiv.org/abs/2311.11969) dataset 
- (2023.10.24) We now released [SAM-Med3D](https://github.com/uni-medical/SAM-Med3D), which focus on segmentation of 3D medical imaging
- (2023.09.14) Train code release
- (2023.09.02) Test code release
- (2023.08.31) Pre-trained model release
- (2023.08.31) Paper release
- (2023.08.26) Online Demo release

## 👉 Dataset
SAM-Med2D is trained and tested on a dataset that includes **4.6M images** and **19.7M masks**. This dataset covers 10 medical data modalities, 4 anatomical structures + lesions, and 31 major human organs. To our knowledge, this is currently the largest and most diverse medical image segmentation dataset in terms of quantity and coverage of categories.
<p align="center"><img width="800" alt="image" src="https://github.com/OpenGVLab/SAM-Med2D/blob/main/assets/dataset.png"></p> 

## 👉 Framework
The pipeline of SAM-Med2D. We freeze the image encoder and incorporate learnable adapter layers in each Transformer block to acquire domain-specific knowledge in the medical field. We fine-tune the prompt encoder using point, Bbox, and mask information, while updating the parameters of the mask decoder through interactive training.
<p align="center"><img width="800" alt="image" src="https://github.com/OpenGVLab/SAM-Med2D/blob/main/assets/framwork.png"></p> 



## 👉 Visualization
<p align="center"><img width="800" alt="image" src="https://github.com/OpenGVLab/SAM-Med2D/blob/main/assets/visualization.png"></p> 

## 👉 Train
Prepare your own dataset and refer to the samples in `SAM-Med2D/data_demo` to replace them according to your specific scenario. You need to generate the `image2label_train.json` file before running `train.py`.

If you want to use mixed-precision training, please install [Apex](https://github.com/NVIDIA/apex). If you don't want to install Apex, you can comment out the line `from apex import amp` and set `use_amp` to False.

```bash
cd ./SAM-Med2D
python train.py
```
- work_dir: Specifies the working directory for the training process. Default value is `workdir`.
- image_size: Default value is 256.
- mask_num: Specify the number of masks corresponding to one image, with a default value of 5.
- data_path: Dataset directory, for example: `data_demo`.
- resume: Pretrained weight file, ignore `sam_checkpoint` if present.
- sam_checkpoint: Load sam checkpoint.
- iter_point: Mask decoder iterative runs.
- multimask: Determines whether to output multiple masks. Default value is True.
- encoder_adapter: Whether to fine-tune the Adapter layer, set to False only for fine-tuning the decoder.
- use_amp: Set whether to use mixed-precision training.

## 👉 Test
Prepare your own dataset and refer to the samples in `SAM-Med2D/data_demo` to replace them according to your specific scenario. You need to generate the `label2image_test.json` file before running `test.py`.

```bash
cd ./SAM-Med2D
python test.py
```
- work_dir: Specifies the working directory for the testing process. Default value is `workdir`.
- batch_size: 1.
- image_size: Default value is 256.
- boxes_prompt: Use Bbox prompt to get segmentation results. 
- point_num: Specifies the number of points. Default value is 1.
- iter_point: Specifies the number of iterations for point prompts.
- sam_checkpoint: Load sam or sammed checkpoint.
- encoder_adapter: Set to True if using SAM-Med2D's pretrained weights.
- save_pred: Whether to save the prediction results.
- prompt_path: Is there a fixed Prompt file? If not, the value is None, and it will be automatically generated in the latest prediction.


```
