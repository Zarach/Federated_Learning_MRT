import flwr as fl
from typing import List, Tuple
from flwr.common import Metrics
from ultralytics import YOLO

SERVER_ADDRESS = "0.0.0.0:8080"

def create_model():
    model = YOLO("yolov5nu.pt")
    return model

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    print(metrics)
    accuracies = [num_examples * m["metrics/mAP50(B)"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"metrics/mAP50(B)": sum(accuracies) / sum(examples)}

net = create_model()
params = [val.cpu().numpy() for _, val in net.model.state_dict().items()]

# Pass parameters to the Strategy for server-side parameter initialization
strategy = fl.server.strategy.FedAvg(
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    min_fit_clients=1,
    min_evaluate_clients=1,
    min_available_clients=1,
    initial_parameters=fl.common.ndarrays_to_parameters(params)#,
    # evaluate_metrics_aggregation_fn=weighted_average,
    # fit_metrics_aggregation_fn=weighted_average
)

# Start Flower server
def start_server():
    fl.server.start_server(
        server_address=SERVER_ADDRESS,
        config=fl.server.ServerConfig(num_rounds=5),
        strategy=strategy
    )

start_server()
