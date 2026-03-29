---
name: openrouter-image-gen
description: Generate images via OpenRouter API using Gemini image models. Outputs PNG files to the workspace.
metadata: {"openclaw": {"requires": {"env": ["OPENROUTER_API_KEY"]}, "primaryEnv": "OPENROUTER_API_KEY"}}
---

# OpenRouter Image Generation

Generate images from text prompts using OpenRouter image generation models.

## Usage

```bash
python3 {baseDir}/scripts/generate.py --prompt "your prompt here"
```

### Options

- `--prompt` (required): Text prompt describing the image to generate
- `--output`: Output file path (default: auto-generated timestamp filename in workspace)
- `--model`: OpenRouter model ID (default: `google/gemini-2.5-flash-image`)
- `--aspect-ratio`: Aspect ratio, e.g. `1:1`, `16:9`, `9:16`, `3:2`, `4:3` (default: `1:1`)

### Examples

```bash
# Basic generation
python3 {baseDir}/scripts/generate.py --prompt "A beautiful iwana char fish swimming in a clear mountain stream"

# Specify output path and aspect ratio
python3 {baseDir}/scripts/generate.py --prompt "Mt. Fuji at sunset" --output /tmp/fuji.png --aspect-ratio 16:9
```

### Output

The script prints the absolute path to the generated PNG file on success. The agent should then use this path to share or attach the image.

### Supported Models

- `google/gemini-2.5-flash-image` (default, cheapest ~bash.039/image)
- `google/gemini-3.1-flash-image-preview` (extended aspect ratios)
- `google/gemini-3-pro-image-preview` (highest quality)

### Cost

Uses OpenRouter pay-per-token pricing. Gemini 2.5 Flash Image is approximately bash.039 per image. Not free, but very cheap.
