# # models/chatbot/model.py
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

# class MentalHealthChatbot:
#     def __init__(self, model_path="mental-health-chatbot"):
#         try:
#             # Try to load fine-tuned model
#             self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#             self.model = AutoModelForCausalLM.from_pretrained(model_path)
#         except:
#             # Fall back to base model
#             print("Fine-tuned model not found, loading base model")
#             self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
#             self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    
#     def generate_response(self, user_input, conversation_history=None, max_length=100):
#         # Format conversation history if provided
#         if conversation_history:
#             input_text = conversation_history + "\nUser: " + user_input + "\nAssistant:"
#         else:
#             input_text = "User: " + user_input + "\nAssistant:"
        
#         # Encode and generate response
#         inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
#         outputs = self.model.generate(
#             inputs["input_ids"],
#             max_length=len(inputs["input_ids"][0]) + max_length,
#             pad_token_id=self.tokenizer.eos_token_id,
#             no_repeat_ngram_size=3,
#             temperature=0.7
#         )
        
#         # Decode response
#         response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
#         return response.strip()