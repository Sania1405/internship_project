# # 1. pipeline: A high-level helper function from Hugging Face to quickly load models for specific tasks (like text classification).
# from transformers import pipeline
# from core.logger import logger

# class IntentModel:
#     def __init__(self, model_name="distilbert-base-uncased"):
#         """
#         Initializes the intent classification model using Hugging Face Transformers.
#         Loaded once to prevent massive memory usage on every request.
#         """
#         logger.info(f"Loading Intent Model ({model_name})...")
#         try:
#             # 2. pipeline("text-classification", model=model_name): Downloads and loads DistilBERT.
#             # DistilBERT is a smaller, faster, cheaper version of BERT (60% faster, retaining 97% accuracy).
#             # It classifies input text (e.g. into POSITIVE/NEGATIVE or custom labels if fine-tuned).
#             self.classifier = pipeline("text-classification", model=model_name)
#             logger.info("Intent Model loaded successfully!")
#         except Exception as e:
#             logger.error(f"Failed to load Intent Model: {e}")
#             raise e

#     def predict(self, text: str) -> str:
#         """
#         Takes transcribed text, passes it to the ML classifier, and returns the predicted intent.
#         """
#         if not text:
#             logger.warning("Received empty text for intent prediction.")
#             return "UNKNOWN"
            
#         logger.info(f"Predicting intent for text: '{text}'")
#         try:
#             # 3. self.classifier(text): Runs text classification. Returns a list containing a dict, e.g.:
#             # [{'label': 'POSITIVE', 'score': 0.985}]
#             result = self.classifier(text)[0]
#             # 4. label: The predicted class name.
#             intent = result['label']
#             # 5. score: The confidence probability (from 0.0 to 1.0) of the prediction.
#             confidence = result['score']
            
#             logger.debug(f"Intent predicted: {intent} (Confidence: {confidence:.2f})")
#             return intent
#         except Exception as e:
#             logger.error(f"Error during intent prediction: {e}")
#             return "ERROR"


# direclty sending speech text to llama api hence saving ram, reducing latency and accuracy improoves too