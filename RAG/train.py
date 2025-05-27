import torch
from torch.utils.data import DataLoader

from transformers import AdamW, T5TokenizerFast, T5ForConditionalGeneration
from dataset import SKCTDataset



device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

tokenizer = T5TokenizerFast.from_pretrained('paust/pko-t5-base')
model = T5ForConditionalGeneration.from_pretrained('paust/pko-t5-base').to(device)
dataset = SKCTDataset(split='train', tokenizer_name='paust/pko-t5-base')
loader = DataLoader(dataset, batch_size=8, shuffle=True)

optimizer = AdamW(model.parameters(), lr=3e-5)
model.train()

for epoch in range(3):
    for step, batch in enumerate(loader):
        input_ids = batch['input_ids'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(
            input_ids=input_ids,
            labels=labels
        )

        loss = outputs['loss']
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if step % 10 == 0:
            print(f"Step {step} | Loss: {loss.item():.4f}")

SAVE_PATH = "./RAG/my_t5_model"
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)