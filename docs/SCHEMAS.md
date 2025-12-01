# CUDAG Data Schemas

This document defines the canonical data schemas used in CUDAG datasets.

## 1. Tool Call Schema

Tool calls are the model's output format for computer use actions.

### Wire Format (JSON)

```json
{
  "name": "computer",
  "arguments": {
    "action": "left_click",
    "coordinate": [500, 300]
  }
}
```

### Schema Definition

```typescript
interface ToolCall {
  name: "computer";
  arguments: {
    action: ToolAction;
    coordinate?: [number, number];  // [x, y] in RU units [0, 1000]
    pixels?: number;                // For scroll/hscroll
    keys?: string[];                // For key press
    text?: string;                  // For type
    time?: number;                  // For wait (seconds)
    status?: "success" | "failure"; // For terminate
  };
}

type ToolAction =
  | "left_click"
  | "right_click"
  | "middle_click"
  | "double_click"
  | "triple_click"
  | "scroll"
  | "hscroll"
  | "mouse_move"
  | "left_click_drag"
  | "key"
  | "type"
  | "wait"
  | "terminate"
  | "answer";
```

### Action-Specific Requirements

| Action | Required Fields | Description |
|--------|-----------------|-------------|
| `left_click` | `coordinate` | Click at (x, y) |
| `right_click` | `coordinate` | Right-click at (x, y) |
| `double_click` | `coordinate` | Double-click at (x, y) |
| `scroll` | `coordinate`, `pixels` | Scroll vertically. Negative = up |
| `hscroll` | `coordinate`, `pixels` | Scroll horizontally. Negative = left |
| `key` | `keys` | Press keys in order, release in reverse |
| `type` | `text` | Type text string |
| `wait` | `time` | Wait N seconds |
| `terminate` | `status` | End task with status |

### Coordinate System (RU Units)

All coordinates are normalized to [0, 1000]:
- Conversion: `normalized = (pixel / image_dimension) * 1000`
- Origin (0, 0) is top-left
- Example: pixel (192, 540) on 1920x1080 image = (100, 500) RU


## 2. Training Sample Schema (JSONL)

Each line in `train.jsonl` and `val.jsonl` follows this schema.

### Wire Format

```json
{
  "id": "sample_00123",
  "image": "images/screenshot_00123.jpg",
  "conversations": [
    {"from": "human", "value": "<image>\nClick on the 'Submit' button"},
    {"from": "gpt", "value": "<tool_call>\n{\"name\": \"computer\", \"arguments\": {\"action\": \"left_click\", \"coordinate\": [750, 890]}}\n</tool_call>"}
  ],
  "metadata": {
    "task_type": "click-button",
    "real_coords": [1440, 961],
    "button_label": "Submit"
  }
}
```

### Schema Definition

```typescript
interface TrainingSample {
  id: string;                      // Unique sample ID
  image: string;                   // Relative path to image
  conversations: Conversation[];   // Human/GPT turn pairs
  metadata: {
    task_type: string;             // Task type identifier
    real_coords: [number, number]; // Original pixel coords
    [key: string]: any;            // Task-specific metadata
  };
}

interface Conversation {
  from: "human" | "gpt";
  value: string;
}
```

### GPT Response Format

The GPT response must be wrapped in XML tags:

```
<tool_call>
{"name": "computer", "arguments": {"action": "left_click", "coordinate": [500, 300]}}
</tool_call>
```


## 3. Test Case Schema (test.json)

Test cases for evaluation are stored in `test/test.json`.

### Wire Format

```json
[
  {
    "test_id": "test_00001",
    "screenshot": "images/test_00001.jpg",
    "prompt": "Click the 'Submit' button",
    "expected_action": {
      "name": "computer",
      "arguments": {
        "action": "left_click",
        "coordinate": [750, 890]
      }
    },
    "tolerance": [50, 50],
    "metadata": {
      "task_type": "click-button",
      "real_coords": [1440, 961],
      "button_label": "Submit"
    }
  }
]
```

### Schema Definition

```typescript
interface TestCase {
  test_id: string;                       // Unique test ID
  screenshot: string;                    // Relative path to image
  prompt: string;                        // Human instruction (no <image> prefix)
  expected_action: ToolCall;             // Expected model output
  tolerance: [number, number] | number;  // [x, y] tolerance in RU units
  metadata: {
    task_type: string;                   // Task type identifier
    real_coords?: [number, number];      // Original pixel coords
    [key: string]: any;                  // Task-specific metadata
  };
}
```

### Tolerance

Tolerance defines acceptable coordinate deviation:
- `[50, 50]` = ±50 RU in x and y directions
- `50` = ±50 RU in both directions (shorthand)
- Evaluation passes if: `|predicted_x - expected_x| <= tolerance_x && |predicted_y - expected_y| <= tolerance_y`


## 4. Dataset Config Schema (dataset.yaml)

Configuration for dataset generation.

### Wire Format

```yaml
name_prefix: calendar-mike
seed: 42

tasks:
  click-day: 500
  scroll-month: 200
  select-appointment: 300

task_distributions:
  click-appointment:
    grey_grey: 0.80
    other_colors: 0.15
    adversarial: 0.05

splits:
  train: 0.8

system_prompt: computer-use

output:
  image_format: jpg
  image_quality: 95

test:
  count: 100
  tolerance: 10

annotation:
  enabled: true
  per_type:
    click-day: 4
    scroll-month: 2
```

### Schema Definition

```typescript
interface DatasetConfig {
  name_prefix: string;           // Dataset name prefix
  seed: number;                  // Random seed for reproducibility

  tasks: Record<string, number>; // Task type → sample count

  task_distributions?: Record<string, Record<string, number>>;
  // Optional: distribution of sample types within each task

  splits: {
    train: number;               // Train split ratio (0.0-1.0)
  };

  system_prompt?: string;        // System prompt style

  output?: {
    image_format?: "png" | "jpg";
    image_quality?: number;      // JPEG quality (1-100)
  };

  test?: {
    count: number;               // Number of test cases
    tolerance: number | [number, number];
  };

  annotation?: {
    enabled: boolean;
    ratio?: number;              // Fraction to annotate
    per_type?: Record<string, number>;  // Per-task annotation counts
  };
}
```


## 5. Dataset Directory Structure

```
dataset-name-timestamp/
├── config.json         # Generation config (for reference)
├── data.jsonl          # All samples (train + val)
├── train.jsonl         # Training split
├── val.jsonl           # Validation split
├── held_out.jsonl      # Optional: held-out samples
├── images/             # Training images
│   ├── screenshot_00000.jpg
│   ├── screenshot_00001.jpg
│   └── ...
└── test/               # Test evaluation data
    ├── test.json       # Test case definitions
    ├── images/         # Test images
    │   ├── test_00000.jpg
    │   └── ...
    └── annotated/      # Optional: annotated test images
        ├── test_00000_annotated.png
        └── ...
```


## Validation

Use `cudag.prompts.tools.validate_tool_call()` to validate tool calls:

```python
from cudag.prompts.tools import ToolCall, validate_tool_call

tool_call = ToolCall.left_click((500, 300))
errors = validate_tool_call(tool_call)
if errors:
    print("Validation errors:", errors)
```

Key validations:
- Coordinate range: [0, 1000]
- Required parameters per action type
- Valid action names
- Valid terminate status values
