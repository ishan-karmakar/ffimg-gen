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
