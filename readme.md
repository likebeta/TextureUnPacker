split image which packed by TexturePacker to little images with help of plist file

#### setup

TexturePacker depend on PIL, you should install PIL first.

You can install Pillow instead of PIL.

```
pip install Pillow
```

#### Usage

```
python TextureUnPacker.py sample.plist
```

#### Todo

Now, TextureUnPacker only support TexturePacker plist with format v2 and v3. It is better to support format v0, v1 and json format.
