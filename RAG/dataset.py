from torch.utils.data import Dataset
from transformers import AutoTokenizer

def load_dataset():

input_ids = tokenizer(["qa question: 당신의 이름은 무엇인가요?"]).input_ids
labels = tokenizer(["T5 입니다."]).input_ids
outputs = model(input_ids=input_ids, labels=labels)

class SKCTDataset(Dataset):
    def __init__(self, split='train', tokenizer_name='skt/kobert-base-v1', max_length=512):
        self.dataset = load_dataset()
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        query = self.data.loc[idx, 'query']
        response = self.data.loc[idx, 'response']
        
        # label이 있으면 (예: positive=1, negative=0), 없으면 None
        label = self.data.loc[idx, 'label'] if 'label' in self.data.columns else None

        encoding = self.tokenizer(
            query,
            response,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        item['labels'] = int(label)

        return item
