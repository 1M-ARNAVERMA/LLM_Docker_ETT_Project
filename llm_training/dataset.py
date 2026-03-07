import torch
import config


def get_batch(data, batch_size):
    
    block_size = config.block_size

    # random starting positions
    ix = torch.randint(len(data) - block_size, (batch_size,))

    # input batch
    x = torch.stack([data[i:i+block_size] for i in ix])

    # target batch
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])

    return x, y