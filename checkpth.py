import torch
import matplotlib.pyplot as plt
import numpy as np

checkpoint = torch.load("dqn_modelRed.pth")  # Or your model file

# 1) Check the keys in the checkpoint
print(checkpoint.keys())
# Example output: dict_keys(['model_state_dict', 'target_model_state_dict',
#                            'optimizer_state_dict', 'epsilon', 'memory'])

# 2) Inspect model state and shapes
model_state = checkpoint['model_state_dict']
for param_name, tensor_value in model_state.items():
    print(param_name, tensor_value.shape)

# 3) Check the replay buffer size
memory_data = checkpoint['memory']  # It's a Python list
print("Replay buffer length:", len(memory_data))

# 4) See the stored epsilon
print("Epsilon value:", checkpoint['epsilon'])


# Suppose we loaded model_state as above
all_weights = []
for p in model_state.values():
    all_weights.extend(p.cpu().numpy().flatten())

plt.hist(all_weights, bins=100)
plt.title("Distribution of Model Weights")
plt.show()
