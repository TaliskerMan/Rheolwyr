import xml.etree.ElementTree as ET
import base64
import os

svg_path = "data/icons/hicolor/scalable/apps/com.taliskerman.rheolwyr.svg"
output_dir = "data/icons/hicolor/512x512/apps"
output_path = os.path.join(output_dir, "com.taliskerman.rheolwyr.png")

os.makedirs(output_dir, exist_ok=True)

try:
    tree = ET.parse(svg_path)
    root = tree.getroot()
    # Find image tag. The namespace might be tricky.
    # Namespace map usually: { 'http://www.w3.org/2000/svg': '' }
    # But let's just iterate.
    
    image_data = None
    for elem in root.iter():
        if 'href' in elem.attrib:
             href = elem.attrib['href']
             if href.startswith('data:image/png;base64,'):
                 image_data = href.split('data:image/png;base64,')[1]
                 break
        # Also check xlink:href (with namespace)
        for k, v in elem.attrib.items():
            if 'href' in k and v.startswith('data:image/png;base64,'):
                image_data = v.split('data:image/png;base64,')[1]
                break
        if image_data:
            break
            
    if image_data:
        # Clean newlines if any
        image_data = image_data.replace('\n', '').replace('\r', '')
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        print(f"Successfully extracted PNG to {output_path}")
    else:
        print("Could not find base64 image data in SVG")
        exit(1)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
