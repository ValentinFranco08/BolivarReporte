class TextPreprocessor:
    def __init__(self, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, text):
        return self.tokenizer(
            text or "reporte urbano", padding="max_length", truncation=True,
            max_length=self.max_length, return_tensors="pt",
        )
