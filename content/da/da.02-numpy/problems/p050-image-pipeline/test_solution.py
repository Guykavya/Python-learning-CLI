import numpy as np
import pytest

from solution import adjust, blur3, equalise, flip, pipeline, to_gray

WEIGHTS = np.array([0.299, 0.587, 0.114])


def make_scene(h=24, w=32):
    """A small picture in the style of Ch. 20.2: sky, sun, ground, building."""
    yy = np.arange(h)[:, None]
    xx = np.arange(w)[None, :]
    img = np.zeros((h, w, 3), dtype=np.uint8)
    sky = (60 + 130 * yy / h).astype(np.uint8)
    img[..., 0] = sky // 2
    img[..., 1] = sky
    img[..., 2] = 255 - sky // 3
    img[(yy - 6) ** 2 + (xx - 24) ** 2 <= 16] = (255, 220, 40)
    img[18:] = (30, 120, 40)
    img[12:20, 5:13] = (150, 40, 30)
    return img


def check_image(out, shape, what):
    assert isinstance(out, np.ndarray), f"{what}: return a NumPy array, not a {type(out).__name__}."
    assert out.dtype == np.uint8, f"{what}: your result is {out.dtype}; the image must stay uint8."
    assert out.shape == shape, f"{what}: shape must be {shape}, got {out.shape}."


def blur_loop(img):
    h, w = img.shape
    out = np.zeros((h, w), dtype=np.uint8)
    for i in range(h):
        for j in range(w):
            total = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ii = min(max(i + di, 0), h - 1)
                    jj = min(max(j + dj, 0), w - 1)
                    total += int(img[ii, jj])
            out[i, j] = round(total / 9)
    return out


# ---------- to_gray ----------

def test_to_gray_pure_colours():
    img = np.zeros((1, 4, 3), dtype=np.uint8)
    img[0, 0] = (255, 0, 0)
    img[0, 1] = (0, 255, 0)
    img[0, 2] = (0, 0, 255)
    img[0, 3] = (255, 255, 255)
    got = to_gray(img)
    check_image(got, (1, 4), "to_gray")
    assert got.tolist() == [[76, 150, 29, 255]], (
        f"pure red, green, blue, white must give 76, 150, 29, 255; got {got.tolist()}. "
        "Weights in the order R, G, B = 0.299, 0.587, 0.114, round (do not truncate), and no uint8 overflow while summing.")


def test_to_gray_scene_matches_the_formula():
    scene = make_scene()
    got = to_gray(scene)
    check_image(got, scene.shape[:2], "to_gray")
    want = np.round(scene.astype(float) @ WEIGHTS)
    assert np.abs(got.astype(int) - want).max() <= 1, "to_gray differs from round(0.299 R + 0.587 G + 0.114 B) by more than rounding."


def test_to_gray_rejects_grey_input():
    with pytest.raises(ValueError):
        to_gray(np.zeros((4, 4), dtype=np.uint8))


# ---------- adjust ----------

def test_adjust_does_not_wrap():
    got = adjust(np.array([250, 10, 0, 255], dtype=np.uint8), brightness=10)
    check_image(got, (4,), "adjust")
    assert got.tolist() == [255, 20, 10, 255], f"values wrapped round: 250 + 10 gave {got.tolist()[0]}. Widen, add, clip(0, 255), then uint8."
    got = adjust(np.array([5, 200], dtype=np.uint8), brightness=-10)
    assert got.tolist() == [0, 190], f"negative brightness: 5 - 10 must clip to 0, got {got.tolist()}."


def test_adjust_identity_and_contrast():
    gray = to_gray(make_scene())
    same = adjust(gray)
    check_image(same, gray.shape, "adjust")
    np.testing.assert_array_equal(same, gray, err_msg="brightness=0, contrast=1 must return an equal image.")
    for c in (0.5, 2.0, 0.0):
        want = np.clip(np.round((gray.astype(float) - 128) * c + 128), 0, 255)
        np.testing.assert_array_equal(adjust(gray, contrast=c), want, err_msg=f"contrast={c}: out = (img - 128) * contrast + 128, rounded and clipped.")
    want = np.clip(np.round((gray.astype(float) - 128) * 1.3 + 128 + 7), 0, 255)
    assert np.abs(adjust(gray, brightness=7, contrast=1.3).astype(int) - want).max() <= 1, "brightness=7, contrast=1.3 does not follow the formula."


def test_adjust_colour_image_keeps_its_shape():
    scene = make_scene()
    check_image(adjust(scene, brightness=30), scene.shape, "adjust on a colour image")


# ---------- flip ----------

