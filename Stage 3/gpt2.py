from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling
import os

# Load tokenizer dan model GPT2
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token 
model = GPT2LMHeadModel.from_pretrained(model_name)

# Siapkan dataset
def load_dataset(file_path, tokenizer, block_size=128):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size
    )

# Load dataset
dataset = load_dataset("data/dataset_ubidots.txt", tokenizer)

# Data collator untuk language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False  
)

# Siapkan konfigurasi pelatihan
training_args = TrainingArguments(
    output_dir="model_train/gpt2-finetuned", 
    overwrite_output_dir=True, 
    num_train_epochs=20, 
    per_device_train_batch_size=2,  
    save_steps=100,  
    save_total_limit=2,  
    prediction_loss_only=True,  
    logging_steps=5, 
    learning_rate=5e-5,  
)

# Siapkan Trainer untuk melatih model
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset
)

# Latih model
print("🚀 Mulai pelatihan GPT-2...")
trainer.train()

# Simpan model yang sudah dilatih dan tokenizer
trainer.save_model("model_train/gpt2-finetuned")
tokenizer.save_pretrained("model_train/gpt2-finetuned")

print("✅ Model sudah dilatih dan disimpan di 'model_train/gpt2-finetuned'.")