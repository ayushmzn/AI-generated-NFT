# -*- coding: utf-8 -*-
"""final_gan_model_(10).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18FAozrB-RNgzPbra0aEPxAzvBmN9SqAP
"""

gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)
if gpu_info.find('failed') >= 0:
  print('Not connected to a GPU')
else:
  print(gpu_info)

from google.colab import drive
drive.mount('/content/drive')

from keras.preprocessing.image import ImageDataGenerator, img_to_array, array_to_img, load_img
datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

import os
path = '/content/drive/MyDrive/mutant_ape_yacht_club/hd_images'
images = os.listdir(path) 
print(len(images))
dir = str(path)
for img in images:
  image_path = dir + str('/') + img
  image = load_img(image_path)
  x = img_to_array(image)
  x = x.reshape((1,) + x.shape)
  i = 0
  for batch in datagen.flow(x, batch_size=1, save_to_dir='/content/drive/MyDrive/mutant_ape_generated_images/images', save_prefix='img', save_format='jpeg'):
    i+=1
    if i>100:
      break

import os
mutate_ape_gen = '/content/drive/MyDrive/mutate_ape_generated_images/images'
print('mutate ape gen : ', len(os.listdir(mutate_ape_gen)))
mutate_ape = '/content/drive/MyDrive/mutant_ape_yacht_club/hd_images'
print('mutate ape  : ', len(os.listdir(mutate_ape)))
clone_x_gen = '/content/drive/MyDrive/clone_x_generated_images/images'
print('clone_x_gen : ', len(os.listdir(clone_x_gen)))
clone_x = '/content/drive/MyDrive/clone_x/hd_images'
print('clone_x : ', len(os.listdir(clone_x)))
crptopunks_gen = '/content/drive/MyDrive/crptopunks_generated_images/images'
print('crptopunks_gen : ', len(os.listdir(crptopunks_gen)))
crptopunks = '/content/drive/MyDrive/cryptopunks/hd_images'
print('crptopunks : ', len(os.listdir(crptopunks)))
tasty_bones_gen = '/content/drive/MyDrive/tasty_bones_generated_images/images'
print('tasty_bones_gen : ', len(os.listdir(tasty_bones_gen)))
tasty_bones = '/content/drive/MyDrive/tasty_bones/hd_images'
print('tasty_bones : ', len(os.listdir(tasty_bones)))

from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import torchvision.transforms as T

image_size = 64
batch_size = 128
stats = (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)

d1 = '/content/drive/MyDrive/mutate_ape_generated_images'
d2 = '/content/drive/MyDrive/mutant_ape_yacht_club'
d3 = '/content/drive/MyDrive/clone_x_generated_images'
d4 = '/content/drive/MyDrive/clone_x'
d5 = '/content/drive/MyDrive/crptopunks_generated_images'
d6 = '/content/drive/MyDrive/cryptopunks'
d7 = '/content/drive/MyDrive/tasty_bones_generated_images'
d8 = '/content/drive/MyDrive/tasty_bones'

dir_list = [d1,d2,d3,d4,d5,d6,d7,d8]

all_readed_images = []
for dir in dir_list:
  train_ds = ImageFolder(dir, transform=T.Compose([
    T.Resize(image_size),
    T.CenterCrop(image_size),
    T.ToTensor(),
    T.Normalize(*stats)]))
  all_readed_images.append(train_ds)

all_image_data = all_readed_images[0] + all_readed_images[1] + all_readed_images[2] + all_readed_images[3] + all_readed_images[4] + all_readed_images[5] + all_readed_images[6] + all_readed_images[7]

len(all_image_data)

train_dl = DataLoader(all_image_data, batch_size, shuffle=True, num_workers=3, pin_memory=True)

dataiter = iter(train_dl)
images, labels = dataiter.next()
print(type(images))
print(images.shape)
print(labels.shape)

# Commented out IPython magic to ensure Python compatibility.
import torch
from torchvision.utils import make_grid
import matplotlib.pyplot as plt
# %matplotlib inline

def denorm(img_tensors):
    return img_tensors * stats[1][0] + stats[0][0]

def show_images(images, nmax=64):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xticks([]); ax.set_yticks([])
    ax.imshow(make_grid(denorm(images.cpu().detach()[:nmax]), nrow=8).permute(1, 2, 0))

def show_batch(dl, nmax=64):
    for images, _ in dl:
        show_images(images, nmax)
        break

show_batch(train_dl)

