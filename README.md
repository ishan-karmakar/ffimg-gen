# File Format Image Generator (ffimg-gen)
This is a utility to create file format images from a YAML specification.

# Examples of Results

# Install
```bash
$ pip install ffimg-gen
$ ffimg-gen ...
```

# Usage
This is an example YAML spec:
```yaml
- fields:
  - size: 8B
    name: Signature
  - size: 4B
    name: Number of fields
- fields:
  - size: 1MB
    name: Data 1
  - size: 2MB
    name: Data 2
```
Each top level array represents a collection of fields (header, body, footer, etc.). While it doesn't make a difference in the output image as of now, a goal is to color code the fields to show the collections.

To run the script:
```bash
$ ffimg-gen spec.yaml
```

# How it works
`ffimg-gen` works by using linear interpolation to approximate the size of the box relative to the other boxes. This is a complicated task, as it has to manage making sure the text can fit, as well as making sure an extremely large sized field (ex. 1MB) doesn't completely take over a smaller field (4B). It does this by having a threshold where any size under it will be linearly scaled to the size of the block, and any size over it will be linearly interpolated between the threshold and the maximum sized block.
