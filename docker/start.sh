podman run -v "/mnt/data/home/rsr/MasterThesis/:/home/psrahul/MasterThesis/"  --net=host --ipc=host --gpus all -ti --rm --name rsr_trainer docker.io/pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime   



apt-get update && apt-get install -y python3 python3-dev python3-pip  build-essential cmake \
    && pip3 install --no-cache-dir --upgrade pip setuptools

docker rm d24ff5be8b21bc25dab9a127b5b7f564b71d34af648d520c581c56517086e60b

podman commit d24ff5be8b21 rsr_trainer

chmod 777 -R MasterThesis/