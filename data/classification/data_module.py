from cgi import test
import pytorch_lightning as pl
from torch.utils.data import random_split, DataLoader
from torchvision.datasets import ImageFolder
from torchvision import transforms
from typing import Optional

import os

class ClassificationDataModule(pl.LightningDataModule):

    def __init__(self, config,train_transforms,test_transforms):
        super().__init__()
        self.cfg = config
        self.train_transforms=train_transforms
        self.test_transforms=test_transforms
        self.prepare_data(train_transforms,test_transforms)

    def prepare_data(self,train_transforms,test_transforms):
        
        train_dataset=ImageFolder(
            root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["train_folder"]),
            transform=train_transforms
            )

        val_dataset=ImageFolder(
            root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["val_folder"]), 
            transform=test_transforms)

        test_dataset=ImageFolder(
            root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["test_folder"]), 
            transform=test_transforms)

        print("Datasets are Accessible")            
    
    def setup(self, stage: Optional[str] = None):

        # Assign train/val datasets for use in dataloaders
        if stage == "fit" or stage is None:
            self.train_dataset=ImageFolder(
            root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["train_folder"]),
            transform=self.train_transforms
            )

        val_dataset=ImageFolder(
            self.root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["val_folder"]), 
            transform=self.test_transforms
            )

        # Assign test dataset for use in dataloader(s)
        if stage == "test" or stage is None:
            self.test_dataset=ImageFolder(
            root=os.path.join(self.cfg["data"]["root_folder"],self.cfg["data"]["test_folder"]), 
            transform=self.test_transforms
            )

        
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=32)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=32)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=32)

    