#!/usr/bin/env python3
"""
Generate placeholder icons for the CAJAL browser extension.
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    """Create a simple CAJAL neuron icon."""
    img = Image.new('RGBA', (size, size), (13, 33, 55, 255))
    draw = ImageDraw.Draw(img)
    
    # Background circle
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], 
                 outline=(244, 162, 97, 255), width=max(2, size // 32))
    
    # Center node (soma)
    center = size // 2
    node_radius = max(4, size // 16)
    draw.ellipse([center - node_radius, center - node_radius - size//10,
                  center + node_radius, center + node_radius - size//10],
                 fill=(244, 162, 97, 255))
    
    # Dendrites (top)
    for angle in [-30, -10, 10, 30]:
        import math
        rad = math.radians(angle)
        x1 = center
        y1 = center - size//10
        x2 = center + int(math.sin(rad) * size * 0.3)
        y2 = center - size//10 - int(math.cos(rad) * size * 0.25)
        draw.line([(x1, y1), (x2, y2)], fill=(244, 162, 97, 200), width=max(1, size // 64))
        # End node
        end_r = max(2, size // 32)
        draw.ellipse([x2 - end_r, y2 - end_r, x2 + end_r, y2 + end_r], 
                     fill=(244, 162, 97, 180))
    
    # Axon (bottom)
    draw.line([(center, center + node_radius - size//10), 
               (center, center + size//3)], 
              fill=(244, 162, 97, 200), width=max(2, size // 48))
    
    # Axon branches
    for angle in [150, 180, 210]:
        import math
        rad = math.radians(angle)
        x1 = center
        y1 = center + size//3
        x2 = center + int(math.sin(rad) * size * 0.15)
        y2 = center + size//3 + int(math.cos(rad) * size * 0.15)
        draw.line([(x1, y1), (x2, y2)], fill=(244, 162, 97, 180), width=max(1, size // 64))
    
    return img

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(base_dir, '..', '..', 'ecosystem', 'browser-extension', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    sizes = [16, 32, 48, 128]
    for size in sizes:
        icon = create_icon(size)
        icon.save(os.path.join(icons_dir, f'icon{size}.png'))
        print(f"Created icon{size}.png")
    
    print(f"\nIcons saved to: {icons_dir}")

if __name__ == "__main__":
    main()
