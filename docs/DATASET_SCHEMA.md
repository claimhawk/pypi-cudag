# CUDAG Dataset Schema

This document defines the required filesystem structure and data schemas for CUDAG-generated datasets.

## Filesystem Structure

```
datasets/{prefix}--{user}--{timestamp}/
├── config.json           # Generation configuration (required)
├── data.jsonl            # All training samples (required)
├── train.jsonl           # Training split (required)
├── val.jsonl             # Validation split (required)
├── held_out.jsonl        # Held-out samples (optional)
├── images/               # Training images (required)
│   └── *.jpg or *.png
└── test/
    ├── test.json         # Test cases (required)
    ├── images/           # Test screenshots (required)
    │   └── *.png
    └── annotated/        # Annotated images (optional)
        └── *_annotated.png
```

### Directory Naming Convention

Dataset directories follow the pattern: `{prefix}--{user}--{timestamp}`
- `prefix`: Dataset name (e.g., "calendar", "appointment")
- `user`: Username who generated the dataset
- `timestamp`: Generation timestamp in format `YYYYMMDD_HHMMSS`

Example: `calendar--mike--20251203_123456`

## Training Record Schema

Records in `data.jsonl`, `train.jsonl`, and `val.jsonl` must conform to this schema:

```json
{
  "id": "string (required)",
  "image": "string (required, relative path starting with 'images/')",
  "conversations": [
    {
      "from": "human",
      "value": "string (must start with '<image>\\n')"
    },
    {
      "from": "gpt",
      "value": "string (must start with '<tool_call>')"
    }
  ],
  "metadata": {
    "task_type": "string (required)",
    "real_coords": [x, y],
    "tolerance": [tol_x, tol_y]
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique sample identifier |
| `image` | string | Yes | Relative path to image (e.g., `images/sample_00001.jpg`) |
| `conversations` | array | Yes | Human-GPT conversation turns (exactly 2) |
| `metadata.task_type` | string | Yes | Task type identifier (e.g., `click-day`) |
| `metadata.real_coords` | [int, int] | Yes | Original pixel coordinates |
| `metadata.tolerance` | [int, int] | No | Coordinate tolerance in RU units |

### Example Training Record

```json
{
  "id": "calendar_00001",
  "image": "images/calendar_00001.jpg",
  "conversations": [
    {"from": "human", "value": "<image>\nClick October 15 in the calendar"},
    {"from": "gpt", "value": "<tool_call>\n{\"name\": \"computer_use\", \"arguments\": {\"action\": \"left_click\", \"coordinate\": [342, 567]}}\n</tool_call>"}
  ],
  "metadata": {
    "task_type": "click-day",
    "real_coords": [164, 306],
    "tolerance": [27, 13]
  }
}
```

## Test Record Schema

Records in `test/test.json` must conform to this schema:

```json
{
  "test_id": "string (required)",
  "screenshot": "string (required, relative path starting with 'images/')",
  "prompt": "string (required)",
  "expected_action": {
    "name": "computer_use",
    "arguments": {
      "action": "string (required)",
      "coordinate": [x, y]
    }
  },
  "tolerance": [tol_x, tol_y],
  "metadata": {
    "task_type": "string (required)",
    "real_coords": [x, y]
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_id` | string | Yes | Unique test case identifier |
| `screenshot` | string | Yes | Relative path to screenshot from test dir |
| `prompt` | string | Yes | Human instruction prompt |
| `expected_action` | object | Yes | Expected tool call response |
| `tolerance` | [int, int] | Yes | Coordinate tolerance in RU units |
| `metadata.task_type` | string | Yes | Task type identifier |
| `metadata.real_coords` | [int, int] | No | Original pixel coordinates |

### Example Test Record

```json
{
  "test_id": "test_00001",
  "screenshot": "images/test_00001.png",
  "prompt": "Click October 15 in the calendar",
  "expected_action": {
    "name": "computer_use",
    "arguments": {
      "action": "left_click",
      "coordinate": [342, 567]
    }
  },
  "tolerance": [27, 13],
  "metadata": {
    "task_type": "click-day",
    "real_coords": [164, 306],
    "image_size": [480, 540]
  }
}
```

## Coordinate System

All coordinates in training and test data use **RU (Resolution Units)** normalized to [0, 1000]:

```
normalized_x = (pixel_x / image_width) * 1000
normalized_y = (pixel_y / image_height) * 1000
```

Original pixel coordinates are stored in `metadata.real_coords`.

## Validation

Use the `cudag validate` command to check a dataset against this schema:

```bash
cudag validate datasets/my-dataset
cudag validate -v datasets/my-dataset  # Show all errors
```

The validator checks:
1. Required filesystem structure
2. Training record schema
3. Test record schema
4. Image path validity (all referenced images exist)

## Common Errors

### Missing test/images/ directory
```
test/: Missing required directory: images/
```
**Fix:** Ensure test images are saved to `test/images/`, not `test/oos_images/` or other names.

### Invalid image path
```
train.jsonl:42: Invalid image path: sample.jpg (must start with 'images/')
```
**Fix:** Image paths must be relative to dataset root and start with `images/`.

### Missing tolerance
```
test.json:5: tolerance must be [tol_x, tol_y] array
```
**Fix:** Test records must include tolerance as a two-element array.
