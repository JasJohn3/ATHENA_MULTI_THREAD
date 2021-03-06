from __future__ import print_function
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
from torch.autograd import Variable
import os
import Generator as Gen
import Discriminator as Disc
import time
import datetime
import csv
from multiprocessing import Process


class Trainer:
    def __init__(self):
        self.Discrimintor = Disc.D()
        self.Generator = Gen.G()

    def Train(self):
        # Setting some hyperparameters
        batchSize = 64  # We set the size of the batch.
        imageSize = 64  # We set the size of the generated images (64x64).

        # Creating the transformations
        transform = transforms.Compose([transforms.Resize(imageSize), transforms.ToTensor(),
                                        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5,
                                                                               0.5)), ])  # We create a list of transformations (scaling, tensor conversion, normalization) to apply to the input images.

        dataset = dset.CIFAR10(root='./Data', download=True,
                               transform=transform)  # We download the training set in the ./Data folder and we apply the previous transformations on each image.
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batchSize, shuffle=True,
                                                 num_workers=0)  # We use dataLoader to get the images of the training set batch by batch.

        # Defining the weights_init function that takes as input a neural network m and that will initialize all its weights.
        def weights_init(m):
            classname = m.__class__.__name__
            if classname.find('Conv') != -1:
                m.weight.data.normal_(0.0, 0.02)
            elif classname.find('BatchNorm') != -1:
                m.weight.data.normal_(1.0, 0.02)
                m.bias.data.fill_(0)
        # Creating the generator
        netG = self.Generator
        netG.apply(weights_init)
        # Creating the discriminator
        netD = self.Discrimintor
        netD.apply(weights_init)

        # Training the DCGANs
        criterion = nn.BCELoss()
        optimizerD = optim.Adam(netD.parameters(), lr=0.0002, betas=(0.5, 0.999))
        optimizerG = optim.Adam(netG.parameters(), lr=0.0002, betas=(0.5, 0.999))
        #Total Training will take an input from the user and set the total number of epochs to complete.
        Total_Training = 30
        #opening or creating the Neural Network Loss log. If file exists, overwrites the file for a new session.
        file = open("Neural Network Loss.txt", "w")


        for epoch in range(Total_Training):

            for i, data in enumerate(dataloader, 0):
                #initiating a timer to determine estimated completion time
                start = time.time()
                # 1st Step: Updating the weights of the neural network of the discriminator

                netD.zero_grad()

                # Training the discriminator with a real image of the dataset
                real, _ = data
                input = Variable(real)
                target = Variable(torch.ones(input.size()[0]))
                output = netD(input)
                errD_real = criterion(output, target)

                # Training the discriminator with a fake image generated by the generator
                noise = Variable(torch.randn(input.size()[0], 100, 1, 1))
                fake = netG(noise)
                target = Variable(torch.zeros(input.size()[0]))
                output = netD(fake.detach())
                errD_fake = criterion(output, target)

                # Backpropagating the total error
                errD = errD_real + errD_fake
                errD.backward()
                optimizerD.step()

                # 2nd Step: Updating the weights of the neural network of the generator

                netG.zero_grad()
                target = Variable(torch.ones(input.size()[0]))
                output = netD(fake)
                errG = criterion(output, target)
                errG.backward()
                optimizerG.step()

                # 3rd Step: Printing the losses and saving the real images and the generated images of the minibatch every 100 steps
                print('[%d/%d][%d/%d] Loss_D: %.4f Loss_G: %.4f' % (epoch, Total_Training, i, len(dataloader), errD.item(), errG.item()))

                ###############################################   Real and Fake Image File Storage    ###############################################
                if i % 100 == 0:
                    if not os.path.exists('./results'):
                        os.makedirs('./results')
                    vutils.save_image(real, '%s/real_samples.png' % "./results", normalize=True)
                    fake = netG(noise)
                    vutils.save_image(fake.data, '%s/fake_samples_epoch_%03d.png' % ("./results", epoch), normalize=True)

                ###############################################   Real and Fake Image File Storage    ###############################################

                ###############################################   Estimated Time    ###############################################

                #ending the timer to create our estimated completion times
                end = time.time()
                #One Epoch = len(DataLoader)
                Epoch = len(dataloader)
                #calculating the epoch trainging time
                epoch_time = len(dataloader) * (end-start)
                epoch_time = datetime.timedelta(seconds=epoch_time)
                #printing the estimated time of completion for one epoch
                print("Estimated Time too Epoch Completion: {:0>8}".format(str(epoch_time)))
                #estimating the completion time for all epochs entered by the user
                Total_Training_Time = epoch_time * Total_Training
                #printing the estimation to the screen for total training
                print("Estimated Time too Training Completion: {:0>8}".format(str(Total_Training_Time)))

                ###############################################   Estimated Time    ###############################################

                ###############################################   Text FILE    ###############################################

                # Appending the Neural Network Loss Log
                file = open("Neural Network Loss.txt", "a+")
                file.write('[%d/%d][%d/%d] Loss_D: %.4f Loss_G: %.4f' % (epoch, Total_Training, i, len(dataloader), errD.item(), errG.item()))
                file.write("\nEstimated Time too Epoch Completion: {:0>8}".format(str(epoch_time)))
                file.write("\nEstimated Time too Training Completion: {:0>8}\n\n".format(str(Total_Training_Time)))
                #Closing Neural Network Loss Log
                file.close()

                ###############################################   Text FILE    ###############################################

                ###############################################   CSV FILE    ###############################################

                with open('ATHENA.csv', 'w', encoding='utf8', newline='') as CSV_file:
                    fieldnames = ['Current_Step', 'Epoch', 'Current_Epoch', 'Total_Training', 'Epoch_Time','Total_Training']
                    writer = csv.DictWriter(CSV_file, fieldnames=fieldnames)
                    writer.writeheader()
                    ATHENA_DICT = {}
                    ATHENA_DICT = {'Current_Step':i, 'Epoch':Epoch, 'Current_Epoch':epoch,'Total_Training':Total_Training,'Epoch_Time':str(epoch_time), 'Total_Training':str(Total_Training_Time)}
                    print(ATHENA_DICT)
                    writer.writerow(ATHENA_DICT)
                CSV_file.close()

                ###############################################   CSV FILE    ###############################################
