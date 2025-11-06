# API Documentation

This document provides detailed information about all three API generators integrated into the Streamlit application.

## Overview

The application now includes **three powerful AI image generation APIs**:

1. **Image Edit API** (`qwen/image-edit`) - Edit existing images with AI
2. **Nano Banana API** (`google/nano-banana`) - Generate images from text prompts
3. **Character Edit API** (`ideogram/character-edit`) - Edit characters with consistency using masks and references

All APIs share the same authentication method and base URL, making integration seamless.

---

## 1. Image Edit API (qwen/image-edit)

### Page: 🎨 API Testing

**Purpose**: Edit and transform existing images using AI-powered modifications based on text prompts.

### Key Features
- Edit existing images with text prompts
- Control generation parameters (steps, guidance scale, etc.)
- Multiple image size options
- Acceleration modes for faster generation
- Safety checker for content moderation
- Auto-save to Google Drive

### Input Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `prompt` | string | Yes | The prompt to generate the image with | "" |
| `image_url` | string | Yes | The URL of the image to edit | - |
| `acceleration` | string | No | Acceleration level (none/regular/high) | "none" |
| `image_size` | string | No | Size of generated image | "landscape_4_3" |
| `num_inference_steps` | number | No | Number of inference steps (2-49) | 25 |
| `guidance_scale` | number | No | CFG scale (0-20) | 4 |
| `seed` | number | No | Random seed for reproducibility | - |
| `num_images` | string | No | Number of images to generate (1-4) | - |
| `enable_safety_checker` | boolean | No | Enable safety checker | true |
| `output_format` | string | No | Output format (png/jpeg) | "png" |
| `negative_prompt` | string | No | What to avoid in generation | "blurry, ugly" |

### Image Size Options
- `square` - Square format
- `square_hd` - Square HD format
- `portrait_4_3` - Portrait 3:4 ratio
- `portrait_16_9` - Portrait 9:16 ratio
- `landscape_4_3` - Landscape 4:3 ratio
- `landscape_16_9` - Landscape 16:9 ratio

### Use Cases
- Photo editing and enhancement
- Style transfer
- Image-to-image transformations
- Object replacement or modification
- Background changes

---

## 2. Nano Banana API (google/nano-banana)

### Page: 🍌 Nano Banana

**Purpose**: Generate high-quality images from text descriptions using Google's Nano Banana model.

### Key Features
- Text-to-image generation
- Multiple aspect ratios
- Simple and intuitive interface
- Fast generation times
- Example prompts included
- Auto-save to Google Drive

### Input Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `prompt` | string | Yes | The prompt for image generation (max 5000 chars) | - |
| `output_format` | string | No | Output format (png/jpeg) | "png" |
| `image_size` | string | No | Aspect ratio | "1:1" |

### Image Size Options
- `1:1` - Square (social media, avatars)
- `9:16` - Portrait vertical (mobile screens, stories)
- `16:9` - Landscape wide (desktop wallpapers, presentations)
- `3:4` - Portrait (photo prints)
- `4:3` - Landscape (classic displays)
- `3:2` - Landscape (photography standard)
- `2:3` - Portrait (photography standard)
- `5:4` - Landscape (medium format)
- `4:5` - Portrait (medium format)
- `21:9` - Ultra-wide (cinematic, panoramic)
- `auto` - Automatic (model decides)

### Example Prompts
1. "A surreal painting of a giant banana floating in space, stars and galaxies in the background, vibrant colors, digital art"
2. "A photorealistic banana wearing sunglasses on a tropical beach at sunset"
3. "An abstract geometric composition with bananas in neon colors, cyberpunk style"
4. "A banana dressed as a superhero flying through a city skyline, comic book art"
5. "A minimalist illustration of a banana on a pastel background, modern design"
6. "A steampunk mechanical banana with gears and brass components, detailed rendering"

### Use Cases
- Creative artwork generation
- Concept art and illustrations
- Social media content
- Marketing materials
- Digital art projects
- Rapid prototyping of visual ideas

---

## 3. Character Edit API (ideogram/character-edit)

### Page: 👤 Character Edit

**Purpose**: Edit characters in images while maintaining consistency using masks and reference images.

### Key Features
- Character-consistent editing
- Mask-based inpainting
- Reference image support
- Multiple style options
- Rendering speed control
- MagicPrompt expansion
- Auto-save to Google Drive

### Input Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `prompt` | string | Yes | Prompt to fill the masked part (max 5000 chars) | - |
| `image_url` | string | Yes | The image URL to generate from | - |
| `mask_url` | string | Yes | The mask URL to inpaint the image | - |
| `reference_image_urls` | array | Yes | Character reference images (max 1 used) | - |
| `rendering_speed` | string | No | Speed vs quality (TURBO/BALANCED/QUALITY) | "BALANCED" |
| `style` | string | No | Style type (AUTO/REALISTIC/FICTION) | "AUTO" |
| `expand_prompt` | boolean | No | Use MagicPrompt enhancement | true |
| `num_images` | string | No | Number of images (1-4) | "1" |
| `seed` | number | No | Random seed for reproducibility | - |

