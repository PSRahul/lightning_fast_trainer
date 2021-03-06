import sys
import tracemalloc
import yaml
from data.classification.data_module import ClassificationDataModule
from yaml.loader import SafeLoader
from network.models_pytorch import ResNet18Model, ResNet50Model, ViTB16Model
from trainer import LightningTrainer
from network.network_module import ClassificationModel
import argparse
import logging
import os
from datetime import datetime
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, default="config.yaml")
    args = parser.parse_args()
    return args


def load_config(config_file):
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=SafeLoader)

    return config


class Logger(object):
    def __init__(self, cfg, checkpoint_dir):
        # os.mknod(checkpoint_dir)
        self.terminal = sys.stdout
        self.log = open(checkpoint_dir, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


def main():
    args = get_args()
    cfg = load_config(args.c)
    now = datetime.now()
    date_save_string = now.strftime("%d%m%Y_%H%M")
    checkpoint_dir = os.path.join(
        "/home/psrahul/MasterThesis/repo/lightning_fast_trainer/",
        cfg["trainer"]["checkpoint_dir"],
        date_save_string,
    )
    os.makedirs(checkpoint_dir, exist_ok=True)

    if not cfg["test_model"]:
        log_file = os.path.join(checkpoint_dir, "log.log")
        sys.stdout = Logger(cfg, log_file)

    pytorch_model_name = globals()[cfg["model"]["name"]]
    pytorch_model = pytorch_model_name(cfg)
    logger_pytorch = logging.getLogger("pytorch_lightning")
    logger_optuna = logging.getLogger("optuna")

    if cfg["debug"]:
        print("Debug Mode Enabled")
        train_transforms = pytorch_model.get_sample_transforms()
        test_transforms = pytorch_model.get_sample_transforms()
    else:
        train_transforms = pytorch_model.get_train_transforms()
        test_transforms = pytorch_model.get_test_transforms()

    trainer = LightningTrainer(cfg, checkpoint_dir)
    logger_pytorch.addHandler(
        logging.FileHandler(os.path.join(trainer.checkpoint_dir, "trainer.log"))
    )
    logger_pytorch.addHandler(
        logging.FileHandler(os.path.join(trainer.checkpoint_dir, "optuna.log"))
    )

    data = ClassificationDataModule(
        config=cfg, train_transforms=train_transforms, test_transforms=test_transforms
    )
    data.setup()
    model = ClassificationModel(pytorch_model)

    if cfg["trainer"]["lr"] != str("None"):
        model.hparams.lr = float(cfg["trainer"]["lr"])
    else:
        model.hparams.lr = 1e-3

    if cfg["tune_model"]:
        model.hparams.lr = trainer.optuna_tune(
            pytorch_model_name,
            cfg,
            data,
        )
    print("Chosen Learning Rate", model.hparams.lr)

    if cfg["train_model"]:
        trainer.train(model, data)

    if cfg["test_model"]:
        print("Train Accuracy")
        trainer.trainer.test(
            model=model,
            dataloaders=data.train_for_eval_dataloader(),
            ckpt_path=cfg["test"]["ckpt_path"],
        )

        print("Validation Accuracy")
        trainer.trainer.test(
            model=model,
            dataloaders=data.val_dataloader(),
            ckpt_path=cfg["test"]["ckpt_path"],
        )

        print("Test Accuracy")
        trainer.trainer.test(
            model=model,
            dataloaders=data.test_dataloader(),
            ckpt_path=cfg["test"]["ckpt_path"],
        )


if __name__ == "__main__":
    sys.exit(main())