def get_default_device():
    """Pick GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')
    
def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

class DeviceDataLoader():
    """Wrap a dataloader to move data to a device"""
    def __init__(self, dl, device):
        self.dl = dl
        self.device = device
        
    def __iter__(self):
        """Yield a batch of data after moving it to device"""
        for b in self.dl: 
            yield to_device(b, self.device)

    def __len__(self):
        """Number of batches"""
        return len(self.dl)

device = get_default_device()
device

train_dl = DeviceDataLoader(train_dl, device)

from torchsummary import summary

import torch.nn as nn

discriminator = nn.Sequential(
    # in: 3 x 64 x 64

    nn.Conv2d(3, 64, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(64),
    nn.LeakyReLU(0.2, inplace=True),
    # out: 64 x 32 x 32

    nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(128),
    nn.LeakyReLU(0.2, inplace=True),
    # out: 128 x 16 x 16

    nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(256),
    nn.LeakyReLU(0.2, inplace=True),
    # out: 256 x 8 x 8

    nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(512),
    nn.LeakyReLU(0.2, inplace=True),
    # out: 512 x 4 x 4

    nn.Conv2d(512, 1, kernel_size=4, stride=1, padding=0, bias=False),
    # out: 1 x 1 x 1

    nn.Flatten(),
    nn.Sigmoid())

discriminator = to_device(discriminator, device)

summary(discriminator, (3,64,64))

latent_size = 256

generator = nn.Sequential(
    # in: latent_size x 1 x 1

    nn.ConvTranspose2d(latent_size, 512, kernel_size=4, stride=1, padding=0, bias=False),
    nn.BatchNorm2d(512),
    nn.ReLU(True),
    # out: 512 x 4 x 4

    nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(256),
    nn.ReLU(True),
    # out: 256 x 8 x 8

    nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(128),
    nn.ReLU(True),
    # out: 128 x 16 x 16

    nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1, bias=False),
    nn.BatchNorm2d(64),
    nn.ReLU(True),
    # out: 64 x 32 x 32

    nn.ConvTranspose2d(64, 3, kernel_size=4, stride=2, padding=1, bias=False),
    nn.Tanh()
    # out: 3 x 64 x 64
)

print(generator)

print(discriminator)

xb = torch.randn(batch_size, latent_size, 1, 1) # random latent tensors
fake_images = generator(xb)
print(fake_images.shape)
show_images(fake_images)

generator = to_device(generator, device)

summary(generator, (256,1,1))

def train_discriminator(real_images, opt_d):
    # Clear discriminator gradients
    opt_d.zero_grad()

    # Pass real images through discriminator
    real_preds = discriminator(real_images)
    real_targets = torch.ones(real_images.size(0), 1, device=device)
    real_loss = F.binary_cross_entropy(real_preds, real_targets)
    real_score = torch.mean(real_preds).item()
    
    # Generate fake images
    latent = torch.randn(batch_size, latent_size, 1, 1, device=device)
    fake_images = generator(latent)

    # Pass fake images through discriminator
    fake_targets = torch.zeros(fake_images.size(0), 1, device=device)
    fake_preds = discriminator(fake_images)
    fake_loss = F.binary_cross_entropy(fake_preds, fake_targets)
    fake_score = torch.mean(fake_preds).item()

    # Update discriminator weights
    loss = real_loss + fake_loss
    loss.backward()
    opt_d.step()
    return loss.item(), real_score, fake_score

def train_generator(opt_g):
      
    # Clear generator gradients
    opt_g.zero_grad()
    
    # Generate fake images
    latent = torch.randn(batch_size, latent_size, 1, 1, device=device)
    fake_images = generator(latent)
    
    # Try to fool the discriminator
    preds = discriminator(fake_images)
    targets = torch.ones(batch_size, 1, device=device)
    loss = F.binary_cross_entropy(preds, targets)
    
    # Update generator weights
    loss.backward()
    opt_g.step()
    
    return loss.item()

from torchvision.utils import save_image

sample_dir = '/content/drive/MyDrive/k3_images'
#os.makedirs(sample_dir, exist_ok=True)

def save_samples(index, latent_tensors, show=True):
    fake_images = generator(latent_tensors)
    print(fake_images.shape)
    fake_fname = 'generated-images-{0:0=4d}.png'.format(index)
    save_image(denorm(fake_images), os.path.join(sample_dir, fake_fname), nrow=8)
    print('Saving', fake_fname)
    if show:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xticks([]); ax.set_yticks([])
        ax.imshow(make_grid(fake_images.cpu().detach(), nrow=8).permute(1, 2, 0))

fixed_latent = torch.randn(64, latent_size, 1, 1, device=device)

save_samples(0, fixed_latent)

from tqdm.notebook import tqdm
import torch.nn.functional as F

def fit(epochs, lr, start_idx=1):

    
    torch.cuda.empty_cache()
    # Losses & scores
    losses_g = []
    losses_d = []
    real_scores = []
    fake_scores = []
    
    # Create optimizers
    opt_d = torch.optim.Adam(discriminator.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_g = torch.optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
    
    for epoch in range(epochs):
      

      
      for real_images, _ in tqdm(train_dl):

          # Train discrimina
        loss_d, real_score, fake_score = train_discriminator(real_images, opt_d)
            # Train generator
        loss_g = train_generator(opt_g)
            
        # Record losses & scores
      losses_g.append(loss_g)
      losses_d.append(loss_d)
      real_scores.append(real_score)
      fake_scores.append(fake_score)
        
        # Log losses & scores (last batch)
      print("Epoch [{}/{}], loss_g: {:.4f}, loss_d: {:.4f}, real_score: {:.4f}, fake_score: {:.4f}".format(
            epoch+1, epochs, loss_g, loss_d, real_score, fake_score))
    
        # Save generated images
      save_samples(epoch+start_idx, fixed_latent, show=False)
      if (epoch+1)%10 == 0:

        dis_path = '/content/drive/MyDrive/k3_disc_wth' + '/save_dis_model' + str(epoch+1) + '.pth'
        gen_path = '/content/drive/MyDrive/k3_gen_wht'  + '/save_gen_model' + str(epoch+1) + '.pth'
        torch.save(generator.state_dict(), gen_path)
        torch.save(discriminator.state_dict(), dis_path)
        print('saved model weight for epoch : ', epoch+1)



    
    return losses_g, losses_d, real_scores, fake_scores

lr = 0.0002
epochs = 2000

history = fit(epochs, lr)



x = torch.rand(128,128,1,1, device=device)
img = generator(x)

show_images(img)

x = torch.rand(1,128,1,1, device=device)
img=generator(x)
img=img.reshape(3,64,64)
plt.imshow(denorm(img.cpu().detach().permute(1,2,0)))

"""to print weights"""

#for i in generator.parameters():
 # print(i)

"""to load weights"""

#generator.load_state_dict(torch.load('/content/drive/MyDrive/gen_model/save_gen_model9.pth'))