### Rendering Speed Options
- `TURBO` - Fastest generation (quick iterations, testing)
- `BALANCED` - Good balance of speed and quality (most use cases)
- `QUALITY` - Highest quality output (final renders)

### Style Options
- `AUTO` - Automatically determines the best style
- `REALISTIC` - Photorealistic style
- `FICTION` - Fictional/artistic style

### How It Works
1. **Base Image**: The original image you want to edit
2. **Mask Image**: A mask indicating which parts to regenerate (white = edit, black = keep)
3. **Reference Image**: A character reference to maintain consistency

The model fills in the masked areas while maintaining the character's appearance from the reference image.

### Use Cases
- Character pose changes
- Facial expression modifications
- Outfit/clothing changes
- Background replacement with character consistency
- Character variations for animation/games
- Consistent character generation across scenes

---

## Common Features Across All APIs

### Authentication
All APIs use the same authentication method:
- **Header**: `Authorization: Bearer YOUR_API_KEY`
- **API Key**: Obtained from [kie.ai/api-key](https://kie.ai/api-key)

### Task Flow
1. **Create Task**: Submit generation request
2. **Get Task ID**: Receive unique task identifier
3. **Poll Status**: Check task progress
4. **Retrieve Results**: Download generated images

### Auto-Save to Google Drive
All three API generators support automatic saving of results to Google Drive:
- Enable "Auto-save results to Google Drive" checkbox
- Optionally specify a custom folder
- Images are saved with unique filenames including task ID
- Supports both default and custom folders

### Error Handling
All APIs return standard error codes:
- `200` - Request successful
- `400` - Invalid request parameters
- `401` - Authentication failed
- `402` - Insufficient account balance
- `404` - Resource not found
- `422` - Parameter validation failed
- `429` - Request rate limit exceeded
- `500` - Internal server error

---

## API Helper Module

The application includes a comprehensive API helper module (`api_helper.py`) with the following classes:

### BaseAPIClient
Base class providing common functionality:
- `create_task()` - Create generation tasks
- `query_task()` - Query task status
- `wait_for_completion()` - Wait for task completion with polling
- `get_result_urls()` - Extract result URLs from task info

### ImageEditAPI
Specialized client for Image Edit API:
- `create_image_edit_task()` - Create image editing tasks

### NanoBananaAPI
Specialized client for Nano Banana API:
- `create_nano_banana_task()` - Create text-to-image tasks

### CharacterEditAPI
Specialized client for Character Edit API:
- `create_character_edit_task()` - Create character editing tasks

---

## Best Practices

### Prompt Engineering
1. **Be Specific**: Include details about style, colors, mood, and composition
2. **Use Art Styles**: Mention specific styles like "digital art", "oil painting", "photorealistic"
3. **Add Context**: Describe setting, lighting, and atmosphere
4. **Experiment**: Try different variations to find what works best
5. **Length Matters**: Longer, detailed prompts often produce better results

### Image Quality
1. **Use High-Resolution Inputs**: Better input images produce better results
2. **Match Dimensions**: Ensure base images and masks have matching dimensions
3. **Quality References**: Use high-quality reference images for character consistency
4. **Appropriate Settings**: Balance speed and quality based on your needs

### Resource Management
1. **Monitor API Credits**: Keep track of your API usage
2. **Use Auto-Save**: Enable Google Drive auto-save to preserve all results
3. **Organize Folders**: Use custom folders to organize different projects
4. **Test Settings**: Use faster settings for testing, quality settings for final renders

---

## Troubleshooting

### Common Issues

**"Failed to create task"**
- Check API key validity
- Verify internet connection
- Ensure sufficient API credits
- Check parameter validation

**"Task timeout"**
- Increase max_wait parameter
- Check task status manually
- Complex generations may take longer

**"Failed to load image"**
- Verify image URL is publicly accessible
- Check image format compatibility
- Ensure image size is within limits

**"Auto-save failed"**
- Verify Google Drive credentials
- Check folder permissions
- Ensure sufficient Drive storage

---

## Support and Resources

- **API Key Management**: [https://kie.ai/api-key](https://kie.ai/api-key)
- **Google Drive API**: [https://console.cloud.google.com](https://console.cloud.google.com)
- **Application Documentation**: See README.md and USAGE_GUIDE.md

---

## Summary

The Streamlit application now provides comprehensive access to three powerful AI image generation APIs, each optimized for different use cases:

- **Image Edit**: Transform and modify existing images
- **Nano Banana**: Generate new images from text descriptions
- **Character Edit**: Maintain character consistency across edits

All APIs are fully integrated with Google Drive for seamless storage and management of generated images.
