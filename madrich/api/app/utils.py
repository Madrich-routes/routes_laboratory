import os
import uuid
from typing import Optional


def save_file(request, path) -> Optional[str]:
    if 'file' not in request.files:
        return None
    file = request.files['file']
    if file.filename == '':
        return None
    if file:
        filename = str(uuid.uuid4())

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        file.save(os.path.join(path, filename))
        return filename
    return None
