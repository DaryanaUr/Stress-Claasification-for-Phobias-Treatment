import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

# Folder where CSV files are stored
DATA_FOLDER = 'Datasets/'  # change if needed
SEQUENCE_LENGTH = 100  # 10 seconds if sampled at 10 Hz

# Load and prepare all CSV files
def load_data():
    X, y = [], []
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(DATA_FOLDER, filename))
            if df.shape[0] < SEQUENCE_LENGTH:
                continue

            # Label from filename (HS, MS, LS)
            if '_HS_' in filename:
                label = 'High'
            elif '_MS_' in filename:
                label = 'Medium'
            elif '_LS_' in filename:
                label = 'Low'
            else:
                continue  # skip files without a clear label

            # Normalize features
            features = df[['Heart Rate', 'Galvanic Skin Response']].values
            scaler = MinMaxScaler()
            features_scaled = scaler.fit_transform(features)

            # Create sliding windows
            for i in range(0, len(features_scaled) - SEQUENCE_LENGTH + 1, SEQUENCE_LENGTH):
                window = features_scaled[i:i+SEQUENCE_LENGTH]
                X.append(window)
                y.append(label)

    return np.array(X), np.array(y)

# Load dataset
print("Loading data...")
X, y = load_data()
print(f"Data shape: X={X.shape}, y={y.shape}")

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

# Build LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(SEQUENCE_LENGTH, 2), return_sequences=False))
model.add(Dense(32, activation='relu'))
model.add(Dense(3, activation='softmax'))  # 3 classes: Low, Medium, High

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train model
print("Training model...")
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

history = model.fit(
    X, y_categorical,
    validation_split=0.2,
    epochs=50,
    batch_size=32,
    callbacks=[early_stop],
    shuffle=True
)

# Save model
model.save('stress_model.h5')
print("Model saved as 'stress_model.h5'")