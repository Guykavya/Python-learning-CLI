# Chapter 3 (ML): Computer Vision

In ml.02 you learned the PyTorch machinery and met one convolutional layer. This chapter is about **images**: how a computer sees them, why convolutional networks are built the way they are, how to make a small dataset behave like a big one (**augmentation**), and how to start from someone else's trained network instead of from random weights (**transfer learning**). Almost every real vision job today (reading X-rays, sorting products, finding defects on a production line, checking photos) is a fine-tuned pretrained network, so the last part of the chapter is the one you will use most.

You will learn **images as tensors** (shapes, channels, normalisation), **convolution in depth** (output sizes, parameter counts, receptive fields, 1x1 and depthwise convolutions), **pooling and normalisation**, **architectures** (a plain CNN, a VGG-style block, and the residual block that made very deep networks trainable), **data augmentation** (what is safe, what silently breaks labels, mixup, test-time augmentation), **looking inside a network** (filters, feature maps, Grad-CAM written by hand), and **transfer learning** (feature extraction, fine-tuning, discriminative learning rates, the batch-norm trap). The syllabus outcome is: **fine-tune a pretrained model on a small custom dataset.** The chapter ends with a project that does exactly that, from PNG files on disk to a validated predictor.

Prerequisites: ml.01 (backpropagation, batch norm, regularisation), ml.02 (tensors, `nn.Module`, `DataLoader`, the training loop, saving and loading), ds.04 (honest evaluation).

> **Offline rule for this chapter.** Everything runs with no internet on the **CPU build** of PyTorch (2.15). `torchvision` is **not installed** and there are no downloadable pretrained weights offline, so:
> - the image data are the 8x8 digit images bundled with scikit-learn, plus PNG files we write to a temporary folder ourselves (Pillow is installed);
> - the "pretrained network" in the transfer-learning sections is one **we pretrain ourselves** on a large source task and then adapt to a small, different target task. The mechanics (freezing, learning rates, batch-norm, replacing the head) are exactly the ones used with ImageNet models;
> - code that needs `torchvision` (`transforms`, `models.resnet18(weights=...)`) is shown as *On your machine* with **no invented output**.
>
> Every output block below was produced by running the code above it, in one session from top to bottom. Timings and exact accuracies are machine-specific (the seeds are fixed, so you should get close numbers, not necessarily identical ones).

```python run
import sys, math, time, os, io, copy, pathlib, tempfile, warnings, platform
import numpy as np
import pandas as pd
import sklearn
from sklearn import datasets, model_selection
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset

warnings.filterwarnings("ignore")
np.set_printoptions(precision=4, suppress=True, linewidth=120)
pd.set_option("display.width", 130)
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, "| pillow", Image.__version__)
print("torch  ", torch.__version__, "| CUDA available:", torch.cuda.is_available(), "| threads:", torch.get_num_threads())
```
```text
python  3.14.4
numpy   2.5.4 | pillow 13.0.0
torch   2.15.0+cpu | CUDA available: False | threads: 6
```

## Table of contents

