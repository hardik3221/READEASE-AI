import base64
import os


def get_image_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def find_logo_path(base_dir, filename_hint="logo readora ai"):
    """Looks for the Readora logo in assets/ first, then the FrontEnd root
    (in case it hasn't been moved yet). Tries the exact filename with a few
    common extensions/casings first, then falls back to any image file in
    those folders whose name contains "logo" — so a slightly different
    filename or extension doesn't silently break it."""
    search_dirs = [os.path.join(base_dir, "assets"), base_dir]
    extensions = [".jpeg", ".jpg", ".png", ".JPEG", ".JPG", ".PNG"]

    for d in search_dirs:
        for ext in extensions:
            candidate = os.path.join(d, filename_hint + ext)
            if os.path.exists(candidate):
                return candidate

    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            lower = fname.lower()
            if "logo" in lower and lower.endswith((".jpeg", ".jpg", ".png")):
                return os.path.join(d, fname)

    return None