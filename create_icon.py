#!/usr/bin/env python3
"""Script to create a simple icon for BatePonto."""

import os
from pathlib import Path

# SVG icon content - simple clock/timer design
SVG_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="512" height="512" rx="90" fill="#2E7D32"/>

  <!-- Clock circle -->
  <circle cx="256" cy="256" r="180" fill="#FFFFFF" stroke="#1B5E20" stroke-width="8"/>

  <!-- Clock face marks -->
  <line x1="256" y1="96" x2="256" y2="116" stroke="#1B5E20" stroke-width="6" stroke-linecap="round"/>
  <line x1="256" y1="396" x2="256" y2="416" stroke="#1B5E20" stroke-width="6" stroke-linecap="round"/>
  <line x1="96" y1="256" x2="116" y2="256" stroke="#1B5E20" stroke-width="6" stroke-linecap="round"/>
  <line x1="396" y1="256" x2="416" y2="256" stroke="#1B5E20" stroke-width="6" stroke-linecap="round"/>

  <!-- Hour hand (pointing to 10) -->
  <line x1="256" y1="256" x2="200" y2="180" stroke="#1B5E20" stroke-width="12" stroke-linecap="round"/>

  <!-- Minute hand (pointing to 2) -->
  <line x1="256" y1="256" x2="340" y2="200" stroke="#1B5E20" stroke-width="10" stroke-linecap="round"/>

  <!-- Center dot -->
  <circle cx="256" cy="256" r="12" fill="#1B5E20"/>

  <!-- Play/Record indicator -->
  <circle cx="360" cy="140" r="35" fill="#FF5252"/>
  <circle cx="360" cy="140" r="25" fill="#FFFFFF"/>
  <circle cx="360" cy="140" r="15" fill="#FF5252"/>
</svg>'''

def create_icon():
    """Create icon files for macOS."""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # Save SVG
    svg_path = assets_dir / "icon.svg"
    with open(svg_path, 'w') as f:
        f.write(SVG_CONTENT)

    print(f"✓ Created SVG icon: {svg_path}")

    # Instructions for creating .icns
    print("\nPara criar o arquivo .icns para macOS:")
    print("1. Instale Inkscape: brew install inkscape")
    print("2. Execute:")
    print("   inkscape assets/icon.svg -o assets/icon.png -w 1024 -h 1024")
    print("   mkdir assets/icon.iconset")
    print("   sips -z 16 16 assets/icon.png --out assets/icon.iconset/icon_16x16.png")
    print("   sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_16x16@2x.png")
    print("   sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_32x32.png")
    print("   sips -z 64 64 assets/icon.png --out assets/icon.iconset/icon_32x32@2x.png")
    print("   sips -z 128 128 assets/icon.png --out assets/icon.iconset/icon_128x128.png")
    print("   sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_128x128@2x.png")
    print("   sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_256x256.png")
    print("   sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_256x256@2x.png")
    print("   sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_512x512.png")
    print("   cp assets/icon.png assets/icon.iconset/icon_512x512@2x.png")
    print("   iconutil -c icns assets/icon.iconset -o assets/icon.icns")
    print("\nOu use o script build_macos.sh que fará isso automaticamente!")

if __name__ == "__main__":
    create_icon()