def test_flip_both_ways_and_copy():
    scene = make_scene()
    h = flip(scene, "horizontal")
    v = flip(scene, "vertical")
    check_image(h, scene.shape, "flip horizontal")
    check_image(v, scene.shape, "flip vertical")
    np.testing.assert_array_equal(h, scene[:, ::-1], err_msg="'horizontal' mirrors left-right: reverse the columns (axis 1).")
    np.testing.assert_array_equal(v, scene[::-1], err_msg="'vertical' mirrors top-bottom: reverse the rows (axis 0).")
    assert not np.shares_memory(h, scene) and not np.shares_memory(v, scene), "flip must return a copy, not a view (add .copy())."
    np.testing.assert_array_equal(flip(flip(scene, "vertical"), "vertical"), scene, err_msg="flipping twice gives the original back.")
    with pytest.raises(ValueError):
        flip(scene, "diagonal")


# ---------- blur3 ----------

def test_blur3_equals_a_loop_on_small_images():
    rng = np.random.default_rng(50)
    for shape in ((6, 6), (5, 7), (1, 4), (3, 1)):
        img = rng.integers(0, 256, size=shape).astype(np.uint8)
        got = blur3(img)
        check_image(got, shape, "blur3")
        np.testing.assert_array_equal(got, blur_loop(img), err_msg=(
            f"shape {shape}: blur3 differs from the pixel loop. Edge pixels repeat outside the image (np.pad mode='edge'), "
            "sum in float or int (not uint8: 9 x 255 overflows), divide by 9, np.round."))


def test_blur3_constant_and_input_unchanged():
    flat = np.full((5, 5), 77, dtype=np.uint8)
    np.testing.assert_array_equal(blur3(flat), flat, err_msg="blurring a constant image changes nothing.")
    img = np.random.default_rng(1).integers(0, 256, size=(8, 8)).astype(np.uint8)
    keep = img.copy()
    blur3(img)
    np.testing.assert_array_equal(img, keep, err_msg="blur3 changed its input.")


# ---------- equalise ----------

def lut_equalise(img):
    counts = np.bincount(img.ravel(), minlength=256)
    cdf = counts.cumsum()
    first = cdf[counts > 0][0]
    lut = np.clip(np.round((cdf - first) / (cdf[-1] - first) * 255), 0, 255).astype(np.uint8)
    return lut[img]


def test_equalise_full_range_and_formula():
    gray = to_gray(make_scene())
    dull = adjust(gray, contrast=0.35)
    got = equalise(dull)
    check_image(got, dull.shape, "equalise")
    assert int(got.min()) == 0 and int(got.max()) == 255, f"equalise must use the full range 0..255, got {int(got.min())}..{int(got.max())}."
    np.testing.assert_array_equal(got, lut_equalise(dull), err_msg="equalise does not follow the lookup-table formula of the statement.")
    order = np.argsort(dull.ravel(), kind="stable")
    assert np.all(np.diff(got.ravel()[order].astype(int)) >= 0), "equalise must keep the order of grey levels (darker stays darker or equal)."


def test_equalise_constant_image():
    flat = np.full((4, 4), 9, dtype=np.uint8)
    got = equalise(flat)
    check_image(got, (4, 4), "equalise on a constant image")
    np.testing.assert_array_equal(got, flat, err_msg="a constant image comes back unchanged (do not divide by cdf[255] - first = 0).")
    assert not np.shares_memory(got, flat), "even for a constant image, return a copy."


# ---------- pipeline ----------

def test_pipeline_whole_chain():
    scene = make_scene()
    before = scene.copy()
    result = pipeline(scene, [to_gray, lambda a: adjust(a, contrast=0.5), blur3, equalise])
    np.testing.assert_array_equal(scene, before, err_msg="the pipeline must not modify the input image.")
    check_image(result, scene.shape[:2], "pipeline (grayscale drops the colour axis)")
    assert int(result.min()) == 0 and int(result.max()) == 255, "the chain ends with equalise: the result must use the full range."
    step_by_step = equalise(blur3(adjust(to_gray(scene), contrast=0.5)))
    np.testing.assert_array_equal(result, step_by_step, err_msg="pipeline must apply the steps in order, each to the previous result.")


def test_pipeline_order_matters():
    gray = to_gray(make_scene())
    a = pipeline(gray, [lambda x: adjust(x, brightness=100), lambda x: adjust(x, contrast=0.0)])
    b = pipeline(gray, [lambda x: adjust(x, contrast=0.0), lambda x: adjust(x, brightness=100)])
    assert np.all(a == 128) and np.all(b == 228), "steps run left to right: brighten then flatten gives 128 everywhere; flatten then brighten gives 228."


def test_empty_pipeline_returns_a_copy():
    scene = make_scene()
    got = pipeline(scene, [])
    np.testing.assert_array_equal(got, scene, err_msg="no steps: the image comes back unchanged.")
    assert got is not scene and not np.shares_memory(got, scene), "no steps must still return a copy, so editing it cannot change the original."
