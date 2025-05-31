from transformers import T5TokenizerFast, T5ForConditionalGeneration

class KoT5Generator:
    def __init__(self, model_path="./my_t5_model"):
        self.tokenizer = T5TokenizerFast.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path).to("cuda")

    def generate_from_text(self, query):
        '''
        query: input + retreive
        '''

        inputs = self.tokenizer(
            query,
            return_tensors="pt",
            truncation=True,
            max_length=True,
            padding=True
        ).to("cuda")

        output = self.model(
            **inputs,
            max_length=True,
            num_beams=4,
            early_stopping=True
        )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)
