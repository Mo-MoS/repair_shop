#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    pics_dir = "rc505mk1/pics"
    thumb_dir = "rc505mk1/thumbnails"
    readme_path = "README.md"

    if not os.path.exists(pics_dir):
        print(f"Error: Directory {pics_dir} does not exist.")
        sys.exit(1)

    os.makedirs(thumb_dir, exist_ok=True)

    # Get sorted files
    files = sorted(os.listdir(pics_dir))
    
    html_lines = []
    html_lines.append("## RC-505 Mk1 Photo Gallery\n")
    html_lines.append("<table>")
    
    row_items = []
    cols = 4  # Number of columns in grid

    for filename in files:
        src_path = os.path.join(pics_dir, filename)
        if not os.path.isfile(src_path):
            continue

        lower_name = filename.lower()
        if not (lower_name.endswith('.jpg') or lower_name.endswith('.jpeg') or lower_name.endswith('.mp4')):
            continue

        # Thumbnail name is always .jpg for simplicity
        thumb_name = os.path.splitext(filename)[0] + "_thumb.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_name)

        print(f"Processing {filename}...")

        # Generate thumbnail if it doesn't exist
        if not os.path.exists(thumb_path):
            if lower_name.endswith('.mp4'):
                # Extract first frame and scale
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", "00:00:01",
                    "-i", src_path,
                    "-vframes", "1",
                    "-vf", "scale=300:-1",
                    thumb_path
                ]
            else:
                # Resize image
                cmd = [
                    "convert",
                    src_path,
                    "-resize", "300x300",
                    thumb_path
                ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  Created thumbnail: {thumb_path}")
            except subprocess.CalledProcessError as e:
                print(f"  Failed to generate thumbnail for {filename}: {e}")
                continue
        else:
            print(f"  Thumbnail already exists: {thumb_path}")

        # Add to row items
        # Use relative paths for markdown rendering in GitHub
        rel_src = f"rc505mk1/pics/{filename}"
        rel_thumb = f"rc505mk1/thumbnails/{thumb_name}"
        
        # Clean label (e.g. without extension and underscores replaced with spaces)
        label = os.path.splitext(filename)[0].replace('_', ' ')

        cell_html = (
            f'    <td align="center" valign="bottom" width="200">\n'
            f'      <a href="{rel_src}">\n'
            f'        <img src="{rel_thumb}" width="180" alt="{label}" /><br/>\n'
            f'        <sub>{label}</sub>\n'
            f'      </a>\n'
            f'    </td>'
        )
        row_items.append(cell_html)

    # Chunk rows into lists of length `cols`
    for i in range(0, len(row_items), cols):
        chunk = row_items[i:i+cols]
        html_lines.append("  <tr>")
        html_lines.extend(chunk)
        # Pad with empty cells if row is not full
        if len(chunk) < cols:
            for _ in range(cols - len(chunk)):
                html_lines.append('    <td width="200"></td>')
        html_lines.append("  </tr>")

    html_lines.append("</table>\n")

    gallery_content = "\n".join(html_lines)

    # Read original README
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "# repair_shop\nDocumenting the repair jobs for friends broken hardware\n"

    # Remove existing gallery if rerun
    gallery_start_marker = "## RC-505 Mk1 Photo Gallery"
    if gallery_start_marker in content:
        content = content.split(gallery_start_marker)[0].strip() + "\n\n"
    else:
        content = content.strip() + "\n\n"

    new_content = content + gallery_content

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("README.md updated successfully with the gallery!")

if __name__ == "__main__":
    main()
