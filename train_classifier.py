# train_classifier.py - CORRECTED
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import os
import numpy as np

# --- 1. CONFIGURATION ---
DATA_PATH = 'ai_training/disaster_messages.csv'
MODEL_SAVE_DIR = 'incidents/utils/saved_models/'
PRETRAINED_MODEL = 'bert-base-uncased'

# Define the columns that will be the targets for the model (All 36 categories)
CATEGORY_COLUMNS = [
    'related', 'request', 'offer', 'aid_related', 'medical_help', 'medical_products', 
    'search_and_rescue', 'security', 'military', 'child_alone', 'water', 'food', 
    'shelter', 'clothing', 'money', 'missing_people', 'refugees', 'death', 
    'other_aid', 'infrastructure_related', 'transport', 'buildings', 
    'electricity', 'tools', 'hospitals', 'shops', 'aid_centers', 
    'other_infrastructure', 'weather_related', 'floods', 'storm', 'fire', 
    'earthquake', 'cold', 'other_weather', 'direct_report'
]

NUM_LABELS = len(CATEGORY_COLUMNS)

# --- 2. CUSTOM DATASET CLASS ---
class DisasterDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        # Ensure labels are float type for multi-label BCEWithLogitsLoss
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.float) 
        return item

    def __len__(self):
        return len(self.labels)

# --- 3. MAIN TRAINING FUNCTION ---
def train_model():
    print(f"Loading data from {DATA_PATH}...")
    
    df = pd.read_csv(DATA_PATH)
    
    # Drop rows with NaN in the 'message' column and ensure labels are valid
    df.dropna(subset=['message'], inplace=True)
    df = df[df[CATEGORY_COLUMNS].sum(axis=1) > 0] # Keep only rows with at least one label

    # Split data
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    # Convert labels to NumPy array
    train_labels = train_df[CATEGORY_COLUMNS].values
    val_labels = val_df[CATEGORY_COLUMNS].values
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(PRETRAINED_MODEL, num_labels=NUM_LABELS)

    # Tokenize text
    train_encodings = tokenizer(train_df['message'].tolist(), truncation=True, padding=True, max_length=128)
    val_encodings = tokenizer(val_df['message'].tolist(), truncation=True, padding=True, max_length=128)

    # Create dataset objects
    train_dataset = DisasterDataset(train_encodings, train_labels)
    val_dataset = DisasterDataset(val_encodings, val_labels)

    # Define training arguments - FIX applied here
    training_args = TrainingArguments(
        output_dir=MODEL_SAVE_DIR,
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        # FIX: Changed 'evaluation_strategy' to 'eval_strategy'
        eval_strategy="epoch",  
        save_strategy="epoch",  
        # FIX: Changed 'load_best_model_at' to 'load_best_model_at_end' for compatibility
        load_best_model_at_end=True, 
        metric_for_best_model='eval_loss',
        save_total_limit=1,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    # Start Training
    print("Starting fine-tuning...")
    trainer.train()

    # --- 4. SAVE FINAL ARTIFACTS ---
    # Save the final best model and tokenizer
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    model_save_path = os.path.join(MODEL_SAVE_DIR, "final_model")
    trainer.save_model(model_save_path)
    tokenizer.save_pretrained(model_save_path)
    print(f"\nModel and Tokenizer saved successfully to: {model_save_path}")


if __name__ == "__main__":
    if not os.path.exists('ai_training/'):
        os.makedirs('ai_training/')
        print("Created 'ai_training/' directory. Place your 'disaster_messages.csv' here.")
    if not os.path.exists(DATA_PATH):
        print(f"CRITICAL: Dataset not found at {DATA_PATH}. Please obtain and place the CSV file.")
    else:
        train_model()