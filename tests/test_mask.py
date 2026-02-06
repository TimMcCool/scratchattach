from util import mask_secret

def test_mask():
    mask_secret("Test Mask 123")
    print("Test Mask 123")
    print("abcTest Mask 123")
    print("Test Mask 123abc")
    print("abc\n\nTest Mask 123")
    # Should not be censored
    print("Testabc Mask 123")
    