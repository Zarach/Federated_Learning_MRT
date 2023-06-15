import datetime
import os

from collections import OrderedDict

import torch
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

from mrt_code.make_dataset import make_data_shuffle, convert_data, split_data, update_xml


import flwr as fl

import numpy as np
from flask import Flask, request

from ultralytics import YOLO
from mrt_code.yolov5 import val


app = Flask(__name__)
SERVER_ADDRESS = "127.0.0.1:8080"
CLIENT_ID = 0
data_received = False

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# def eval_net(opt):
#     save_dir = increment_path(Path("runs/eval/") / opt.name)
#     os.mkdir(save_dir)
#
#     results, _, _ = val.run(
#         data=opt.data,
#         model=creation_of_the_model(opt),
#         device=opt.device,
#         save_dir=save_dir,
#         save_model=True,
#     )
#
#     return results

def load_data():
    """Load CIFAR-10 (training and test set)."""
    transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )
    make_data_shuffle.main()
    update_xml.main()
    convert_data.main()
    split_data.main()
    # trainset = CIFAR10(".", train=True, download=True, transform=transform)
    # testset = CIFAR10(".", train=False, download=True, transform=transform)
    #trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    #testloader = DataLoader(testset, batch_size=32)
    # num_examples = {"trainset" : len(trainset), "testset" : len(testset)}
    # return trainloader, testloader, num_examples


# Use one of the following URLs per Client
# "FL_Data/hh_01"
# "FL_Data/hh_07"
# "FL_Data/hh_14"
@app.route('/startClient', methods=['GET'])
def start_client():

    # Make TensorFlow log less verbose
    # metrics.append(tf.keras.metrics.Precision())
    # metrics.append(tf.keras.metrics.Recall())

    yolo = YOLO("yolov5nu.pt")
    yolo.to(DEVICE)
    load_data()


    # Define Flower client
    class Client(fl.client.NumPyClient):

        data_received = False
        datetime_state = datetime.datetime.strptime("2023-04-13", "%Y-%m-%d")
        def get_parameters(self, config):
            return [val.cpu().numpy() for _, val in yolo.model.state_dict().items()]

        def set_parameters(self, parameters):
            params_dict = zip(yolo.model.state_dict().keys(), parameters)
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            yolo.model.load_state_dict(state_dict, strict=True)


        def fit(self, parameters, config):
            self.set_parameters(parameters)
            yolo.train(data="mrt_code/yolov5/data/mrt_data.yaml", epochs=1)

            num_files = sum(os.path.isfile(os.path.join(os.path.dirname(__file__)+'\mrt_code\make_dataset\mrt_dataset/train/images/', f)) for f in os.listdir(os.path.dirname(__file__)+'\mrt_code\make_dataset\mrt_dataset/train/images/'))
            print(yolo.metrics)
            return self.get_parameters(config={yolo.metrics}), num_files, {}

        def evaluate(self, parameters, config):
            self.set_parameters(parameters)
            metrics = yolo.val(data="mrt_code/yolov5/data/mrt_data.yaml")
            loss = 0
            accuracy = 0
            num_files = sum(os.path.isfile(
                os.path.join(os.path.dirname(__file__) + '\mrt_code\make_dataset\mrt_dataset/test/images/', f)) for f
                            in
                            os.listdir(os.path.dirname(__file__) + '\mrt_code\make_dataset\mrt_dataset/test/images/'))
            return float(loss), num_files, {"accuracy": float(accuracy)}

        def preprocessing(self):
            split_data.main()


    # Start Flower client
    client = Client()
    fl.client.start_numpy_client(server_address=SERVER_ADDRESS, client=client)

    return {
        'statusCode': 200,
        'body': 'Client finished'
    }


    # url = request.args.get('url')

    # X = utils.load_csv_from_folder(url, "timestamp")[['smartMeter']]
    # y = utils.load_csv_from_folder(url+'/ActionSeq_active_phases', "timestamp")[['kettle']]



    # call SynTiSeD Service here (first time)



if __name__ == '__main__':
   #app.run()
    start_client()



