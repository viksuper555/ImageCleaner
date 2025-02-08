import collections
import os
import hashlib
import io

from PIL import Image


class ImagePreprocessor:
    data_path: str = None
    files: [str] = None

    def __init__(self, data_path):
        self.data_path = data_path
        self.files = os.listdir(data_path)

    def deduplicate_group(self, files: set[str]):
        keep = None
        for file in files:
            if keep is None:
                keep = file
                continue
            self.delete_file(file)

    def delete_file(self, name):
        if not os.path.exists(os.path.join(self.data_path, name)):
            return
        os.remove(os.path.join(self.data_path, name))

    def find_all_duplicates(self):
        unique_set = {}
        duplicates = collections.defaultdict(set)
        for file in self.files:
            file_hash = self.get_hash(file)
            if file_hash in unique_set:
                duplicates[file_hash].add(unique_set[file_hash])
                duplicates[file_hash].add(file)
            else:
                unique_set[self.get_hash(file)] = file
        return duplicates

    def yield_similar(self, name):
        current = self.get_hash(name)

        for file in self.files:
            if file == name:
                continue

            if current == self.get_hash(file):
                yield file

    def get_hash(self, name):
        return ImagePreprocessor._hash(self._load(name))

    def _load(self, name) -> Image:
        img = Image.open(os.path.join(self.data_path, name)).convert("RGB")
        return img

    @staticmethod
    def _hash(image, fmt="JPEG"):
        with io.BytesIO() as buffer:
            image.save(buffer, format=fmt)
            image_bytes = buffer.getvalue()
        return hashlib.md5(image_bytes).hexdigest()


if __name__ == "__main__":
    image_preprocessor = ImagePreprocessor("data")
    # print(image_preprocessor.get_hash("image_293.jpg"))
    # print(image_preprocessor.get_hash("image_293_copy.jpg"))

    # print([x for x in image_preprocessor.yield_similar("image_293.jpg")])
    dups = image_preprocessor.find_all_duplicates()
    print(dups)
