import numpy as np
import pytest

from solution import add_clipped


def slow(img, delta):
    out = [min(max(int(v) + delta, 0), 255) for v in img.ravel().tolist()]
    return np.array(out, dtype=np.uint8).reshape(img.shape)


def test_brighter_does_not_wrap():
    img = np.array([[250, 100, 5]], dtype=np.uint8)
    got = add_clipped(img, 10)
    assert got[0, 0] != 4, "values wrapped round: 250 + 10 gave 4. Widen to int16 BEFORE adding, then clip to 0..255."
    assert got.tolist() == [[255, 110, 15]], f"expected [[255, 110, 15]], got {got.tolist()}: clip to 255 at the top."


def test_darker_does_not_wrap():
    img = np.array([[250, 100, 5]], dtype=np.uint8)
    got = add_clipped(img, -10)
    assert got[0, 2] != 251, "values wrapped round: 5 - 10 gave 251. Widen first, then clip at 0."
    assert got.tolist() == [[240, 90, 0]], f"expected [[240, 90, 0]], got {got.tolist()}."


def test_dtype_and_shape():
    img = np.full((4, 5, 3), 120, dtype=np.uint8)
    got = add_clipped(img, 30)
    assert got.dtype == np.uint8, f"your result is {got.dtype}; the image must stay uint8. Convert back with .astype(np.uint8) after clipping."
    assert got.shape == (4, 5, 3), f"the shape must stay (4, 5, 3), got {got.shape}."


def test_input_unchanged_and_new_array():
    img = np.array([[10, 20], [30, 40]], dtype=np.uint8)
    before = img.copy()
    got = add_clipped(img, 50)
    np.testing.assert_array_equal(img, before, err_msg="the caller's image changed: do not use += on the input.")
    assert not np.shares_memory(got, img), "return a new array, not the input itself."


def test_big_deltas():
    img = np.array([0, 1, 128, 254, 255], dtype=np.uint8)
    assert add_clipped(img, 255).tolist() == [255, 255, 255, 255, 255], "delta 255 pushes every pixel to the top: clip."
    assert add_clipped(img, -255).tolist() == [0, 0, 0, 0, 0], "delta -255 pushes every pixel to 0: clip."
    assert add_clipped(img, 0).tolist() == [0, 1, 128, 254, 255], "delta 0 changes nothing."


@pytest.mark.parametrize("seed", range(6))
def test_random_images(seed):
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 256, size=(6, 7, 3)).astype(np.uint8)
    delta = int(rng.integers(-255, 256))
    got = add_clipped(img, delta)
    assert got.dtype == np.uint8, f"your result is {got.dtype}; the image must stay uint8."
    np.testing.assert_array_equal(got, slow(img, delta), err_msg=f"wrong pixels for delta = {delta}.")