1. [Images as tensors](#1-images-as-tensors)
2. [Convolution in depth](#2-convolution-in-depth)
3. [Pooling, normalisation and seeing the shapes](#3-pooling-normalisation-and-seeing-the-shapes)
4. [Architectures: plain, VGG-style and residual](#4-architectures-plain-vgg-style-and-residual)
5. [Training a CNN and reading its curves](#5-training-a-cnn-and-reading-its-curves)
6. [Data augmentation](#6-data-augmentation)
7. [Looking inside a network](#7-looking-inside-a-network)
8. [Transfer learning](#8-transfer-learning)
9. [Project: a fine-tuned classifier for a custom dataset](#9-project-a-fine-tuned-classifier-for-a-custom-dataset)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. Images as tensors

### 1.1 Pixels, channels and the `(N, C, H, W)` layout

A grayscale image is a grid of numbers, one per pixel: brightness. A colour image has **three grids** (red, green, blue), called **channels**. A batch of images stacks many of them. PyTorch's convention is

```
(N, C, H, W)   =   (batch, channels, height, width)
```

This is **channels first**. Pillow, NumPy images, Matplotlib and OpenCV use **channels last**, `(H, W, C)`. Converting between the two is the most common source of a model that "runs but learns nothing", because a wrongly ordered tensor still has *a* valid shape for some layer.

```python run
digits = datasets.load_digits()
print("raw array:", digits.images.shape, digits.images.dtype, "| value range", digits.images.min(), "to", digits.images.max())
one = digits.images[0]
print("one image, shape", one.shape, "(H, W). It is a", digits.target[0])
for row in one.astype(int):
    print(" ".join(f"{v:2d}" for v in row))

# build a fake colour image to practise the layouts
rgb_hwc = np.random.default_rng(0).integers(0, 256, size=(4, 6, 3), dtype=np.uint8)     # (H, W, C), like Pillow gives
chw = torch.from_numpy(rgb_hwc).permute(2, 0, 1)                                         # (C, H, W), like PyTorch wants
batch = chw[None].float()                                                                # (1, C, H, W)
print("HWC", rgb_hwc.shape, "-> CHW", tuple(chw.shape), "-> NCHW", tuple(batch.shape))
print("permute does not copy the data; it is just a different view of it:", chw.is_contiguous())
```
```text
raw array: (1797, 8, 8) float64 | value range 0.0 to 16.0
one image, shape (8, 8) (H, W). It is a 0
 0  0  5 13  9  1  0  0
 0  0 13 15 10 15  5  0
 0  3 15  2  0 11  8  0
 0  4 12  0  0  8  8  0
 0  5  8  0  0  9  8  0
 0  4 11  0  1 12  7  0
 0  2 14  5 10 12  0  0
 0  0  6 13 10  0  0  0
HWC (4, 6, 3) -> CHW (3, 4, 6) -> NCHW (1, 3, 4, 6)
permute does not copy the data; it is just a different view of it: False
```

> **Predict the output.** What does `chw.is_contiguous()` print above, and what does that mean for `chw.view(-1)`?

<details><summary>Answer</summary>

It prints `False`. `permute` returns a *view* with changed strides, so the memory order is still H, W, C. `chw.view(-1)` would raise an error because `view` needs contiguous memory; use `chw.reshape(-1)` or `chw.contiguous().view(-1)`, which copy.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw how a PyTorch image tensor is laid out. Show a colour image of height 4 and width 6 as three stacked 4x6 grids labelled R, G, B, giving shape (C, H, W) = (3, 4, 6). Then show a batch of one: (N, C, H, W) = (1, 3, 4, 6). Next to it show the channels-last layout (H, W, C) = (4, 6, 3) used by Pillow and NumPy, with arrows labelled 'permute(2, 0, 1)' between them."

### 1.2 Scaling and normalising

Pixels arrive as integers 0..255 (or 0..16 in the digits). A network wants small numbers centred near zero, for the same reasons you met in ml.01 (initialisation and gradient sizes). Two steps:

1. **Scale** to `[0, 1]`: divide by the maximum.
2. **Standardise**: subtract a mean and divide by a standard deviation, per channel.

The golden rule from ds.04 applies: **compute the mean and standard deviation from the training images only.** Computing them on all the data lets information about the test set leak into the model. Pretrained ImageNet models were trained with specific statistics (mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`); when you reuse such a model you **must** use *its* statistics, not your own.

```python run
X_all, y_all = digits.data / 16.0, digits.target
# a stratified split keeps the class proportions in every part
X_dev, X_te, y_dev, y_te = model_selection.train_test_split(X_all, y_all, test_size=0.25, random_state=0, stratify=y_all)
X_tr, X_va, y_tr, y_va = model_selection.train_test_split(X_dev, y_dev, test_size=0.25, random_state=0, stratify=y_dev)
mean, std = X_tr.mean(), X_tr.std()                      # TRAINING images only
to_img = lambda A: torch.tensor(((A - mean) / std).reshape(-1, 1, 8, 8), dtype=torch.float32)
Xtr, Xva, Xte = to_img(X_tr), to_img(X_va), to_img(X_te)
ytr, yva, yte = map(torch.tensor, (y_tr, y_va, y_te))
print("train/val/test sizes:", len(ytr), len(yva), len(yte))
print(f"train mean {Xtr.mean():+.3f}  std {Xtr.std():.3f}   |   test mean {Xte.mean():+.3f}  std {Xte.std():.3f}  (close to, but not exactly, 0 and 1: that is normal)")
print("class counts in train:", np.bincount(y_tr).tolist())
```
```text
train/val/test sizes: 1010 337 450
train mean +0.000  std 1.000   |   test mean -0.002  std 1.000  (close to, but not exactly, 0 and 1: that is normal)
class counts in train: [100, 102, 100, 103, 102, 102, 102, 100, 98, 101]
```

### 1.3 Reading and writing real image files

Real datasets are files. With Pillow you open a file, convert it to the mode you want (`"L"` = one grayscale channel, `"RGB"` = three), and turn it into an array. A very common bug is a mix of modes in one folder (a few PNGs with an alpha channel, a few grayscale): always call `.convert(...)`.

```python run
tmp = pathlib.Path(tempfile.mkdtemp())
arr = (digits.images[3][:, :6] / 16 * 255).astype(np.uint8)          # deliberately not square: 8 rows, 6 columns
Image.fromarray(arr, mode="L").save(tmp / "three.png")
im = Image.open(tmp / "three.png")
print("opened:", im.size, "(width, height) | mode", im.mode, "| format", im.format)
back = np.asarray(im.convert("L"))
print("round trip is lossless for PNG:", np.array_equal(back, arr), "| array shape", back.shape, "(H, W)")
rgb = im.convert("RGB")
print("converted to RGB:", np.asarray(rgb).shape, "-> the one grey channel was copied three times")
print("size is (W, H) in Pillow but the array is (H, W):", im.size, "vs", back.shape)
```
```text
opened: (6, 8) (width, height) | mode L | format PNG
round trip is lossless for PNG: True | array shape (8, 6) (H, W)
converted to RGB: (8, 6, 3) -> the one grey channel was copied three times
size is (W, H) in Pillow but the array is (H, W): (6, 8) vs (8, 6)
```

### 1.4 Try it

1. A batch of 32 RGB images, 224 pixels square, is a tensor of what shape? How many numbers is that, and how many megabytes as `float32`?
2. Why is it wrong to compute the mean and standard deviation over the whole dataset before splitting?

## 2. Convolution in depth

### 2.1 What a convolutional layer computes

You met the idea in ml.02: slide a small grid of weights, a **filter** or **kernel**, over the image and compute a weighted sum at every position. Here is the full picture with several channels.

A `Conv2d(in_channels=C_in, out_channels=C_out, kernel_size=k)` layer holds `C_out` filters. Each filter is a block of shape `(C_in, k, k)`: it looks at **all** input channels at once over a `k x k` window and produces **one** output channel. So the weight tensor has shape `(C_out, C_in, k, k)`, plus one bias per output channel:

```
parameters = C_out x (C_in x k x k) + C_out
```

The output size along one spatial dimension is

```
out = floor( (in + 2*padding - dilation*(k-1) - 1) / stride ) + 1
```

(with `dilation = 1` this is the formula from ml.02: `floor((in + 2p - k)/s) + 1`).

```python run
conv = nn.Conv2d(in_channels=3, out_channels=8, kernel_size=3, padding=1)
print("weight shape (C_out, C_in, k, k):", tuple(conv.weight.shape), "| bias shape:", tuple(conv.bias.shape))
print("parameters:", sum(p.numel() for p in conv.parameters()), "= 8 x (3x3x3) + 8 =", 8 * 27 + 8)

def out_size(n, k, p=0, s=1, d=1):
    return (n + 2 * p - d * (k - 1) - 1) // s + 1

x = torch.randn(2, 3, 32, 32)
print(f"{'k':>2} {'p':>2} {'s':>2} {'d':>2} | formula | PyTorch")
for k, p, s, d in [(3, 0, 1, 1), (3, 1, 1, 1), (3, 1, 2, 1), (5, 2, 1, 1), (7, 3, 2, 1), (3, 2, 1, 2), (1, 0, 1, 1)]:
    got = nn.Conv2d(3, 4, k, stride=s, padding=p, dilation=d)(x).shape[-1]
    print(f"{k:>2} {p:>2} {s:>2} {d:>2} | {out_size(32, k, p, s, d):>7} | {got:>7}")
```
```text
weight shape (C_out, C_in, k, k): (8, 3, 3, 3) | bias shape: (8,)
parameters: 224 = 8 x (3x3x3) + 8 = 224
 k  p  s  d | formula | PyTorch
 3  0  1  1 |      30 |      30
 3  1  1  1 |      32 |      32
 3  1  2  1 |      16 |      16
 5  2  1  1 |      32 |      32
 7  3  2  1 |      16 |      16
 3  2  1  2 |      32 |      32
 1  0  1  1 |      32 |      32
```

A useful rule: with an odd kernel `k`, stride 1 and padding `(k-1)//2` (called "same" padding) the height and width do not change. That is why `k=3, p=1` and `k=5, p=2` are everywhere.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a Conv2d layer with in_channels=3, out_channels=8, kernel_size=3, padding=1 on an input of shape (3, 32, 32). Show one filter as a (3, 3, 3) block sliding over the zero-padded input, producing one 32x32 output channel at each stop. Show that 8 such filters give an output of (8, 32, 32), and label the weight tensor shape (8, 3, 3, 3) and the 224 parameters (8 x 27 + 8)."

### 2.2 A multi-channel convolution written by hand

To be sure you understand the shapes, write it with loops and let PyTorch referee.

```python run
def conv2d_naive(x, weight, bias, padding=0, stride=1):
    """x: (N, C_in, H, W); weight: (C_out, C_in, k, k); bias: (C_out,). Plain loops, no tricks."""
    N, C_in, H, W = x.shape
    C_out, _, k, _ = weight.shape
    xp = F.pad(x, (padding,) * 4)
    H_out, W_out = (H + 2 * padding - k) // stride + 1, (W + 2 * padding - k) // stride + 1
    out = torch.zeros(N, C_out, H_out, W_out)
    for n in range(N):
        for co in range(C_out):
            for i in range(H_out):
                for j in range(W_out):
                    window = xp[n, :, i * stride:i * stride + k, j * stride:j * stride + k]      # (C_in, k, k): ALL channels
                    out[n, co, i, j] = (window * weight[co]).sum() + bias[co]
    return out

torch.manual_seed(0)
x = torch.randn(2, 3, 7, 7)
layer = nn.Conv2d(3, 4, 3, padding=1, stride=2)
ours = conv2d_naive(x, layer.weight.detach(), layer.bias.detach(), padding=1, stride=2)
print("our output shape", tuple(ours.shape), "| PyTorch", tuple(layer(x).shape))
print("hand-written loops equal nn.Conv2d:", bool(torch.allclose(ours, layer(x), atol=1e-5)))
```
```text
our output shape (2, 4, 4, 4) | PyTorch (2, 4, 4, 4)
hand-written loops equal nn.Conv2d: True
```

Two details worth keeping. First, PyTorch's "convolution" is really **cross-correlation** (the kernel is not flipped); since the weights are learned, nobody cares. Second, *each output channel mixes all input channels*: a `Conv2d(64, 128, 3)` filter has `64 x 3 x 3 = 576` weights.

### 2.3 Why convolutions beat fully connected layers: three properties

```python run
# 1. Few parameters, independent of the image size
for size in (8, 32, 224):
    fc = size * size * 16                      # a Linear layer from one channel's pixels to 16 maps the same size
    cv = 16 * (1 * 3 * 3) + 16
    print(f"image {size:>3}x{size:<3}: Linear to 16 maps of the same size = {fc:>9,} weights | Conv2d(1->16, k=3) = {cv} weights")

# 2. Translation equivariance: shift the input, the output shifts the same way
torch.manual_seed(0)
c = nn.Conv2d(1, 4, 3, padding=0, bias=False)
img = torch.zeros(1, 1, 10, 10); img[0, 0, 2:5, 2:4] = torch.rand(3, 2)              # a small blob near the top-left
moved = torch.roll(img, shifts=(3, 4), dims=(2, 3))                                  # same blob 3 down, 4 right
a, b = c(img), c(moved)
print("conv(shifted image) == shifted conv(image) (blob far from the borders):", bool(torch.allclose(torch.roll(a, (3, 4), (2, 3)), b, atol=1e-6)))

# 3. Local connectivity: one output pixel only sees a small window of the input
x = torch.randn(1, 1, 10, 10, requires_grad=True)
c(x)[0, 0, 4, 4].backward()
rows, cols = (x.grad[0, 0] != 0).nonzero().T
print("output pixel (4,4) depends on input rows", rows.min().item(), "to", rows.max().item(), "and cols", cols.min().item(), "to", cols.max().item(), "(a 3x3 window)")
```
```text
image   8x8  : Linear to 16 maps of the same size =     1,024 weights | Conv2d(1->16, k=3) = 160 weights
image  32x32 : Linear to 16 maps of the same size =    16,384 weights | Conv2d(1->16, k=3) = 160 weights
image 224x224: Linear to 16 maps of the same size =   802,816 weights | Conv2d(1->16, k=3) = 160 weights
conv(shifted image) == shifted conv(image) (blob far from the borders): True
output pixel (4,4) depends on input rows 4 to 6 and cols 4 to 6 (a 3x3 window)
```

Equivariance means the same pattern gets the same response wherever it is. Combined with pooling at the end it becomes (approximate) **invariance**: "there is a 7 in this picture" no matter where. This is the structural reason a CNN needs fewer examples than a fully connected network on images.

### 2.4 The receptive field

The **receptive field** of an output unit is the region of the *input* that can influence it. One `3x3` convolution gives 3x3. Stack two: the second layer's unit sees a 3x3 window of first-layer units, each of which sees 3x3 pixels, so the total is 5x5. Pooling and stride make it grow faster. The recurrence, going layer by layer, with `jump` = distance between neighbouring units measured in input pixels:

```
rf_new   = rf   + (k - 1) * jump
jump_new = jump * stride
```

You can *measure* it with autograd, exactly like the check above: set the input's gradient to track, backpropagate from the centre output unit, and count the input pixels with non-zero gradient.

```python run
def receptive_field_formula(layers):
    rf, jump = 1, 1
    for k, s in layers:
        rf += (k - 1) * jump
        jump *= s
    return rf

def receptive_field_measured(model, size=65):
    x = torch.randn(1, 1, size, size, requires_grad=True)
    out = model(x)
    out[0, 0, out.shape[2] // 2, out.shape[3] // 2].backward()
    touched = (x.grad[0, 0].abs() > 0)
    return int(touched.any(dim=0).sum())                                  # width of the touched region

stacks = {
    "3x3":                             ([(3, 1)],                                 nn.Sequential(nn.Conv2d(1, 1, 3))),
    "3x3, 3x3":                        ([(3, 1), (3, 1)],                         nn.Sequential(nn.Conv2d(1, 1, 3), nn.Conv2d(1, 1, 3))),
    "3x3 x3 (VGG idea)":               ([(3, 1)] * 3,                             nn.Sequential(*[nn.Conv2d(1, 1, 3) for _ in range(3)])),
    "3x3, avgpool2, 3x3":                ([(3, 1), (2, 2), (3, 1)],                 nn.Sequential(nn.Conv2d(1, 1, 3), nn.AvgPool2d(2), nn.Conv2d(1, 1, 3))),
    "3x3 stride2, 3x3 stride2, 3x3":   ([(3, 2), (3, 2), (3, 1)],                 nn.Sequential(nn.Conv2d(1, 1, 3, stride=2), nn.Conv2d(1, 1, 3, stride=2), nn.Conv2d(1, 1, 3))),
}
for name, (spec, model) in stacks.items():
    print(f"{name:<32} formula {receptive_field_formula(spec):>3} | measured {receptive_field_measured(model):>3}")
print("\nweights: one 5x5 conv (C->C) =", 25, "x C^2 | two 3x3 convs (same 5x5 view) =", 18, "x C^2  -> deeper stacks of small kernels see the same area with fewer weights")
```
```text
3x3                              formula   3 | measured   3
3x3, 3x3                         formula   5 | measured   5
3x3 x3 (VGG idea)                formula   7 | measured   7
3x3, avgpool2, 3x3               formula   8 | measured   8
3x3 stride2, 3x3 stride2, 3x3    formula  15 | measured  15

weights: one 5x5 conv (C->C) = 25 x C^2 | two 3x3 convs (same 5x5 view) = 18 x C^2  -> deeper stacks of small kernels see the same area with fewer weights
```

One caution: with **max** pooling the measured region can be *smaller* than the formula says, because the gradient flows back only to the single pixel that won the max in each window (try it with `nn.MaxPool2d(2)`: you get 7 instead of 8 for the stack above). The formula gives the region that *can* influence the unit; max pooling picks one pixel of it per window for any particular input. That is why this check uses average pooling.

This is why modern networks use `3x3` almost exclusively: two `3x3` layers see the same `5x5` area as one `5x5` layer with `18/25` of the weights, *and* have an extra non-linearity between them.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the receptive field of a stack of 3x3 convolutions (stride 1, no pooling). Show three layers as grids. Pick one unit in layer 3 and highlight the 3x3 patch it reads in layer 2, then the 5x5 patch in layer 1, then the 7x7 patch of the input image. Label the receptive field growing 3, 5, 7 using rf_new = rf + (k - 1) * jump with jump = 1."

### 2.5 1x1 convolutions and depthwise convolutions

A `1x1` convolution looks at no neighbours at all: at each pixel it mixes the channels with a small matrix multiplication. It is used to **change the number of channels cheaply** (the "bottleneck" in ResNets). A **depthwise** convolution (`groups=C`) gives each channel its own `k x k` filter and does no mixing; a **depthwise-separable** convolution is a depthwise one followed by a `1x1` that mixes, and is the building block of mobile networks.

```python run
C_in, C_out, k = 64, 128, 3
regular = nn.Conv2d(C_in, C_out, k, padding=1)
depthwise = nn.Conv2d(C_in, C_in, k, padding=1, groups=C_in)
pointwise = nn.Conv2d(C_in, C_out, 1)
count = lambda *ms: sum(p.numel() for m in ms for p in m.parameters())
print("regular 3x3   64->128:", count(regular), "parameters")
print("depthwise 3x3 + pointwise 1x1:", count(depthwise, pointwise), "parameters  (", round(count(regular) / count(depthwise, pointwise), 1), "x fewer )")
x = torch.randn(1, 64, 16, 16)
print("both give the same output shape:", tuple(regular(x).shape), tuple(pointwise(depthwise(x)).shape))

# a 1x1 convolution IS a Linear layer applied at every pixel
lin = nn.Linear(C_in, C_out)
pw = nn.Conv2d(C_in, C_out, 1)
pw.weight.data = lin.weight.data[:, :, None, None].clone(); pw.bias.data = lin.bias.data.clone()
as_linear = lin(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)
print("1x1 conv equals a Linear layer applied per pixel:", bool(torch.allclose(pw(x), as_linear, atol=1e-5)))
```
```text
regular 3x3   64->128: 73856 parameters
depthwise 3x3 + pointwise 1x1: 8960 parameters  ( 8.2 x fewer )
both give the same output shape: (1, 128, 16, 16) (1, 128, 16, 16)
1x1 conv equals a Linear layer applied per pixel: True
```

### 2.6 Try it

1. A `Conv2d(16, 32, kernel_size=5, padding=2)` is applied to a `(8, 16, 40, 40)` tensor. What is the output shape and how many parameters does the layer have?
2. A network has convolutions `3x3 stride 1`, `3x3 stride 2`, `3x3 stride 1`. Use the recurrence to compute the receptive field. Then verify with `receptive_field_measured`.
3. Why can a `Conv2d(1, 16, 3)` run on a `10x10` image but a `Conv2d(1, 16, 11)` not (without padding)?

## 3. Pooling, normalisation and seeing the shapes

### 3.1 Pooling shrinks the map

**Max pooling** (`MaxPool2d(2)`) takes the largest value in each `2x2` window, halving height and width; it keeps "was the feature found here?" and discards the exact position, which adds a little robustness to small shifts. **Average pooling** takes the mean. **Global average pooling** (`AdaptiveAvgPool2d(1)`) averages the *whole* map of each channel into one number, so the network no longer cares about the input size, and the final `Linear` has only `C` inputs instead of `C x H x W`.

```python run
x = torch.tensor([[[[1., 2., 5., 0.],
                    [3., 4., 1., 1.],
                    [0., 0., 9., 2.],
                    [1., 2., 3., 4.]]]])
print("input\n", x[0, 0])
print("MaxPool2d(2)\n", nn.MaxPool2d(2)(x)[0, 0])
print("AvgPool2d(2)\n", nn.AvgPool2d(2)(x)[0, 0])
print("global average pool:", nn.AdaptiveAvgPool2d(1)(x).flatten().item(), "= mean of all 16 values =", x.mean().item())
# the same global-pool + Linear head works for any input size
head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(8, 3))
for s in (8, 16, 33):
    print(f"feature map 8 x {s} x {s} -> head output {tuple(head(torch.randn(2, 8, s, s)).shape)}")
```
```text
input
 tensor([[1., 2., 5., 0.],
        [3., 4., 1., 1.],
        [0., 0., 9., 2.],
        [1., 2., 3., 4.]])
MaxPool2d(2)
 tensor([[4., 5.],
        [2., 9.]])
AvgPool2d(2)
 tensor([[2.5000, 1.7500],
        [0.7500, 4.5000]])
global average pool: 2.375 = mean of all 16 values = 2.375
feature map 8 x 8 x 8 -> head output (2, 3)
feature map 8 x 16 x 16 -> head output (2, 3)
feature map 8 x 33 x 33 -> head output (2, 3)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw this 4x4 grid of numbers (rows: 1 2 5 0 / 3 4 1 1 / 0 0 9 2 / 1 2 3 4), split into four coloured 2x2 windows. Beside it draw the MaxPool2d(2) result [[4, 5], [2, 9]] and the AvgPool2d(2) result [[2.5, 1.75], [0.75, 4.5]], with arrows from each window. Then show global average pooling collapsing all 16 values into one number, 2.375."

### 3.2 Batch normalisation for images

`BatchNorm2d(C)` normalises **each channel** over the batch and both spatial dimensions, then applies a learned scale and shift. It has two modes (you met this in ml.01 and ml.02, and it matters again in section 8):

- **train mode**: uses the statistics of the current batch and updates running averages;
- **eval mode**: uses the stored running averages.

```python run
torch.manual_seed(0)
bn = nn.BatchNorm2d(3)
x = torch.randn(16, 3, 8, 8) * torch.tensor([1.0, 5.0, 0.2]).view(1, 3, 1, 1) + torch.tensor([0.0, 10.0, -3.0]).view(1, 3, 1, 1)
print("input channel means:", x.mean(dim=(0, 2, 3)).numpy().round(2), "stds:", x.std(dim=(0, 2, 3)).numpy().round(2))
y = bn(x).detach()
print("train-mode output  :", y.mean(dim=(0, 2, 3)).numpy().round(3), "stds:", y.std(dim=(0, 2, 3)).numpy().round(2))
print("running_mean after one batch:", bn.running_mean.numpy().round(3), "(moved 10% of the way: momentum = 0.1)")
bn.eval()
y2 = bn(x).detach()
print("eval-mode output means    :", y2.mean(dim=(0, 2, 3)).numpy().round(2), "<- NOT normalised: running stats have barely moved from 0 and 1")
print("parameters:", [n for n, _ in bn.named_parameters()], "| buffers:", [n for n, _ in bn.named_buffers()])
```
```text
input channel means: [ 0.02  9.83 -3.  ] stds: [1.03 4.96 0.2 ]
train-mode output  : [ 0.  0. -0.] stds: [1. 1. 1.]
running_mean after one batch: [ 0.002  0.983 -0.3  ] (moved 10% of the way: momentum = 0.1)
eval-mode output means    : [ 0.02  4.83 -2.84] <- NOT normalised: running stats have barely moved from 0 and 1
parameters: ['weight', 'bias'] | buffers: ['running_mean', 'running_var', 'num_batches_tracked']
```

The last line is the point to remember: `weight` and `bias` are learned **parameters**; `running_mean`, `running_var` and `num_batches_tracked` are **buffers**: saved in `state_dict`, moved with `.to(device)`, but *not* touched by the optimiser. Freezing a layer with `requires_grad=False` therefore does **not** stop its running statistics from changing. We will hit this in section 8.

### 3.3 A shape tracker

When a CNN fails with `mat1 and mat2 shapes cannot be multiplied`, you want to see every layer's output shape. Forward hooks give you that in a dozen lines. This tool is worth keeping.

```python run
def shape_table(model, x):
    rows, hooks = [], []
    for name, mod in model.named_modules():
        if not list(mod.children()):                                         # leaf layers only
            hooks.append(mod.register_forward_hook(lambda m, i, o, name=name: rows.append((name, type(m).__name__, tuple(o.shape)))))
    was_training = model.training
    model.eval()
    with torch.no_grad(): model(x)
    model.train(was_training)
    for h in hooks: h.remove()
    return pd.DataFrame(rows, columns=["layer", "type", "output shape"])

demo = nn.Sequential(
    nn.Conv2d(1, 8, 3, padding=1), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
    nn.Flatten(), nn.Linear(16, 10))
print(shape_table(demo, torch.randn(4, 1, 8, 8)).to_string(index=False))
```
```text
layer              type  output shape
    0            Conv2d  (4, 8, 8, 8)
    1       BatchNorm2d  (4, 8, 8, 8)
    2              ReLU  (4, 8, 8, 8)
    3         MaxPool2d  (4, 8, 4, 4)
    4            Conv2d (4, 16, 4, 4)
    5       BatchNorm2d (4, 16, 4, 4)
    6              ReLU (4, 16, 4, 4)
    7 AdaptiveAvgPool2d (4, 16, 1, 1)
    8           Flatten       (4, 16)
    9            Linear       (4, 10)
```

### 3.4 Try it

1. Without running it: what is the output of `nn.MaxPool2d(2)` on a `(1, 3, 7, 7)` tensor? (Hint: pooling floors.) Check with PyTorch.
2. Why does `BatchNorm2d(16)` have exactly `32` parameters, and how many numbers does it keep in buffers?

## 4. Architectures: plain, VGG-style and residual

### 4.1 The standard recipe

Nearly every image classifier has the same three-part shape:

```
image -> [ conv block -> conv block -> ... ] -> global pool -> Linear -> class scores
          \________ feature extractor ________/               \__ head __/
```

A **conv block** is `Conv2d -> BatchNorm2d -> ReLU` (optionally followed by a pool). As you go deeper, spatial size **shrinks** (pooling or stride) and the channel count **grows** (16, 32, 64, ...): the network trades "where" for "what". The feature extractor turns pixels into a vector of features; the head turns that vector into class scores. This split matters in section 8: transfer learning keeps the extractor and replaces the head.

```python run
def conv_block(c_in, c_out, pool=False):
    layers = [nn.Conv2d(c_in, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU()]       # bias=False: BatchNorm's shift replaces it
    if pool: layers.append(nn.MaxPool2d(2))
    return nn.Sequential(*layers)

class SmallCNN(nn.Module):
    """features: two conv blocks; head: global average pooling + Linear."""
    def __init__(self, n_classes=10, channels=(16, 32), dropout=0.0):
        super().__init__()
        c1, c2 = channels
        self.features = nn.Sequential(conv_block(1, c1, pool=True), conv_block(c1, c2))              # 8x8 -> 4x4, then 4x4 stays
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(dropout), nn.Linear(c2, n_classes))
    def forward(self, x): return self.head(self.features(x))

torch.manual_seed(0)
net = SmallCNN()
print(shape_table(net, torch.randn(2, 1, 8, 8)).to_string(index=False))
print("parameters:", sum(p.numel() for p in net.parameters()), "| features:", sum(p.numel() for p in net.features.parameters()), "| head:", sum(p.numel() for p in net.head.parameters()))
```
```text
       layer              type  output shape
features.0.0            Conv2d (2, 16, 8, 8)
features.0.1       BatchNorm2d (2, 16, 8, 8)
features.0.2              ReLU (2, 16, 8, 8)
features.0.3         MaxPool2d (2, 16, 4, 4)
features.1.0            Conv2d (2, 32, 4, 4)
features.1.1       BatchNorm2d (2, 32, 4, 4)
features.1.2              ReLU (2, 32, 4, 4)
      head.0 AdaptiveAvgPool2d (2, 32, 1, 1)
      head.1           Flatten       (2, 32)
      head.2           Dropout       (2, 32)
      head.3            Linear       (2, 10)
parameters: 5178 | features: 4848 | head: 330
```

Notice `bias=False` in the convolution: a bias followed by batch norm is wasted, because batch norm subtracts the mean and adds its own shift.

### 4.2 The VGG idea: stack small kernels

The VGG family (2014) showed that you do not need clever kernels: repeat `[3x3 conv, 3x3 conv, pool]`, doubling channels after every pool. As section 2.4 showed, two `3x3` convs see a `5x5` area with fewer weights. The cost is memory and compute: the early, high-resolution layers are expensive.

```python run
def vgg_stage(c_in, c_out, n_convs=2):
    return nn.Sequential(*[conv_block(c_in if i == 0 else c_out, c_out) for i in range(n_convs)], nn.MaxPool2d(2))

vgg_like = nn.Sequential(vgg_stage(1, 8), vgg_stage(8, 16), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(16, 10))
print(shape_table(vgg_like, torch.randn(2, 1, 8, 8)).query("type in ['MaxPool2d', 'AdaptiveAvgPool2d', 'Linear']").to_string(index=False))
print("parameters:", sum(p.numel() for p in vgg_like.parameters()))
```
```text
layer              type  output shape
  0.2         MaxPool2d  (2, 8, 4, 4)
  1.2         MaxPool2d (2, 16, 2, 2)
    2 AdaptiveAvgPool2d (2, 16, 1, 1)
    4            Linear       (2, 10)
parameters: 4370
```

### 4.3 The residual block: why very deep networks needed a trick

Making a network deeper should never hurt (extra layers could just learn to do nothing), yet in practice plain deep stacks train *worse*: gradients shrink as they travel back through many layers (ml.01), and the optimiser struggles to learn "do nothing". The fix (ResNet, 2015) is a **skip connection**: the block outputs `x + F(x)` instead of `F(x)`, where `F` is a couple of convolutions.

```
 x ──────────────┐
 │               │ (identity: just copy x)
 conv-bn-relu    │
 conv-bn         │
 │               │
 └──── add ──────┘ ── relu ──> output = relu(x + F(x))
```

If a block has nothing useful to add, `F` only has to learn *zero*, which is easy. And in the backward pass the gradient has a direct path through the `+`: the derivative of `x + F(x)` with respect to `x` is `1 + F'(x)`, so it cannot vanish through that block.

```python run
class ResBlock(nn.Module):
    def __init__(self, c_in, c_out, stride=1):
        super().__init__()
        self.f = nn.Sequential(
            nn.Conv2d(c_in, c_out, 3, stride=stride, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU(),
            nn.Conv2d(c_out, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out))
        # when the shape changes, the shortcut needs a 1x1 conv so that x and F(x) can be added
        self.shortcut = nn.Identity() if (stride == 1 and c_in == c_out) else nn.Sequential(nn.Conv2d(c_in, c_out, 1, stride=stride, bias=False), nn.BatchNorm2d(c_out))
    def forward(self, x):
        return F.relu(self.shortcut(x) + self.f(x))

blk = ResBlock(16, 16)
x = torch.randn(4, 16, 8, 8)
print("same-shape block:", tuple(x.shape), "->", tuple(blk(x).shape))
down = ResBlock(16, 32, stride=2)
print("down-sampling block:", tuple(x.shape), "->", tuple(down(x).shape), "(shortcut uses a 1x1 stride-2 conv)")

# if F(x) is exactly zero, the block is (relu of) the identity: "do nothing" is easy to represent
for p in blk.f[-1].parameters(): nn.init.zeros_(p)
blk.eval()
print("with the last BatchNorm zeroed, block(x) == relu(x):", bool(torch.allclose(blk(x), F.relu(x))))
```
```text
same-shape block: (4, 16, 8, 8) -> (4, 16, 8, 8)
down-sampling block: (4, 16, 8, 8) -> (4, 32, 4, 4) (shortcut uses a 1x1 stride-2 conv)
with the last BatchNorm zeroed, block(x) == relu(x): True
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a residual block as a flow diagram. The input x of shape (4, 16, 8, 8) splits in two: one path goes through conv-bn-relu then conv-bn (this is F(x)), the other is a skip connection carrying x unchanged. Both meet at an add node, then relu gives relu(x + F(x)). Show a second version for the down-sampling case, where the skip path has a 1x1 stride-2 conv so x becomes (4, 32, 4, 4). Mark the gradient path through the plus as 1 + F'(x)."

### 4.4 Evidence: gradients in a 30-layer network, plain against residual

A claim worth testing: build two networks with the same 30 layers, one plain and one with a skip around every layer, and compare the gradient reaching the **first** layer.

```python run
def make_deep(depth, residual, width=16):
    class Layer(nn.Module):
        def __init__(self):
            super().__init__(); self.lin = nn.Linear(width, width)
            nn.init.normal_(self.lin.weight, std=0.6 / math.sqrt(width))         # a smallish init, as can happen in a real net
        def forward(self, x):
            h = torch.tanh(self.lin(x))
            return x + h if residual else h
    return nn.Sequential(*[Layer() for _ in range(depth)])

torch.manual_seed(0)
x = torch.randn(64, 16)
rows = []
for depth in (5, 15, 30, 60):
    r = []
    for residual in (False, True):
        torch.manual_seed(1)
        net_d = make_deep(depth, residual)
        net_d(x).pow(2).mean().backward()
        r.append(net_d[0].lin.weight.grad.norm().item())
    rows.append([depth, *r])
print(pd.DataFrame(rows, columns=["depth", "plain: grad norm, layer 1", "residual: grad norm, layer 1"]).to_string(index=False, float_format=lambda v: f"{v:.2e}"))
```
```text
 depth  plain: grad norm, layer 1  residual: grad norm, layer 1
     5                   8.38e-03                      1.20e+00
    15                   1.70e-05                      3.32e+00
    30                   1.01e-08                      6.74e+00
    60                   1.46e-15                      2.43e+01
```

The plain network's gradient at layer 1 shrinks exponentially with depth (from 8e-3 to 1e-15); the residual network's does not shrink (it even grows, because this toy has no normalisation; real ResNets use batch norm). This is the experiment behind "residual connections make depth trainable". (We used `tanh` layers without normalisation to expose the effect; with batch norm the plain network's problem is milder, which is why VGG-style networks with batch norm train at all.)

### 4.5 A tiny ResNet and a parameter budget

```python run
class TinyResNet(nn.Module):
    def __init__(self, n_classes=10, widths=(16, 32), blocks_per_stage=1):
        super().__init__()
        w1, w2 = widths
        layers = [conv_block(1, w1)]
        layers += [ResBlock(w1, w1) for _ in range(blocks_per_stage)]
        layers += [ResBlock(w1, w2, stride=2)] + [ResBlock(w2, w2) for _ in range(blocks_per_stage - 1)]
        self.features = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(w2, n_classes))
    def forward(self, x): return self.head(self.features(x))

for name, m in [("SmallCNN", SmallCNN()), ("VGG-like", vgg_like), ("TinyResNet", TinyResNet()), ("TinyResNet x2 blocks", TinyResNet(blocks_per_stage=2))]:
    print(f"{name:<22} {sum(p.numel() for p in m.parameters()):>8,} parameters | output {tuple(m(torch.randn(2, 1, 8, 8)).shape)}")
```
```text
SmallCNN                  5,178 parameters | output (2, 10)
VGG-like                  4,370 parameters | output (2, 10)
TinyResNet               19,706 parameters | output (2, 10)
TinyResNet x2 blocks     42,938 parameters | output (2, 10)
```

### 4.6 Try it

1. A residual block with `stride=2` and `c_in=c_out`. Why does it still need a `1x1` shortcut convolution?
2. Count by hand the parameters of `conv_block(1, 16)` (convolution without bias plus batch norm), then check with PyTorch.

## 5. Training a CNN and reading its curves

### 5.1 One training function for the whole chapter

You wrote training loops in ml.02. Here is the compact version we reuse, with the habits that matter: `model.train()` / `model.eval()`, `zero_grad`, validation without gradients, and the best-validation checkpoint (a restore of the best weights, not the last).

```python run
def seed_everything(seed):
    torch.manual_seed(seed); np.random.seed(seed)

@torch.no_grad()
def evaluate(model, X, y, bs=512):
    model.eval()
    logits = torch.cat([model(X[i:i + bs]) for i in range(0, len(X), bs)])
    return F.cross_entropy(logits, y).item(), (logits.argmax(1) == y).float().mean().item()

def fit(model, X, y, X_val=None, y_val=None, epochs=30, lr=3e-3, wd=1e-2, bs=32, augment=None, params=None, seed=0, mixup=0.0, bn_eval=False, verbose=False):
    """Train with AdamW + cosine schedule. Returns history; restores the best-validation weights if a validation set is given."""
    g = torch.Generator().manual_seed(seed)
    # `params` may be a list of parameter groups; then `lr` is a list with one peak learning rate per group
    opt = torch.optim.AdamW(params if params is not None else model.parameters(), lr=lr if isinstance(lr, float) else 1e-3, weight_decay=wd)
    steps = epochs * math.ceil(len(X) / bs)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps)
    hist, best, best_state = [], -1, None
    for ep in range(epochs):
        model.train()
        if bn_eval:
            for m in model.modules():
                if isinstance(m, nn.modules.batchnorm._BatchNorm): m.eval()
        perm = torch.randperm(len(X), generator=g)
        tot = n_correct = 0
        for i in range(0, len(X), bs):
            idx = perm[i:i + bs]
            xb, yb = X[idx], y[idx]
            if augment is not None: xb = augment(xb)
            if mixup > 0:
                lam = float(np.random.default_rng(seed * 100003 + ep * 1009 + i).beta(mixup, mixup))
                j = torch.randperm(len(xb), generator=g)
                out = model(lam * xb + (1 - lam) * xb[j])
                loss = lam * F.cross_entropy(out, yb) + (1 - lam) * F.cross_entropy(out, yb[j])
            else:
                out = model(xb); loss = F.cross_entropy(out, yb)
            opt.zero_grad(); loss.backward(); opt.step()
            if sched: sched.step()
            tot += loss.item() * len(idx); n_correct += (out.argmax(1) == yb).sum().item()
        row = {"epoch": ep + 1, "train_loss": tot / len(X), "train_acc": n_correct / len(X)}
        if X_val is not None:
            row["val_loss"], row["val_acc"] = evaluate(model, X_val, y_val)
            if row["val_acc"] > best: best, best_state = row["val_acc"], copy.deepcopy(model.state_dict())
        hist.append(row)
        if verbose and (ep + 1) % 5 == 0: print({k: round(v, 3) for k, v in row.items()})
    if best_state is not None: model.load_state_dict(best_state)
    return pd.DataFrame(hist)

seed_everything(0)
cnn = SmallCNN()
t0 = time.time()
hist = fit(cnn, Xtr, ytr, Xva, yva, epochs=25)
print(hist.iloc[[0, 4, 9, 14, 19, 24]].round(4).to_string(index=False))
print(f"best validation accuracy {hist.val_acc.max():.4f} | test accuracy {evaluate(cnn, Xte, yte)[1]:.4f} | {time.time() - t0:.1f}s on CPU")
```
```text
 epoch  train_loss  train_acc  val_loss  val_acc
     1      2.3269     0.1059    2.2845   0.1039
     5      1.3988     0.8119    1.1817   0.8398
    10      0.2400     0.9713    0.2768   0.9466
    15      0.1137     0.9851    0.1858   0.9525
    20      0.0749     0.9960    0.1546   0.9644
    25      0.0674     0.9980    0.1462   0.9644
best validation accuracy 0.9674 | test accuracy 0.9711 | 7.6s on CPU
```

Two things in that code deserve a sentence. `OneCycleLR` warms the learning rate up and then anneals it to near zero: with small CNNs it usually gives a better end result than a constant rate. And the test set was touched exactly **once**, after training and model selection were over (ds.04).

### 5.2 The shape of the curves tells you what to do

Reading train and validation curves side by side is the vision practitioner's main diagnostic tool.

| What you see | It means | Try |
|---|---|---|
| train and val both poor | **underfitting** | bigger model, train longer, higher learning rate, check for bugs |
| train great, val much worse | **overfitting** | more data, augmentation, weight decay, dropout, smaller model |
| val noisy from epoch to epoch | small validation set or too high a learning rate | larger val set, lower rate, average over seeds |
| val gets better then worse | overfitting set in at that epoch | early stopping, or restore the best checkpoint |

We can manufacture each case. Train the same network on the full training set and on only 60 images (6 per class) and watch the gap open.

```python run
rows = []
for n_per_class in (6, 20, 100):
    idx = torch.cat([(ytr == c).nonzero().flatten()[:n_per_class] for c in range(10)])
    seed_everything(0)
    m = SmallCNN()
    h = fit(m, Xtr[idx], ytr[idx], epochs=40, bs=16)
    rows.append([n_per_class * 10, h.train_acc.iloc[-1], evaluate(m, Xva, yva)[1]])
print(pd.DataFrame(rows, columns=["training images", "final train acc", "validation acc"]).round(3).to_string(index=False))
```
```text
 training images  final train acc  validation acc
              60            1.000           0.774
             200            0.995           0.920
            1000            0.998           0.970
```

> **Predict the output.** Before you read the table: with only 60 training images, will the *training* accuracy be high or low? What about validation accuracy? What does the gap between them say, and which section of this chapter is the remedy?

<details><summary>Answer</summary>

Training accuracy reaches 1.0 even with 60 images (the network has more than enough capacity to memorise them), while validation accuracy is lower, and the gap shrinks as the training set grows. A big train-minus-validation gap is overfitting; the remedies for *not having more data* are data augmentation (section 6) and transfer learning (section 8). See the table above for the exact numbers.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot training and validation accuracy against number of training images (60, 200, 1000) as two lines with labelled axes. Use train accuracy 1.000, 0.995, 0.998 and validation accuracy 0.774, 0.920, 0.970. Shade the gap between the lines and label it 'overfitting gap'. Annotate that the gap is largest at 60 images and shrinks as data grows."

### 5.3 A sanity check that finds bugs: overfit one batch

Before any long training run, train on **one batch** of 32 images for 100 steps. A correct model and loop will drive the loss to nearly zero. If they cannot, something is broken (wrong labels, no `zero_grad`, wrong loss, frozen weights), and no amount of tuning will help. This five-line test is the cheapest debugging step in deep learning.

```python run
seed_everything(0)
m = SmallCNN()
opt = torch.optim.Adam(m.parameters(), lr=1e-2)
xb, yb = Xtr[:32], ytr[:32]
m.train()
for step in range(101):
    loss = F.cross_entropy(m(xb), yb)
    opt.zero_grad(); loss.backward(); opt.step()
    if step in (0, 10, 30, 60, 100): print(f"step {step:>3}  loss {loss.item():.4f}")
print("a healthy model memorises 32 images: final loss near zero ->", loss.item() < 0.05)
```
```text
step   0  loss 2.4202
step  10  loss 1.2885
step  30  loss 0.1830
step  60  loss 0.0090
step 100  loss 0.0032
a healthy model memorises 32 images: final loss near zero -> True
```

### 5.4 Try it

1. Retrain `SmallCNN` with `channels=(4, 8)` and with `channels=(64, 128)` for 25 epochs. Which overfits more? Which gives the best validation accuracy?
2. Comment out `model.eval()` inside `evaluate` and compare the validation accuracy. Why does it change when the network contains batch norm?

## 6. Data augmentation

### 6.1 The idea, and the one rule that matters

Augmentation shows the network **modified copies** of each training image: shifted, flipped, noisier, partly hidden. Each copy is a new, plausible training example, so a small dataset behaves like a larger one, and the network is forced to learn features that survive those changes. You are *teaching invariances through examples*.

The one rule: **an augmentation must not change the label.** A horizontal flip of a cat photo is still a cat. A horizontal flip of a handwritten `2` is *not* a `2`, a vertical flip turns a `6` into something like a `9`. Whether a transform is label-preserving depends on the task, so you decide with domain knowledge. Chest X-rays: left-right flips are suspicious (the heart is on one side). Satellite images: any rotation is fine. Text recognition: flips destroy meaning.

A second rule: **augment the training data only.** Validation and test images must be untouched (or you would be measuring something else), except in the deliberate "test-time augmentation" of section 6.5.

### 6.2 The augmentations, written as tensor functions

`torchvision.transforms` provides all of these for PIL images. Here we write them for tensors in the `(N, C, H, W)` layout, so you see exactly what each does. Each takes a batch and returns a batch, with independent random parameters per image.

```python run
BG = float(Xtr.min())                                           # the value of an empty (background) pixel after normalisation

def random_shift(x, max_shift=1):
    """Move each image by up to max_shift pixels in each direction, filling the gap with background."""
    N, C, H, W = x.shape
    xp = F.pad(x, (max_shift,) * 4, value=BG)
    dy = torch.randint(0, 2 * max_shift + 1, (N,)); dx = torch.randint(0, 2 * max_shift + 1, (N,))
    return torch.stack([xp[n, :, dy[n]:dy[n] + H, dx[n]:dx[n] + W] for n in range(N)])

def random_hflip(x, p=0.5):
    flip = torch.rand(len(x)) < p
    return torch.where(flip[:, None, None, None], x.flip(3), x)

def add_noise(x, sigma=0.3):
    return x + sigma * torch.randn_like(x)

def cutout(x, size=2):
    """Erase one random size x size square per image (set to background)."""
    N, C, H, W = x.shape
    out = x.clone()
    ys = torch.randint(0, H - size + 1, (N,)); xs = torch.randint(0, W - size + 1, (N,))
    for n in range(N): out[n, :, ys[n]:ys[n] + size, xs[n]:xs[n] + size] = BG
    return out

def compose(*fns):
    def run(x):
        for f in fns: x = f(x)
        return x
    return run

def show(img):                                                   # tiny ASCII picture so we can SEE the effect
    chars = " .:-=+*#%@"
    lo, hi = img.min(), img.max()
    return ["".join(chars[int((v - lo) / (hi - lo + 1e-9) * 9)] * 2 for v in row) for row in img[0]]

torch.manual_seed(3)
sample = Xtr[:1]
panels = {"original": sample, "shift": random_shift(sample, 2), "hflip": random_hflip(sample, 1.0), "noise": add_noise(sample, 0.6), "cutout": cutout(sample, 2)}
print(f"label of this image: {ytr[0].item()}")
for r in range(8):
    print("   ".join(show(p[0])[r] for p in panels.values()))
print("   ".join(f"{k:<16}" for k in panels))
```
```text
label of this image: 7
    ==##@@@@..                          ..@@@@##==       ..::--##==##==::       ==##@@@@..  
    **----@@         ==##@@@@..           @@----**       ..::++====##..         **----@@    
        ++**         **----@@             **++             ::::..==++::::           ++**    
    **@@@@@@**           ++**           **@@@@@@**         --++@@****++::       **@@@@@@**  
  ..**####..         **@@@@@@**           ..####**..     ::::++**==..::..     ..**####..    
      ##::         ..**####..               ::##         ::  ::**--::..           ##::      
    ==**               ##::                   **==       ..::..**..::--         ==          
    **--             ==**                     --**       ::  ==++--::::..       **          
original           shift              hflip              noise              cutout          
```

Look at what `random_shift` does with a bare `torch.roll`: roll **wraps around**, so pixels that leave on the right re-enter on the left. For a small centred digit that is harmless, but for natural images it invents content. Padding with the background value (not with `0`, which after normalisation is *not* background; see the trap below) and cropping is the honest version.

> **Trap.** After normalisation the background is `BG`, about `-0.8`, not `0`. Padding with `0` paints a grey frame that the network learns to see as "this image was shifted". Always pad with a value that means "nothing" in the *current* representation.

### 6.3 Does augmentation actually help? Measure it, on the conditions you care about

"Augmentation helps small datasets" is a claim you can test cheaply, but you must decide **what "helps" is measured on**. Training on 150 images (15 per class), we evaluate each model on three versions of the same untouched validation images: **clean** (like the training data), **shifted** (every image moved by up to a pixel) and **noisy** (sensor noise added). Each cell is a mean over 4 seeds, since a single run is noisy.

```python run
idx150 = torch.cat([(ytr == c).nonzero().flatten()[:15] for c in range(10)])
X150, y150 = Xtr[idx150], ytr[idx150]
configs = {
    "none":                       None,
    "shift ±1":                   random_shift,
    "shift ±1 + noise":           compose(random_shift, add_noise),
    "shift ±1 + cutout":          compose(random_shift, cutout),
    "hflip (wrong for digits!)":  random_hflip,
}
torch.manual_seed(123); Xva_shift = random_shift(Xva, 1)                        # the same validation images, each moved by up to 1 pixel
torch.manual_seed(124); Xva_noisy = add_noise(Xva, 0.5)                          # ... and with sensor noise added
rows = []
t0 = time.time()
for name, aug in configs.items():
    accs = []
    for seed in range(4):
        seed_everything(seed)
        m = SmallCNN()
        fit(m, X150, y150, epochs=40, bs=16, augment=aug, seed=seed)
        accs.append([evaluate(m, Xv_, yva)[1] for Xv_ in (Xva, Xva_shift, Xva_noisy)])
    accs = np.array(accs)
    rows.append([name, *accs.mean(0), accs[:, 0].std()])
res = pd.DataFrame(rows, columns=["training augmentation", "clean val", "shifted val", "noisy val", "std (clean)"]).round(3)
print(res.to_string(index=False))
print(f"{time.time() - t0:.0f}s")
```
```text
    training augmentation  clean val  shifted val  noisy val  std (clean)
                     none      0.898        0.561      0.690        0.006
                 shift ±1      0.837        0.841      0.530        0.003
         shift ±1 + noise      0.796        0.804      0.695        0.006
        shift ±1 + cutout      0.781        0.792      0.521        0.021
hflip (wrong for digits!)      0.841        0.522      0.570        0.014
90s
```

> **Predict the output.** Which training setting do you expect to win on the *clean* column, which on the *shifted* column, and which on the *noisy* column? Does any single setting win all three?

<details><summary>Answer</summary>

No setting wins everywhere. Read the table above: with no augmentation the network is best on **clean** images (0.898), because the validation images look exactly like the training images, but it collapses to 0.561 when the images are shifted by a pixel. Training with random shifts lifts the shifted column to 0.841 and costs about six points on clean images (0.837): the network has to solve a harder problem with the same 150 images and the same 40 epochs. Shift alone hurts on noisy images (0.530); adding noise augmentation brings that column back (0.695) and costs a little more on clean images. The horizontal flip is the one that gets nothing in return: it lowers the clean score and does not make the network robust to shifts (0.522) or noise.

The lesson is not "augment more". It is: **augmentation buys robustness to the variation you add, and costs accuracy on conditions you did not need it for.** Choose augmentations that match the variation you expect after deployment, and evaluate under those conditions, not only on clean validation images. (With a bigger network, a longer schedule or more images, the clean-image cost shrinks.) Differences smaller than about two standard deviations over 4 seeds (the last column) are not evidence of anything.

</details>

### 6.4 Mixup

**Mixup** blends two training images and their labels: `x = λ·x_a + (1−λ)·x_b`, and the loss is `λ·CE(out, y_a) + (1−λ)·CE(out, y_b)`, with `λ` drawn from a Beta distribution. It asks the network to behave *linearly* between examples, which acts as a regulariser; on large image sets it often helps, and it is cheap to try. Our `fit` has it built in (`mixup=0.4`). We verify the loss identity first, because "mixing the labels" is easy to get subtly wrong.

```python run
torch.manual_seed(0)
m = SmallCNN().eval()
xa, xb = Xtr[:8], Xtr[8:16]
ya, yb = ytr[:8], ytr[8:16]
lam = 0.7
out = m(lam * xa + (1 - lam) * xb)
loss_mix = lam * F.cross_entropy(out, ya) + (1 - lam) * F.cross_entropy(out, yb)
soft = lam * F.one_hot(ya, 10).float() + (1 - lam) * F.one_hot(yb, 10).float()                  # the same thing with soft labels
loss_soft = -(soft * F.log_softmax(out, 1)).sum(1).mean()
print(f"mixing the losses {loss_mix.item():.6f} == soft-label cross-entropy {loss_soft.item():.6f}: {bool(torch.isclose(loss_mix, loss_soft))}")

rows = []
for name, kw in {"shift only": dict(augment=random_shift), "shift + mixup(0.4)": dict(augment=random_shift, mixup=0.4)}.items():
    accs = []
    for seed in range(4):
        seed_everything(seed); m = SmallCNN()
        fit(m, X150, y150, epochs=40, bs=16, seed=seed, **kw)
        accs.append(evaluate(m, Xva, yva)[1])
    rows.append([name, np.mean(accs), np.std(accs)])
print(pd.DataFrame(rows, columns=["setting", "val acc (mean of 4 seeds)", "std"]).round(4).to_string(index=False))
```
```text
mixing the losses 2.355222 == soft-label cross-entropy 2.355221: True
           setting  val acc (mean of 4 seeds)    std
        shift only                     0.8368 0.0030
shift + mixup(0.4)                     0.8390 0.0128
```

The two rows differ by far less than their standard deviations, so on this tiny problem mixup does **nothing measurable**. That is a legitimate result: report it as "no detectable effect", do not dress it up as a win. Mixup earns its place on larger datasets and longer schedules, where over-fitting is the bottleneck.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Show mixup with lambda = 0.7. Draw two small digit images, image A (label 3) and image B (label 8), then a blended image 0.7*A + 0.3*B between them. Under the blend draw a bar chart of the soft label: 0.7 on class 3, 0.3 on class 8, zero elsewhere over 10 classes. Add a slider for lambda from 0 to 1 that updates the blend and the bars."

### 6.5 Test-time augmentation (TTA)

At prediction time, classify several slightly shifted copies of the input and **average the predicted probabilities**. It costs more compute per prediction and usually adds a little accuracy, because the average smooths out errors that depend on the exact pixel alignment. The input transforms must again be label-preserving.

```python run
@torch.no_grad()
def predict_proba(model, X, tta=False):
    model.eval()
    views = [X]
    if tta:
        xp = F.pad(X, (1,) * 4, value=BG)
        views += [xp[:, :, 1 + dy:9 + dy, 1 + dx:9 + dx] for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
    return torch.stack([F.softmax(model(v), 1) for v in views]).mean(0)

seed_everything(0); m = SmallCNN()
fit(m, X150, y150, epochs=40, bs=16, augment=random_shift)
for tta in (False, True):
    p = predict_proba(m, Xva, tta)
    print(f"TTA={tta!s:<5}  val accuracy {(p.argmax(1) == yva).float().mean():.4f}  |  mean confidence {p.max(1).values.mean():.4f}")
```
```text
TTA=False  val accuracy 0.8338  |  mean confidence 0.6047
TTA=True   val accuracy 0.8665  |  mean confidence 0.5811
```

### 6.6 On your machine: the same pipeline with torchvision

*Not run here (torchvision is not installed offline). Do not trust any number from it until you run it yourself.*

```python
from torchvision import transforms as T

train_tf = T.Compose([
    T.RandomResizedCrop(224, scale=(0.7, 1.0)),      # random crop, resized: scale + shift in one step
    T.RandomHorizontalFlip(),                         # only if the task allows it!
    T.ColorJitter(brightness=0.2, contrast=0.2),      # lighting changes
    T.ToTensor(),                                     # PIL (H,W,C) uint8 -> tensor (C,H,W) in [0,1]
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),   # ImageNet statistics, for ImageNet-pretrained models
])
eval_tf = T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor(), T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
# train transforms: random.  eval transforms: deterministic.  Never the other way round.
```

The structure is identical to what we wrote: **random label-preserving transforms for training, deterministic ones for evaluation, the same normalisation in both**.

### 6.7 Try it

1. Add a `random_brightness(x)` augmentation that scales each image's contrast by a random factor in `[0.8, 1.2]`. Is it label-preserving for digits? Add it to the comparison table.
2. Explain why `random_hflip` hurts digit classification, but the same augmentation is routine for photos of street scenes.
3. Replace `random_shift` with `torch.roll(x, shifts=1, dims=3)` for the whole batch. Why is a *single* random shift per batch weaker than one per image?

## 7. Looking inside a network

A trained CNN is not a black box you must take on faith. Three cheap tools show what it learned and whether it looks at the right thing.

### 7.1 Filters and feature maps

The first layer's filters are small enough to read as numbers. The outputs of that layer, **feature maps**, show where each filter responds. We use the network trained in section 5.1.

```python run
conv1 = cnn.features[0][0]                                      # first Conv2d of SmallCNN: weight shape (16, 1, 3, 3)
print("first-layer weight tensor:", tuple(conv1.weight.shape))
for f in (0, 1, 2):
    print(f"filter {f}:"); print(conv1.weight[f, 0].detach().numpy().round(2))

x = Xva[:1]
maps = conv1(x).detach()
print("\ninput image (a", yva[0].item(), ") and three of the 16 feature maps of the first layer:")
panels = [x[0]] + [maps[0, f:f + 1] for f in (0, 1, 2)]
for r in range(8):
    print("   ".join(show(p)[r] for p in panels))
```
```text
first-layer weight tensor: (16, 1, 3, 3)
filter 0:
[[-0.04  0.21 -0.33]
 [-0.3  -0.15  0.16]
 [-0.13  0.04 -0.06]]
filter 1:
[[-0.    0.02  0.01]
 [-0.4  -0.24 -0.19]
 [ 0.01  0.16  0.15]]
filter 2:
[[-0.17  0.14  0.29]
 [ 0.37  0.03  0.  ]
 [-0.02 -0.02  0.29]]

input image (a 9 ) and three of the 16 feature maps of the first layer:
    ++##==         ++####--::==**##   **##==::--++****   ==--..++##--  ::
  ==**..--**       ****::==##==--**   ++**----++++==**   ----**++--..::::
  **--  ..@@::     ++++==--**++::++   ==++++####++::++   --****++++::----
  ..##**####--     --@@##==..++--==   ++==::    ..::==   --::  --@@##::--
          ----     ++++**++**##++==   ++**********++==   ..----::++--  --
          ++++     **######**##====   ++******##**--==           ==::::--
        ..@@       **####****--==**   ++##%%@@**==::**     ..::::::--==..
    ==####::       ++%%##++  ++++**   ****==::..--**##   ..  ..--%%**  ..
```

You will usually find some filters that look like edge detectors (positive on one side, negative on the other) and some that respond to blobs. Deeper layers combine them into strokes and parts, and are impossible to read as numbers; that is where Grad-CAM helps.

### 7.2 Grad-CAM: where did the network look?

**Grad-CAM** answers "which *part of the image* made the network say class `c`?" Take the last convolutional feature maps `A` (shape `K x h x w`). For class `c`:

1. compute the gradient of the class score with respect to each map, and average it over space to get one **weight** `w_k` per channel (how much channel `k` matters for class `c`);
2. build the heat map `ReLU( Σ_k w_k · A_k )`.

For our network (global average pooling, then one `Linear`) there is a neat fact: the gradient of the class score with respect to map `k` is the same at every position, equal to `W[c, k] / (h·w)`. So `w_k` is just a rescaled row of the head's weight matrix, and Grad-CAM reduces to the original "class activation map". We verify that, which also verifies our code.

```python run
def grad_cam(model, x, c=None):
    """x: one image (1, C, H, W). Returns (cam of shape (h, w), predicted class, weights)."""
    model.eval()
    maps = model.features(x)
    maps.retain_grad()
    logits = model.head(maps)
    c = int(logits.argmax(1)) if c is None else c
    model.zero_grad(); logits[0, c].backward()
    w = maps.grad.mean(dim=(2, 3))                                  # (1, K): average gradient per channel
    cam = F.relu((w[:, :, None, None] * maps).sum(1))[0].detach()   # (h, w)
    return cam, c, w[0].detach()

x = Xva[:1]
cam, c, w = grad_cam(cnn, x)
head_w = cnn.head[-1].weight[c].detach()
h, ww = cnn.features(x).shape[2:]
print("class", c, "| feature maps are", (h, ww), "| heat map shape", tuple(cam.shape))
print("channel weights == head weight row / (h*w):", bool(torch.allclose(w, head_w / (h * ww), atol=1e-6)))
print("heat map (4x4), larger = more responsible for the prediction:"); print(cam.numpy().round(2))
```
```text
class 9 | feature maps are (4, 4) | heat map shape (4, 4)
channel weights == head weight row / (h*w): True
heat map (4x4), larger = more responsible for the prediction:
[[0.37 0.63 0.71 0.55]
 [0.33 0.46 0.28 0.21]
 [0.08 0.35 0.01 0.02]
 [0.23 0.23 0.06 0.21]]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the Grad-CAM steps for a CNN whose last feature maps A have shape K x 4 x 4. Show K small 4x4 maps, each multiplied by a weight w_k (the gradient of the class score averaged over space), summed, then passed through ReLU to give a 4x4 heat map. Then draw this heat map as a colour grid, rows [0.37 0.63 0.71 0.55], [0.33 0.46 0.28 0.21], [0.08 0.35 0.01 0.02], [0.23 0.23 0.06 0.21], upscaled over an 8x8 digit."

### 7.3 Does the heat map tell the truth? A test

A visual explanation can look convincing and still be wrong. So test it with an **occlusion experiment**: hide the 2x2 block of pixels where the heat map peaks and see how much the predicted-class probability drops; compare with hiding a *random* 2x2 block. If Grad-CAM is meaningful, hiding its peak should hurt more.

```python run
@torch.no_grad()
def prob_of(model, x, c):
    model.eval(); return F.softmax(model(x), 1)[0, c].item()

rng = np.random.default_rng(0)
drops_cam, drops_rand = [], []
for i in range(300):
    x = Xva[i:i + 1]
    cam, c, _ = grad_cam(cnn, x)
    if c != yva[i].item(): continue                                   # only images the network gets right
    py, px = divmod(int(cam.argmax()), cam.shape[1])                  # peak in the 4x4 map -> 2x2 pixel block in the 8x8 image
    xo = x.clone(); xo[:, :, 2 * py:2 * py + 2, 2 * px:2 * px + 2] = BG
    ry, rx = rng.integers(0, 4, 2)
    xr = x.clone(); xr[:, :, 2 * ry:2 * ry + 2, 2 * rx:2 * rx + 2] = BG
    base = prob_of(cnn, x, c)
    drops_cam.append(base - prob_of(cnn, xo, c)); drops_rand.append(base - prob_of(cnn, xr, c))
print(f"images tested: {len(drops_cam)}")
print(f"mean drop in class probability when hiding the Grad-CAM peak block: {np.mean(drops_cam):.3f}")
print(f"mean drop when hiding a random block                              : {np.mean(drops_rand):.3f}")
print("hiding the highlighted region hurts more than a random region:", np.mean(drops_cam) > np.mean(drops_rand))
```
```text
images tested: 291
mean drop in class probability when hiding the Grad-CAM peak block: 0.240
mean drop when hiding a random block                              : 0.093
hiding the highlighted region hurts more than a random region: True
```

In real projects this is how Grad-CAM catches **shortcut learning**: a classifier that scores well because it looks at a hospital's watermark, a ruler next to a skin lesion, or the background of the photo, not the object. If the heat map sits on the watermark, the accuracy number is lying to you.

### 7.4 Try it

1. Compute Grad-CAM for the *wrong* class on an image (pass `c=` explicitly). Where does the heat map go?
2. Run the occlusion test with a `3x3` block, and with the block placed at the *lowest* Grad-CAM value. Does the ranking hold?

## 8. Transfer learning

### 8.1 The idea

Training a good vision network from scratch needs millions of images. But the early layers learn **generic** things (edges, textures, simple shapes) that are useful for almost any picture, and only the last layers are specific to the original task. So you take a network **pretrained** on a huge dataset (for instance ImageNet, 1.2 million photos) and reuse its feature extractor:

| Approach | What you train | When it fits |
|---|---|---|
| **Feature extraction** | only a new head; the extractor stays frozen | very little data, target similar to the source |
| **Fine-tuning** | the new head *and* (some of) the extractor, with a small learning rate | more data, or a target that differs from the source |
| **From scratch** | everything | lots of data, or a domain very unlike photos |

The recipe in four moves: (1) load the pretrained network, (2) replace the head with one for your classes, (3) decide what to freeze, (4) train with a **smaller** learning rate for the pretrained part than for the new head.

### 8.2 Building our own "pretrained" network

No internet means no ImageNet weights. So we create the situation ourselves, keeping the roles identical: a **source task** with plenty of data, a **target task** with very little and with a visibly different look.

- **Source**: the clean digit images (1,010 training images, 10 classes). We train a wider `SmallCNN` on them and save it. This plays the role of "ResNet pretrained on ImageNet".
- **Target A (similar domain)**: the same kind of digits with a little sensor noise.
- **Target B (moderately different)**: digits **shifted two pixels to the right** (an off-centre camera) and noisy. The network was pretrained with shifts of at most one pixel, so this is outside what it has seen.
- **Target C (very different)**: digits that are **transposed** (mirrored along the diagonal) and noisy. The strokes are the same kinds of curves, but their orientation is not.

In both targets we are given only `k` labelled images **per class** (k = 2, 5, 10).

```python run
def target_images(X, domain, seed):
    g = torch.Generator().manual_seed(seed)
    if domain == "A: similar":   return X + 0.3 * torch.randn(X.shape, generator=g)
    if domain == "B: shifted":   return F.pad(X, (2, 0, 0, 0), value=BG)[..., :8] + 0.3 * torch.randn(X.shape, generator=g)
    if domain == "C: transposed": return X.transpose(2, 3) + 0.5 * torch.randn(X.shape, generator=g)
    raise ValueError(domain)

seed_everything(0)
base_net = SmallCNN(channels=(32, 64))
fit(base_net, Xtr, ytr, Xva, yva, epochs=30, augment=random_shift)
ckpt = tmp / "pretrained.pt"
torch.save(base_net.state_dict(), ckpt)
print(f"source-task test accuracy: {evaluate(base_net, Xte, yte)[1]:.4f} | saved to {ckpt.name} ({ckpt.stat().st_size / 1024:.0f} KB)")
for dom in ("A: similar", "B: shifted", "C: transposed"):
    print(f"pretrained network, never adapted, on target {dom:<13}: accuracy {evaluate(base_net, target_images(Xva, dom, 99), yva)[1]:.3f}")
```
```text
source-task test accuracy: 0.9800 | saved to pretrained.pt (83 KB)
pretrained network, never adapted, on target A: similar   : accuracy 0.899
pretrained network, never adapted, on target B: shifted   : accuracy 0.798
pretrained network, never adapted, on target C: transposed: accuracy 0.104
```

The un-adapted network degrades as the domain shift grows. Now the recipe.

### 8.3 Step by step: replace the head, freeze, check

```python run
def load_pretrained(n_classes, path=ckpt):
    model = SmallCNN(channels=(32, 64))
    model.load_state_dict(torch.load(path))                        # weights of the extractor AND the old head
    model.head[-1] = nn.Linear(64, n_classes)                      # (2) a fresh head (random weights) for our classes
    return model

def freeze_features(model):
    for p in model.features.parameters(): p.requires_grad = False   # (3) the optimiser will skip these
    return model

m = freeze_features(load_pretrained(10))
trainable = sum(p.numel() for p in m.parameters() if p.requires_grad)
total = sum(p.numel() for p in m.parameters())
print(f"trainable parameters: {trainable:,} of {total:,} ({100 * trainable / total:.1f}%)")

# verify what freezing does and does not do
before_w = m.features[0][0].weight.detach().clone()
before_rm = m.features[0][1].running_mean.clone()
Xt, yt = Xtr[:200], ytr[:200]
fit(m, Xt, yt, epochs=3, lr=1e-2, params=[p for p in m.parameters() if p.requires_grad])
print("frozen conv weights changed?        ", not torch.equal(before_w, m.features[0][0].weight))
print("BatchNorm running_mean changed?     ", not torch.equal(before_rm, m.features[0][1].running_mean), " <- the trap: requires_grad=False does NOT freeze batch-norm statistics")
m2 = freeze_features(load_pretrained(10))
rm2 = m2.features[0][1].running_mean.clone()
fit(m2, Xt, yt, epochs=3, lr=1e-2, params=[p for p in m2.parameters() if p.requires_grad], bn_eval=True)
print("with bn_eval=True, running_mean changed?", not torch.equal(rm2, m2.features[0][1].running_mean))
```
```text
trainable parameters: 650 of 19,562 (3.3%)
frozen conv weights changed?         False
BatchNorm running_mean changed?      True  <- the trap: requires_grad=False does NOT freeze batch-norm statistics
with bn_eval=True, running_mean changed? False
```

> **Predict the output.** Is the second-to-last line `True` or `False`, and what would a data scientist who fine-tunes ImageNet models with a *tiny* batch size (say 2) be at risk of?

<details><summary>Answer</summary>

`True`: `requires_grad=False` only tells autograd not to compute gradients for those parameters. In train mode, batch norm still updates its *running statistics* (buffers, not parameters) from whatever batches it sees. With a tiny batch the statistics are computed from two images and are very noisy, so the "frozen" extractor is quietly damaged. The fix is to keep frozen batch-norm layers in eval mode (`bn_eval=True` in our `fit`; in plain PyTorch, call `.eval()` on those layers after every `model.train()`), or not to freeze them at all when you have reasonable batch sizes.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a transfer-learning model as two blocks in a row: a 'features' extractor (convolution layers) marked frozen with a padlock, then a fresh 'head' Linear(64, 10) with 650 trainable parameters, marked trainable. Label the total as 19,562 parameters, of which 3.3% train. Show gradients flowing back only into the head. Add a note that batch-norm running statistics still update in train mode unless the frozen layers are put in eval mode."

### 8.4 Different learning rates for different parts

When you fine-tune, the pretrained layers already hold good weights; a large step would wreck them ("catastrophic forgetting"), while the new head starts from random and needs big steps. So use **parameter groups**: a small peak learning rate for the extractor, a larger one for the head. This is called **discriminative learning rates**.

```python run
m = load_pretrained(10)
groups = [{"params": m.features.parameters(), "lr": 1e-4}, {"params": m.head.parameters(), "lr": 1e-2}]
opt = torch.optim.AdamW(groups)
print("peak learning rate per group:", [g["lr"] for g in opt.param_groups])
print("number of tensors per group:", [len(g["params"]) for g in opt.param_groups])
```
```text
peak learning rate per group: [0.0001, 0.01]
number of tensors per group: [6, 2]
```

### 8.5 The experiment: scratch, frozen extractor, fine-tuning

Four ways to train on `k` images per class, in two domains. Every cell is the mean validation accuracy over **3 different random subsets** of the target data, since a few images either way change the result a lot.

- **scratch**: a random `SmallCNN` of the same size.
- **frozen, BN adapts**: extractor weights frozen, head trained, batch-norm statistics free to follow the new data.
- **frozen, BN fixed**: extractor frozen and in eval mode: it behaves exactly like the pretrained one.
- **fine-tune**: everything trains, extractor at a peak rate of `1e-3`, head at `1e-2`.

```python run
def run_transfer(domain, k, seed, mode):
    g = torch.Generator().manual_seed(seed)
    idx = torch.cat([(ytr == c).nonzero().flatten()[torch.randperm(int((ytr == c).sum()), generator=g)[:k]] for c in range(10)])
    Xt = target_images(Xtr[idx], domain, seed); yt = ytr[idx]
    seed_everything(seed)
    if mode == "scratch":
        m = SmallCNN(channels=(32, 64)); return fit(m, Xt, yt, epochs=60, bs=16, lr=3e-3, seed=seed), m
    m = load_pretrained(10)
    if mode.startswith("frozen"):
        freeze_features(m)
        fit(m, Xt, yt, epochs=60, bs=16, lr=1e-2, params=list(m.head.parameters()), bn_eval=(mode == "frozen, BN fixed"), seed=seed)
    else:
        groups = [{"params": list(m.features.parameters())}, {"params": list(m.head.parameters())}]
        fit(m, Xt, yt, epochs=60, bs=16, lr=[1e-3, 1e-2], params=groups, seed=seed)
    return None, m

modes = ["scratch", "frozen, BN adapts", "frozen, BN fixed", "fine-tune"]
rows = []
t0 = time.time()
for dom in ("A: similar", "B: shifted", "C: transposed"):
    Xv = target_images(Xva, dom, 99)
    for k in (2, 5, 10):
        accs = {mo: np.mean([evaluate(run_transfer(dom, k, s, mo)[1], Xv, yva)[1] for s in range(3)]) for mo in modes}
        rows.append([dom, k, *accs.values()])
res = pd.DataFrame(rows, columns=["target domain", "images/class", *modes]).round(3)
print(res.to_string(index=False))
print(f"{time.time() - t0:.0f}s")
```
```text
target domain  images/class  scratch  frozen, BN adapts  frozen, BN fixed  fine-tune
   A: similar             2    0.583              0.865             0.869      0.822
   A: similar             5    0.733              0.879             0.894      0.855
   A: similar            10    0.842              0.905             0.914      0.905
   B: shifted             2    0.573              0.770             0.779      0.729
   B: shifted             5    0.710              0.841             0.847      0.831
   B: shifted            10    0.813              0.873             0.883      0.895
C: transposed             2    0.460              0.364             0.359      0.432
C: transposed             5    0.578              0.456             0.450      0.577
C: transposed            10    0.733              0.515             0.543      0.722
233s
```

> **Predict the output.** In which of the three domains do you expect the frozen extractor to do best, and in which worst? Does fine-tuning ever lose to training from scratch? And with only 2 images per class, which approach is the most reliable?

<details><summary>Answer</summary>

Read the table above for the numbers; the pattern is:

- **A (similar)**: the frozen extractor is best (0.87 to 0.91): its features are already right, and a 650-parameter head is hard to over-fit with 20 to 100 images. Scratch is far behind at k=2 (0.58) and still behind at k=10 (0.84). Fine-tuning is a few points below frozen at k=2 and k=5, and level with it at k=10.
- **B (shifted two pixels)**: pretraining still helps a lot (scratch 0.71 at k=5 against 0.84 to 0.85 for the others). Frozen is best at k=2 and k=5; fine-tuning overtakes it at k=10 (0.895 against 0.873 and 0.883).
- **C (transposed)**: the pretrained features do **not** transfer. Fine-tuning only matches scratch (0.43 and 0.46 at k=2; 0.577 and 0.578 at k=5), and the frozen extractor is the worst, 10 to 20 points behind, because a fixed extractor tuned to upright digits cannot be corrected by a new head alone.

Fine-tuning never lost badly to scratch (at best it tied), and it was never far from the best option in any row; frozen was the best in some rows and the worst in others. "Frozen BN adapts" against "frozen BN fixed" differ by at most 0.03, because the batch size of 16 is large enough for stable batch-norm statistics (the damage described in 8.3 appears with batches of 2 to 4). Every cell is a mean over only 3 subsets, so treat gaps of a few points as noise and look at the pattern.

</details>

### 8.6 Reading the result honestly

Do not over-read one table. The reliable lessons are structural:

1. **Transfer is a bet on similarity.** The closer the target is to the source, the more of the pretrained extractor you can leave alone: in A and B the pretrained extractor wins by 10 to 30 points at k=2 to 5; in C it gives nothing.
2. **Fine-tuning with a small learning rate is the safe default.** It was never the worst choice in any row, never far from the best, and it is the only option that did not collapse in domain C. Freezing is cheaper and can win when the target is close, but it is the riskiest if the target is not.
3. **Gains shrink as the target set grows.** In A the gap between the frozen extractor and scratch falls from 0.28 (k=2) to 0.06 (k=10); in B from 0.20 to 0.06. With thousands of target images, scratch can catch up.
4. **Our setup is deliberately small.** On real photos with a network pretrained on ImageNet the gains are usually far larger than here, because ImageNet features are rich and photos share their statistics. Here the "pretraining" is ten digit classes at 8x8 pixels.

### 8.7 On your machine: fine-tuning a real pretrained ResNet

*Not run here (needs torchvision and a download). This is the standard recipe; it is the same four moves as above.*

```python
import torch, torch.nn as nn
from torchvision import models

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)      # (1) load ImageNet weights
model.fc = nn.Linear(model.fc.in_features, n_classes)                 # (2) replace the head (the layer is called `fc` in ResNets)

for p in model.parameters(): p.requires_grad = False                  # (3) freeze everything...
for p in model.fc.parameters(): p.requires_grad = True                #     ...except the head: stage 1 = feature extraction
# stage 2 (fine-tuning): unfreeze the last block, use two learning rates
for p in model.layer4.parameters(): p.requires_grad = True
opt = torch.optim.AdamW([
    {"params": model.layer4.parameters(), "lr": 1e-4},
    {"params": model.fc.parameters(),     "lr": 1e-3}], weight_decay=1e-2)
# use the ImageNet normalisation (section 6.6) and keep frozen BatchNorm layers in eval mode
```

### 8.8 When transfer learning fails

- **Wrong normalisation**: the pretrained model expects its own mean and std (and often an input size). Feeding other statistics silently cuts accuracy.
- **Domain too far**: ImageNet features help on photos and still help (less) on medical images; they help little on spectrograms or microscopy at an unusual scale. Test it; do not assume.
- **Learning rate too high** on the pretrained layers destroys what makes them valuable. If fine-tuning is *worse* than a frozen extractor, lower it.
- **Batch norm with tiny batches**: see 8.3.
- **Leakage**: if the pretraining data contained your test images (common with web-scraped sets), your score is inflated.

### 8.9 Try it

1. Change the fine-tune extractor learning rate to `1e-2` (the same as the head). What happens in domain B at k=5, and why?
2. Unfreeze only the *second* conv block of the frozen model (leave the first frozen). Is this between "frozen" and "fine-tune" in accuracy?
3. Write a function that prints, for any `nn.Module`, the number of trainable and frozen parameters per top-level child.

## 9. Project: a fine-tuned classifier for a custom dataset

### 9.1 The brief

You have been handed **a small folder of images** (30 per class, 10 classes) and a pretrained network. Build the pipeline a colleague could run and trust:

1. **Data**: read class folders of PNG files (tolerating a few files in the wrong colour mode), split them into train / validation / test **by file**, stratified and seeded, with the **pretrained model's own** normalisation.
2. **Model**: load the pretrained extractor, replace the head, and fine-tune in **two stages**: head only (extractor frozen, batch norm fixed), then everything with a smaller learning rate for the extractor.
3. **Comparison**: scratch against head-only against two-stage fine-tuning, on the **validation** set, over several seeds.
4. **Evaluation**: the test set once, for the chosen strategy only: accuracy, per-class recall, the most confused pairs.
5. **A deployable artefact**: one file holding weights, class names and normalisation, loadable into a `Predictor` that **validates its input**.
6. **Tests** for the properties that matter: shapes, mixed colour modes, split hygiene, frozen weights really frozen, determinism, save/load equivalence, input validation, ability to overfit a batch.

### 9.2 Make the dataset (a stand-in for "a folder someone gave you")

Our custom data are the target-B digits of section 8 (shifted two pixels and noisy), saved as PNG files, ten class folders with 30 images each. Four files are saved as RGB instead of grayscale on purpose, because real folders contain such surprises.

```python run
import shutil
proj = pathlib.Path(tempfile.mkdtemp()) / "imgft_project"; proj.mkdir()
data_root = proj / "custom_digits"
names = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
rng = np.random.default_rng(7)
n_rgb = 0
for c, cname in enumerate(names):
    (data_root / cname).mkdir(parents=True)
    pool = np.where(digits.target == c)[0]
    for j, i in enumerate(rng.choice(pool, 30, replace=False)):
        a = np.pad(digits.images[i] / 16.0, ((0, 0), (2, 0)))[:, :8]           # target domain B: moved two columns to the right ...
        a = np.clip(a + rng.normal(0, 0.1, a.shape), 0, 1)                     # ... plus sensor noise
        arr = (a * 255).round().astype(np.uint8)
        if c < 4 and j == 0:                                                   # four stray RGB files
            Image.fromarray(np.stack([arr] * 3, -1), mode="RGB").save(data_root / cname / f"img_{j:02d}.png"); n_rgb += 1
        else:
            Image.fromarray(arr, mode="L").save(data_root / cname / f"img_{j:02d}.png")
files_on_disk = sorted(data_root.rglob("*.png"))
print(f"{len(files_on_disk)} PNG files in {len(names)} class folders | stray RGB files: {n_rgb}")
print("layout:", *[str(p.relative_to(data_root)) for p in files_on_disk[:3]], "...")
modes = {Image.open(p).mode for p in files_on_disk}
print("image modes present:", modes, "<- a loader that forgets .convert('L') breaks on the RGB ones")
```
```text
300 PNG files in 10 class folders | stray RGB files: 4
layout: eight/img_00.png eight/img_01.png eight/img_02.png ...
image modes present: {'L', 'RGB'} <- a loader that forgets .convert('L') breaks on the RGB ones
```

We also need the "pretrained bundle": the weights of section 8 plus what a user of them must know (normalisation statistics, input size, channel widths). This is the information a model zoo ships alongside the weights.

```python run
bundle = {"state_dict": torch.load(ckpt), "channels": (32, 64), "n_source_classes": 10, "mean": float(mean), "std": float(std), "size": 8}
torch.save(bundle, proj / "pretrained_bundle.pt")
print("bundle keys:", list(bundle), "| normalisation used when pretraining: mean %.4f, std %.4f" % (bundle["mean"], bundle["std"]))
```
```text
bundle keys: ['state_dict', 'channels', 'n_source_classes', 'mean', 'std', 'size'] | normalisation used when pretraining: mean 0.3062, std 0.3763
```

### 9.3 The module

```python run
(proj / "imgft.py").write_text('''"""imgft: fine-tune a pretrained small CNN on a folder of images (PyTorch)."""
import copy, dataclasses, math, random
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


# ---------- model ----------
def conv_block(c_in, c_out, pool=False):
    layers = [nn.Conv2d(c_in, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU()]
    if pool:
        layers.append(nn.MaxPool2d(2))
    return nn.Sequential(*layers)


class SmallCNN(nn.Module):
    def __init__(self, n_classes=10, channels=(16, 32)):
        super().__init__()
        c1, c2 = channels
        self.features = nn.Sequential(conv_block(1, c1, pool=True), conv_block(c1, c2))
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.0), nn.Linear(c2, n_classes))

    def forward(self, x):
        return self.head(self.features(x))


def build_model(bundle, n_classes, strategy):
    """strategy: 'scratch' (random weights) or 'head' / 'finetune' (start from the pretrained extractor). The head is always new."""
    if strategy not in ("scratch", "head", "finetune"):
        raise ValueError(f"unknown strategy {strategy!r}")
    model = SmallCNN(bundle["n_source_classes"], tuple(bundle["channels"]))
    if strategy != "scratch":
        model.load_state_dict(bundle["state_dict"])
    model.head[-1] = nn.Linear(model.head[-1].in_features, n_classes)
    return model


# ---------- data ----------
def list_images(root):
    """Class names (sorted folder names), file paths, integer labels. Fails loudly on an empty class."""
    root = Path(root)
    classes = sorted(d.name for d in root.iterdir() if d.is_dir())
    if len(classes) < 2:
        raise ValueError(f"need at least 2 class folders in {root}, found {len(classes)}")
    files, labels = [], []
    for ci, cname in enumerate(classes):
        found = sorted(p for p in (root / cname).iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
        if not found:
            raise ValueError(f"class folder {cname!r} contains no images")
        files += found
        labels += [ci] * len(found)
    return classes, files, np.array(labels)


def split_indices(labels, seed=0, val=0.2, test=0.2):
    """Stratified split BY FILE. Returns three disjoint, sorted index arrays."""
    rng = np.random.default_rng(seed)
    tr, va, te = [], [], []
    for c in np.unique(labels):
        idx = rng.permutation(np.where(labels == c)[0])
        n_te, n_va = max(1, round(len(idx) * test)), max(1, round(len(idx) * val))
        te += idx[:n_te].tolist()
        va += idx[n_te:n_te + n_va].tolist()
        tr += idx[n_te + n_va:].tolist()
    return np.array(sorted(tr)), np.array(sorted(va)), np.array(sorted(te))


def to_tensor(image, size, mean, std):
    """PIL image or path -> normalised float tensor (1, size, size). Always converts to grayscale; checks the size."""
    im = image if isinstance(image, Image.Image) else Image.open(image)
    im = im.convert("L")
    if im.size != (size, size):
        raise ValueError(f"expected a {size}x{size} image, got {im.size[0]}x{im.size[1]}")
    a = np.asarray(im, dtype=np.float32) / 255.0
    return torch.from_numpy((a - mean) / std)[None]


class ImageFolderDataset(Dataset):
    """Items are (image tensor, label). Random shifts of up to one pixel when `augment` is true (training data only)."""
    def __init__(self, files, labels, size, mean, std, augment=False, seed=0):
        self.files, self.labels, self.size, self.mean, self.std = list(files), list(labels), size, mean, std
        self.augment, self.rng = augment, np.random.default_rng(seed)
        self.bg = to_tensor(Image.fromarray(np.zeros((size, size), np.uint8)), size, mean, std).min().item()

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        x = to_tensor(self.files[i], self.size, self.mean, self.std)
        if self.augment:
            dy, dx = (int(v) for v in self.rng.integers(-1, 2, 2))
            xp = F.pad(x, (1, 1, 1, 1), value=self.bg)
            x = xp[:, 1 + dy:1 + dy + self.size, 1 + dx:1 + dx + self.size]
        return x, int(self.labels[i])


# ---------- training ----------
@dataclasses.dataclass
class Config:
    strategy: str = "finetune"
    seed: int = 0
    head_epochs: int = 15
    epochs: int = 30
    lr_head: float = 1e-2
    lr_backbone: float = 1e-3
    weight_decay: float = 1e-2
    batch_size: int = 16
    augment: bool = True


def seed_everything(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def set_frozen(model, frozen):
    for p in model.features.parameters():
        p.requires_grad = not frozen


def train_mode(model, bn_fixed):
    model.train()
    if bn_fixed:
        for m in model.modules():
            if isinstance(m, nn.modules.batchnorm._BatchNorm):
                m.eval()


@torch.no_grad()
def evaluate(model, loader):
    model.eval()
    logits, ys = [], []
    for xb, yb in loader:
        logits.append(model(xb)); ys.append(yb)
    logits, ys = torch.cat(logits), torch.cat(ys)
    return {"loss": F.cross_entropy(logits, ys).item(), "accuracy": (logits.argmax(1) == ys).float().mean().item(),
            "pred": logits.argmax(1).tolist(), "true": ys.tolist(), "prob": F.softmax(logits, 1).max(1).values.tolist()}


def run_stage(model, loader, val_loader, epochs, param_groups, peak_lrs, weight_decay, bn_fixed):
    opt = torch.optim.AdamW(param_groups, lr=1e-3, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=peak_lrs, total_steps=epochs * len(loader))
    best, best_state, history = -1.0, None, []
    for ep in range(epochs):
        train_mode(model, bn_fixed)
        total = 0.0
        for xb, yb in loader:
            loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
            total += loss.item() * len(yb)
        val = evaluate(model, val_loader)
        history.append({"train_loss": total / len(loader.dataset), "val_loss": val["loss"], "val_acc": val["accuracy"]})
        if val["accuracy"] > best:
            best, best_state = val["accuracy"], copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    return history


def fit(bundle, files, labels, split, n_classes, cfg):
    """Train according to cfg.strategy. Returns (model, history). Validation picks the best epoch; the test set is never touched here."""
    seed_everything(cfg.seed)
    tr, va, _ = split
    size, mean, std = bundle["size"], bundle["mean"], bundle["std"]
    train_ds = ImageFolderDataset([files[i] for i in tr], labels[tr], size, mean, std, augment=cfg.augment, seed=cfg.seed)
    val_ds = ImageFolderDataset([files[i] for i in va], labels[va], size, mean, std)
    g = torch.Generator().manual_seed(cfg.seed)
    loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, generator=g)
    val_loader = DataLoader(val_ds, batch_size=256)
    model = build_model(bundle, n_classes, cfg.strategy)
    history = []
    if cfg.strategy == "scratch":
        history += run_stage(model, loader, val_loader, cfg.head_epochs + cfg.epochs, [{"params": model.parameters()}], [3e-3], cfg.weight_decay, bn_fixed=False)
    elif cfg.strategy == "head":
        set_frozen(model, True)
        history += run_stage(model, loader, val_loader, cfg.head_epochs + cfg.epochs, [{"params": model.head.parameters()}], [cfg.lr_head], cfg.weight_decay, bn_fixed=True)
    else:
        set_frozen(model, True)                                     # stage 1: the new head learns on top of fixed features
        history += run_stage(model, loader, val_loader, cfg.head_epochs, [{"params": model.head.parameters()}], [cfg.lr_head], cfg.weight_decay, bn_fixed=True)
        set_frozen(model, False)                                    # stage 2: everything, extractor at a smaller rate
        groups = [{"params": model.features.parameters()}, {"params": model.head.parameters()}]
        history += run_stage(model, loader, val_loader, cfg.epochs, groups, [cfg.lr_backbone, cfg.lr_head / 10], cfg.weight_decay, bn_fixed=False)
    return model, history


# ---------- reporting ----------
def make_loader(bundle, files, labels, idx):
    ds = ImageFolderDataset([files[i] for i in idx], labels[idx], bundle["size"], bundle["mean"], bundle["std"])
    return DataLoader(ds, batch_size=256)


def report(model, loader, classes):
    res = evaluate(model, loader)
    true, pred = np.array(res["true"]), np.array(res["pred"])
    recall = {classes[c]: float((pred[true == c] == c).mean()) for c in range(len(classes)) if (true == c).any()}
    pairs = {}
    for t, p in zip(true, pred):
        if t != p:
            pairs[(classes[t], classes[p])] = pairs.get((classes[t], classes[p]), 0) + 1
    return {"accuracy": res["accuracy"], "n": len(true), "recall": recall, "confusions": sorted(pairs.items(), key=lambda kv: -kv[1])}


# ---------- the artefact ----------
def save_artifact(path, model, bundle, classes, cfg):
    torch.save({"state_dict": model.state_dict(), "channels": tuple(bundle["channels"]), "classes": list(classes), "mean": bundle["mean"],
                "std": bundle["std"], "size": bundle["size"], "config": dataclasses.asdict(cfg)}, path)


class Predictor:
    """Loads an artefact and classifies ONE image (path, PIL image, or 2-D uint8 array). Validates the input."""
    def __init__(self, path):
        a = torch.load(path, weights_only=True)
        self.classes, self.size, self.mean, self.std = a["classes"], a["size"], a["mean"], a["std"]
        self.model = SmallCNN(len(self.classes), tuple(a["channels"]))
        self.model.load_state_dict(a["state_dict"])
        self.model.eval()

    def predict(self, image, top=3):
        if isinstance(image, np.ndarray):
            if image.ndim != 2:
                raise ValueError(f"expected a 2-D grayscale array, got shape {image.shape}")
            if not np.isfinite(image).all():
                raise ValueError("image contains NaN or infinity")
            image = Image.fromarray(np.clip(image, 0, 255).astype(np.uint8), mode="L")
        x = to_tensor(image, self.size, self.mean, self.std)[None]
        with torch.no_grad():
            p = F.softmax(self.model(x), 1)[0]
        order = p.argsort(descending=True)[:top].tolist()
        return {"label": self.classes[order[0]], "confidence": float(p[order[0]]), "top": [(self.classes[i], round(float(p[i]), 4)) for i in order]}
''', encoding="utf-8")
print("wrote", (proj / "imgft.py").name, "|", len((proj / "imgft.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
wrote imgft.py | 233 lines
```

### 9.4 Data hygiene first

```python run
sys.path.insert(0, str(proj))
import importlib, imgft
importlib.reload(imgft)

classes, files, labels = imgft.list_images(data_root)
split = imgft.split_indices(labels, seed=0)
tr, va, te = split
print("classes:", classes)
print(f"files {len(files)} | train {len(tr)} ({len(tr) // 10}/class) | validation {len(va)} | test {len(te)}")
print("splits are disjoint:", not (set(tr) & set(va) or set(tr) & set(te) or set(va) & set(te)), "| all files used:", len(tr) + len(va) + len(te) == len(files))
print("class balance in each split:", [np.bincount(labels[s]).tolist() for s in split])

ds = imgft.ImageFolderDataset([files[i] for i in tr], labels[tr], 8, bundle["mean"], bundle["std"])
rgb_idx = next(i for i, f in enumerate(ds.files) if Image.open(f).mode == "RGB")
x, y = ds[rgb_idx]
print(f"an item (including a stray RGB file): image {tuple(x.shape)} {x.dtype}, label {y} = {classes[y]}")
```
```text
classes: ['eight', 'five', 'four', 'nine', 'one', 'seven', 'six', 'three', 'two', 'zero']
files 300 | train 180 (18/class) | validation 60 | test 60
splits are disjoint: True | all files used: True
class balance in each split: [[18, 18, 18, 18, 18, 18, 18, 18, 18, 18], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6]]
an item (including a stray RGB file): image (1, 8, 8) torch.float32, label 4 = one
```

### 9.5 Which strategy? Three seeds on the validation set

```python run
t0 = time.time()
rows = []
for strategy in ("scratch", "head", "finetune"):
    vals = []
    for seed in range(3):
        sp = imgft.split_indices(labels, seed=seed)                      # a different split per seed: more honest than one lucky split
        cfg = imgft.Config(strategy=strategy, seed=seed)
        model_s, hist_s = imgft.fit(bundle, files, labels, sp, 10, cfg)
        vals.append(imgft.evaluate(model_s, imgft.make_loader(bundle, files, labels, sp[1]))["accuracy"])
    rows.append([strategy, np.mean(vals), np.std(vals), min(vals), max(vals)])
cmp_ = pd.DataFrame(rows, columns=["strategy", "val acc mean", "std", "worst seed", "best seed"]).round(4)
print(cmp_.to_string(index=False))
print(f"{time.time() - t0:.0f}s")
```
```text
strategy  val acc mean    std  worst seed  best seed
 scratch        0.9333 0.0236      0.9000     0.9500
    head        0.9444 0.0157      0.9333     0.9667
finetune        0.9444 0.0157      0.9333     0.9667
151s
```

> **Predict the output.** Which strategy do you expect to win on validation, and which has the *largest* spread across seeds? What would you do if the best strategies were within one standard deviation of each other?

<details><summary>Answer</summary>

Read the table above. In this run head-only and two-stage fine-tuning tie at 0.944 and scratch is close behind at 0.933, with scratch showing the largest spread. These differences are well inside the noise: the validation set has 60 images, so one image is 1.7 points and a "difference" of 0.011 is less than one image on average. When strategies tie, do not crown a winner. Pick on other grounds: cost, and robustness if the target changes. We pick **two-stage fine-tuning**, because it tied for best here, and in section 8 it was the one strategy never far from the best across all three domains (frozen collapsed in domain C). Notice, too, that on this dataset pretraining gives little: 18 images per class is enough for a small network on 8x8 digits. In section 8, with 5 images per class, the pretrained extractor won by more than 10 points. Pretraining pays most when labelled data are scarcest.

</details>

### 9.6 Train the chosen strategy and test it, once

We go with **two-stage fine-tuning** (the standard recipe, and the choice argued for in 9.5), seed 0, and open the test set for the first and only time.

```python run
cfg = imgft.Config(strategy="finetune", seed=0)
model_f, hist_f = imgft.fit(bundle, files, labels, split, 10, cfg)
h = pd.DataFrame(hist_f); h.index += 1; h.index.name = "epoch"
print("stage 1 = epochs 1-15 (head only), stage 2 = epochs 16-45 (all layers):")
print(h.iloc[[0, 4, 14, 15, 24, 44]].round(4).to_string())
rep = imgft.report(model_f, imgft.make_loader(bundle, files, labels, te), classes)
print(f"\nTEST accuracy {rep['accuracy']:.4f} on {rep['n']} images")
print("per-class recall:", {k: round(v, 2) for k, v in rep["recall"].items()})
print("most confused (true -> predicted, count):", [(f"{t}->{p}", n) for (t, p), n in rep["confusions"][:5]] or "no mistakes")
```
```text
stage 1 = epochs 1-15 (head only), stage 2 = epochs 16-45 (all layers):
       train_loss  val_loss  val_acc
epoch                               
1          2.4182    2.3493   0.0333
5          1.2128    0.8334   0.9667
15         0.5740    0.4099   0.9667
16         1.0885    0.7806   0.9333
25         0.6839    0.4755   0.9500
45         0.4213    0.3231   0.9667

TEST accuracy 0.9167 on 60 images
per-class recall: {'eight': 1.0, 'five': 1.0, 'four': 1.0, 'nine': 0.67, 'one': 0.83, 'seven': 0.83, 'six': 0.83, 'three': 1.0, 'two': 1.0, 'zero': 1.0}
most confused (true -> predicted, count): [('nine->five', 2), ('one->four', 1), ('seven->two', 1), ('six->five', 1)]
```

Read the table first. After 5 epochs of head-only training the validation accuracy is already 0.967: the pretrained features fit this target. When stage 2 starts at epoch 16 the extractor begins to move and the training loss jumps (0.57 to 1.09), then settles lower than where stage 1 ended (0.42 at epoch 45). That jump is the price of unfreezing; it is why stage 2 uses a smaller learning rate for the extractor.

The test accuracy is 0.917, which is **55 of 60 images**; one more mistake would be 1.7 points. Report the count, not just the percentage. Two of the five mistakes are `nine -> five`, which tells you where to look first (do the Grad-CAM audit of 9.9), and you must not tune anything on this number now: the test set has been used.

### 9.7 Package it and use it

```python run
art = proj / "digit_classifier.pt"
imgft.save_artifact(art, model_f, bundle, classes, cfg)
pred = imgft.Predictor(art)
print(f"artefact: {art.name}, {art.stat().st_size / 1024:.0f} KB")
i = int(te[0])
out = pred.predict(files[i])
print("file", files[i].parent.name + "/" + files[i].name, "->", out["label"], f"(confidence {out['confidence']:.3f})", "| top 3:", out["top"])
print("predictor agrees with the in-memory model on all test files:",
      all(pred.predict(files[j])["label"] == classes[p] for j, p in zip(te, imgft.evaluate(model_f, imgft.make_loader(bundle, files, labels, te))["pred"])))
for bad, why in [(np.zeros((9, 9), np.uint8), "wrong size"), (np.full((8, 8), np.nan), "NaN pixels"), (np.zeros((8, 8, 3), np.uint8), "colour array")]:
    try: pred.predict(bad)
    except ValueError as e: print(f"rejected ({why}):", e)
```
```text
artefact: digit_classifier.pt, 83 KB
file eight/img_02.png -> eight (confidence 0.774) | top 3: [('eight', 0.7739), ('three', 0.0738), ('seven', 0.0551)]
predictor agrees with the in-memory model on all test files: True
rejected (wrong size): expected a 8x8 image, got 9x9
rejected (NaN pixels): image contains NaN or infinity
rejected (colour array): expected a 2-D grayscale array, got shape (8, 8, 3)
```

A confidence of 0.95 does **not** mean "right 95% of the time": softmax confidences from small, overfit networks are usually over-confident (ds.04, calibration). Use the value to rank or to flag low-confidence cases for a human, not as a probability.

### 9.8 Tests for the properties that matter

```python run
(proj / "test_imgft.py").write_text('''import numpy as np, pytest, torch
from PIL import Image
import imgft

MEAN, STD = 0.3, 0.9


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    """A 3-class folder of 12 random 8x8 images per class, one of them RGB, plus an untrained bundle."""
    root = tmp_path_factory.mktemp("data")
    rng = np.random.default_rng(0)
    for c in range(3):
        (root / f"c{c}").mkdir()
        for j in range(12):
            a = (rng.random((8, 8)) * 60 + c * 80).astype(np.uint8)          # classes differ in brightness: learnable
            img = Image.fromarray(np.stack([a] * 3, -1), mode="RGB") if j == 0 else Image.fromarray(a, mode="L")
            img.save(root / f"c{c}" / f"{j}.png")
    torch.manual_seed(0)
    net = imgft.SmallCNN(10, (8, 16))
    bundle = {"state_dict": net.state_dict(), "channels": (8, 16), "n_source_classes": 10, "mean": MEAN, "std": STD, "size": 8}
    classes, files, labels = imgft.list_images(root)
    return root, bundle, classes, files, labels


def test_dataset_item_shape_and_mixed_modes(tiny):
    _, bundle, _, files, labels = tiny
    ds = imgft.ImageFolderDataset(files, labels, 8, MEAN, STD)
    x, y = ds[0]                                                                     # item 0 is the RGB file of class c0
    assert x.shape == (1, 8, 8) and x.dtype == torch.float32, "an item must be one float32 channel; convert('L') the RGB file"
    assert isinstance(y, int)


def test_split_is_disjoint_stratified_and_seeded(tiny):
    labels = tiny[4]
    a, b = imgft.split_indices(labels, 0), imgft.split_indices(labels, 0)
    assert all(np.array_equal(u, v) for u, v in zip(a, b)), "same seed must give the same split"
    tr, va, te = a
    assert not (set(tr) & set(va) or set(tr) & set(te) or set(va) & set(te)), "LEAKAGE: a file is in two splits"
    for s in a:
        assert len(np.unique(labels[s])) == 3, "every split needs every class"


def test_wrong_size_image_rejected():
    with pytest.raises(ValueError, match="8x8"):
        imgft.to_tensor(Image.fromarray(np.zeros((9, 9), np.uint8)), 8, MEAN, STD)


def test_head_is_replaced(tiny):
    model = imgft.build_model(tiny[1], 3, "finetune")
    assert model(torch.zeros(2, 1, 8, 8)).shape == (2, 3), "the head must output one score per NEW class"


def test_head_strategy_really_freezes_the_extractor(tiny):
    _, bundle, _, files, labels = tiny
    split = imgft.split_indices(labels, 0)
    cfg = imgft.Config(strategy="head", head_epochs=1, epochs=2, augment=False)
    before = imgft.build_model(bundle, 3, "head")
    model, _ = imgft.fit(bundle, files, labels, split, 3, cfg)
    for (n, p0), (_, p1) in zip(before.features.state_dict().items(), model.features.state_dict().items()):
        assert torch.equal(p0, p1), f"{n} changed: a frozen extractor must keep weights AND batch-norm statistics"


def test_finetune_changes_the_extractor(tiny):
    _, bundle, _, files, labels = tiny
    cfg = imgft.Config(strategy="finetune", head_epochs=1, epochs=2, augment=False)
    model, _ = imgft.fit(bundle, files, labels, imgft.split_indices(labels, 0), 3, cfg)
    assert not torch.equal(model.features[0][0].weight, bundle["state_dict"]["features.0.0.weight"]), "stage 2 should update the extractor"


def test_training_is_deterministic(tiny):
    _, bundle, _, files, labels = tiny
    cfg = imgft.Config(strategy="finetune", head_epochs=1, epochs=2, seed=3)
    sp = imgft.split_indices(labels, 0)
    m1, _ = imgft.fit(bundle, files, labels, sp, 3, cfg)
    m2, _ = imgft.fit(bundle, files, labels, sp, 3, cfg)
    for k, v in m1.state_dict().items():
        assert torch.equal(v, m2.state_dict()[k]), f"{k} differs between two runs with the same seed: seed every source of randomness"


def test_can_overfit_a_batch(tiny):
    _, bundle, _, files, labels = tiny
    model = imgft.build_model(bundle, 3, "scratch")
    ds = imgft.ImageFolderDataset(files[:30], labels[:30], 8, MEAN, STD)
    x = torch.stack([ds[i][0] for i in range(30)]); y = torch.tensor([ds[i][1] for i in range(30)])
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    model.train()
    for _ in range(80):
        loss = torch.nn.functional.cross_entropy(model(x), y)
        opt.zero_grad(); loss.backward(); opt.step()
    assert loss.item() < 0.1, f"loss {loss.item():.3f}: a correct model must memorise 30 images (check labels, zero_grad, loss)"


def test_artifact_roundtrip_and_validation(tiny, tmp_path):
    _, bundle, classes, files, labels = tiny
    model = imgft.build_model(bundle, 3, "finetune")
    imgft.save_artifact(tmp_path / "m.pt", model, bundle, classes, imgft.Config())
    p = imgft.Predictor(tmp_path / "m.pt")
    x = imgft.to_tensor(files[5], 8, MEAN, STD)[None]
    model.eval()
    with torch.no_grad():
        want = torch.softmax(model(x), 1)[0]
    got = p.predict(files[5])
    assert got["label"] == classes[int(want.argmax())] and abs(got["confidence"] - float(want.max())) < 1e-6, "loaded model must equal the saved one"
    with pytest.raises(ValueError):
        p.predict(np.zeros((8, 8, 3), np.uint8))
    with pytest.raises(ValueError):
        p.predict(np.full((8, 8), np.nan))
''', encoding="utf-8")
import subprocess
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_imgft.py"], cwd=proj, capture_output=True, text=True, encoding="utf-8")
print((r.stdout + r.stderr).strip()[-900:])
```
```text
.........                                                                [100%]
9 passed in 4.24s
```

Each test exists because of a real failure mode: an RGB file crashing the loader, a file in two splits, a "frozen" extractor whose batch-norm statistics drift, a run that cannot be reproduced, a loss that never reaches zero on 30 images, a saved model that differs from the one you trained.

### 9.9 Extensions

1. **Unfreeze gradually**: stage 2 unfreezes the whole extractor; try unfreezing only the second conv block first (as in practice, from the last layers backwards).
2. **Class imbalance**: remove 20 images from one class and compare plain training, class-weighted loss (ml.01/ds.04) and per-class recall.
3. **A learning-rate range test**: train for a few steps with an exponentially increasing learning rate and plot the loss; pick the peak rate just below where the loss starts to rise.
4. **Grad-CAM audit**: run section 7's Grad-CAM on the misclassified test images. Is the network looking at the strokes?
5. **Real photos (on your machine)**: replace `SmallCNN` and the bundle by `torchvision` ResNet-18 (section 8.7), the `ImageFolderDataset` by `torchvision.datasets.ImageFolder` with the transforms of section 6.6, and keep everything else, including the tests.

## 10. Common traps

1. **Channel order.** PyTorch wants `(N, C, H, W)`; Pillow and NumPy give `(H, W, C)`. A silent wrong order trains on nonsense (section 1.1).
2. **Normalisation statistics from the wrong place.** Compute them from the training set only, and with a pretrained model use *its* statistics (1.2, 8.8).
3. **Mixed colour modes.** A folder with a few RGB or RGBA files among grayscale ones crashes a loader, or worse, trains on a mix. Always `.convert(...)` (1.3).
4. **Forgetting `model.eval()`** when evaluating: batch norm and dropout then behave as in training (5.4).
5. **Augmenting validation or test data**, or using an augmentation that changes the label (a flipped `2`, a rotated `6`) (6.1).
6. **Padding with `0`** after normalisation, which is not "background" (6.2).
7. **`requires_grad=False` is not freezing batch norm.** The running statistics still move in train mode (3.2, 8.3).
8. **The same learning rate for pretrained and new layers.** A large rate destroys the pretrained features (8.4).
9. **Judging on a tiny validation set.** With 60 images one example is 1.7 points; average over seeds and say how many images decided the result (9.5).
10. **Opening the test set repeatedly.** Once, at the end, for the chosen model only (9.6).
11. **Trusting a heat map or a confidence without testing it.** Grad-CAM can mislead (check with occlusion, 7.3); softmax confidence is not a calibrated probability (9.7).
12. **Assuming transfer learning always helps.** It is a bet on similarity between source and target (8.6, 8.8).

## 11. Summary

- An image batch is a `(N, C, H, W)` tensor of scaled, standardised values; the statistics come from the training set (or from the pretrained model).
- A `Conv2d(C_in, C_out, k)` has `C_out·(C_in·k·k + 1)` parameters; the output size is `floor((n + 2p − d(k−1) − 1)/s) + 1`. Convolutions share weights across positions, so they are far cheaper than fully connected layers and are translation-equivariant. Receptive fields grow with depth, stride and pooling; two `3x3` convs see what one `5x5` sees with fewer weights.
- `1x1` convs mix channels; depthwise convs mix space; global average pooling removes the dependence on image size.
- A standard classifier is `[conv-bn-relu blocks] → global pool → Linear`: a feature extractor and a head. Residual blocks (`x + F(x)`) keep gradients alive in deep networks.
- Read train and validation curves: a big gap is overfitting. Before any long run, overfit one batch.
- Augmentation adds label-preserving variety to **training data only**; measure it over several seeds, and treat a flip that changes the label as a bug. Mixup blends images and labels; test-time augmentation averages predictions over small shifts.
- Grad-CAM shows which regions drove a prediction; verify it by occlusion before you trust it.
- Transfer learning: load the pretrained extractor, replace the head, freeze what you must, use a **small** learning rate for pretrained layers and a larger one for the new head, keep frozen batch norm in eval mode, use the pretrained model's normalisation. It is a bet on source-target similarity; the closer they are, the more you can freeze.
- A finished project has a hygienic split, a comparison over seeds, a single test evaluation, an artefact that carries its own normalisation and class names, a predictor that validates input, and tests for each property above.

**Self-check (answer without looking back):**

1. A `Conv2d(32, 64, 3, padding=1)` receives `(8, 32, 20, 20)`. Output shape? Parameters?
2. Why does `bias=False` make sense in a conv followed by batch norm?
3. Name two reasons a horizontal flip can be a bad augmentation.
4. What does `requires_grad=False` not stop in a batch-norm layer?
5. Why two learning rates when fine-tuning?
6. Your fine-tuned model scores 97% on validation and 82% on a colleague's new photos. List three explanations.

<details><summary>Answer</summary>

1. `(8, 64, 20, 20)`; `64 × (32·3·3) + 64 = 18,496` parameters.
2. Batch norm subtracts the per-channel mean and adds its own learned shift, so a convolution bias is redundant.
3. The flipped image can have a different true label (digits, text, handedness in medical images), and it shows the network configurations it will never see at test time.
4. The running mean and variance (buffers), which keep updating in train mode.
5. The pretrained layers already hold good weights and a large step would destroy them; the new head starts from random weights and needs larger steps.
6. Domain shift between the validation images and the new photos (lighting, camera, scale); leakage or an over-optimistic validation split (near-duplicates across splits); different preprocessing or normalisation at prediction time; the validation set being so small that 97% was luck.

</details>
