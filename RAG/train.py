from transformers import AdamW, T5TokenizerFast, T5ForConditionalGeneration
from torch.utils.data import DataLoader
from model import SKCTKoBert
from dataset import SKCTDataset
import torch

tokenizer = T5TokenizerFast.from_pretrained('paust/pko-t5-base')
model = T5ForConditionalGeneration.from_pretrained('paust/pko-t5-base')
dataset = SKCTDataset(split='train', tokenizer_name='skt/kobert-base-v1')
loader = DataLoader(dataset, batch_size=8, shuffle=True)

optimizer = AdamW(model.parameters(), lr=3e-5)
model.train()

for epoch in range(3):
    for batch in loader:
        input_ids = batch['input_ids']
        labels = batcch['labels']

        outputs = model(
            input_ids=input_ids,
            labels=labels
        )

        loss = outputs['loss']
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()