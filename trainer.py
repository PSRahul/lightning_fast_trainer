from asyncio.log import logger
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning import Trainer
import sys
import pytorch_lightning as pl
import os
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from datetime import datetime

now = datetime.now()


class LightningTrainer:
    def __init__(self, cfg):
        date_save_string = now.strftime("%d%m%Y_%H%M")

        checkpoint_dir = os.path.join(
            cfg["trainer"]["checkpoint_dir"], date_save_string
        )
        logger = TensorBoardLogger(checkpoint_dir, name=cfg["trainer"]["exp_name"])

        self.trainer = pl.Trainer(
            enable_checkpointing=True,
            logger=logger,
            accelerator="gpu",
            devices=1,
            callbacks=[EarlyStopping(monitor="val_loss", mode="min")],
            max_epochs=cfg["trainer"]["max_epochs"],
            default_root_dir=checkpoint_dir,
        )

    def tune_learning_rate(self, model, data):
        lr_finder = self.trainer.tuner.lr_find(
            model=model,
            train_dataloaders=data.train_dataloader(),
            val_dataloaders=data.val_dataloader(),
        )