from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

class KoBARTGenerator:
    def __init__(self, model_name="./my_model"):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def generate(self, query, context):
