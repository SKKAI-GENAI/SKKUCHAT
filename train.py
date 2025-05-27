from transformers import T5ForConditionalGeneration, PreTrainedTokenizerFast
import torch
from torch.optim import Adam


MODEL_NAME = "KETI-AIR/ke-t5-base-ko"
tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME).to("cuda")


def load_dataset():
    return 


dataset = load_dataset()
dataloader = DataLoader(dataset)
optimizer = Adam(model.parameters(), lr=)


EPOCHS = 
model.train()
for epoch in range(EPOCHS):
    for step, batch in enumerate(dataloader):
        batch = {k: v.squeeze().to("cuda") for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        if step % 10 == 0:
            print(f"Step {step} | Loss: {loss.item():.4f}")


SAVE_PATH = "./my_model"
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)
