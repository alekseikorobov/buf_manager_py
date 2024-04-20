
from PIL import Image
import imagehash
import os

class DuplicatedImageService:
  def __init__(self, path_db):
    self.path_db = path_db
    self.image_hashes = []
    self.init_data()


  def init_data(self):
    if os.path.exists(self.path_db):
      with open(self.path_db) as f:
        for line in f:
          image_hash = line.strip()
          self.image_hashes.append(image_hash)


  def is_duplicated(self,image):
    img_hash = imagehash.average_hash(image)
    return f'{img_hash}' in self.image_hashes

  def add_image(self,image):
    img_hash = imagehash.average_hash(image)
    self.image_hashes.append(f'{img_hash}')
    with open(self.path_db, 'a') as f:
      f.write(f'{img_hash}\n')
        
if __name__ == "__main__":
  service = DuplicatedImageService("duplicated_images.txt")
  image1 = Image.open(r"c:\Users\aakorobov\Pictures\Screenshots\image_20240417_084517.png")

  if not service.is_duplicated(image1):
    service.add_image(image1)
    print("Not duplicated")
  else:
    print("Duplicated")

  if not service.is_duplicated(image1):
    service.add_image(image1)
    print("Not duplicated")
  else:
    print("Duplicated")