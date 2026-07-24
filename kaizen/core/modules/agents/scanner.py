import os

from kaizen.core.modules.agents.backend import ServiceClass
from kaizen.core.modules.Schemas import FileInfo, ProjectSnapshot
from utils import IGNORE_DIRS, IGNORE_EXTENSIONS, IGNORE_FILES


class ScannerService(ServiceClass):
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.abs_path = os.path.abspath(root_dir)

        self.files_list = []
        self.dirs_list = []

    def invoke(self) -> ProjectSnapshot:
        self.files_list = []
        self.dirs_list = []
        try:
            for root, dirs, files in os.walk(self.root_dir):
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

                for d in dirs:
                    dir_abs_path = os.path.join(root, d)

                    dir_rel_path = os.path.relpath(dir_abs_path, self.abs_path).replace(
                        "\\", "/"
                    )

                    self.dirs_list.append(dir_rel_path)

                for file in files:
                    if file in IGNORE_FILES:
                        continue

                    ext = os.path.splitext(file)[1].lower()

                    if ext in IGNORE_EXTENSIONS:
                        continue

                    file_abs_path = os.path.join(root, file)

                    file_rel_path = os.path.relpath(
                        file_abs_path, self.abs_path
                    ).replace("\\", "/")
                    try:
                        file_size = os.path.getsize(file_abs_path)

                        with open(
                            file_abs_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            lines_count = sum(1 for _ in f)

                    except OSError:
                        continue

                    self.files_list.append(
                        FileInfo(
                            path=file_rel_path,
                            extension=ext,
                            size_bytes=file_size,
                            lines_count=lines_count,
                        )
                    )

            return ProjectSnapshot(
                root_path=self.abs_path,
                files=self.files_list,
                directories=self.dirs_list,
                total_files=len(self.files_list),
                total_directories=len(self.dirs_list),
            )
        except Exception:
            return ProjectSnapshot(
                root_path=self.abs_path,
                files=[],
                directories=[],
                total_files=0,
                total_directories=0,
            )
