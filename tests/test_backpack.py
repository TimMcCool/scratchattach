import warnings
import util


def test_backpack():
    if not util.credentials_available():
        warnings.warn("Skipped test_backpack because there were no credentials available.")
        return
    sess = util.session()
    backpack = sess.backpack()

    asset = backpack[0]
    assert asset.filename == "83c36d806dc92327b9e7049a565c6bff.wav"
    assert asset.file_ext == "wav"
    assert not asset.is_json
    assert isinstance(asset.data, bytes)
    # TODO: include delete

    asset = backpack[1]
    assert asset.filename == "bcf454acf82e4504149f7ffe07081dbc.svg"
    assert asset.file_ext == "svg"
    assert not asset.is_json
    assert isinstance(asset.data, bytes)

    asset = backpack[2]
    assert asset.filename == "f8c2f7f077c2fd3aa4a15ce217021152.zip"
    assert asset.file_ext == "zip"
    assert not asset.is_json
    assert isinstance(asset.data, bytes)

    asset = backpack[3]
    assert asset.filename == "3866bcb8de8c798d110d77eefc77190f.json"
    assert asset.file_ext == "json"
    assert asset.is_json
    assert isinstance(asset.data, list)


if __name__ == "__main__":
    test_backpack()
