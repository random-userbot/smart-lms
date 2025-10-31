# 🎯 Practical GPU Training Solution for Your LSTM Model

## Current Situation
- **GPU**: NVIDIA GeForce GTX 1650 ✅ (detected)
- **TensorFlow**: 2.15.1 (CPU-only) ⚠️
- **DirectML**: Installation issues on your system

## ✅ Recommended Solutions (Ranked by Ease)

---

### **Solution 1: Use Google Colab (FREE GPU) - FASTEST** ⭐ Recommended

**Why this is best for you:**
- ✅ **Zero setup** - No installation needed
- ✅ **Free GPU access** - NVIDIA T4 or P100 (better than GTX 1650)
- ✅ **15-25 GB RAM** vs your local machine
- ✅ **Works immediately** - Just upload your code
- ✅ **Training time**: 10-15 minutes for LSTM

#### Step-by-Step:

1. **Go to Google Colab**: https://colab.research.google.com/

2. **Enable GPU**:
   - Click: `Runtime` → `Change runtime type`
   - Hardware accelerator: `GPU`
   - GPU type: `T4` (free tier)
   - Click `Save`

3. **Upload Your Data** (create new notebook):
```python
# Cell 1: Check GPU
import tensorflow as tf
print("TensorFlow version:", tf.__version__)
print("GPU available:", tf.test.is_gpu_available())
print("GPU device:", tf.test.gpu_device_name())

# Expected output:
# TensorFlow version: 2.15.0
# GPU available: True
# GPU device: /device:GPU:0
```

4. **Mount Google Drive** (to save your model):
```python
# Cell 2: Mount Drive
from google.colab import drive
drive.mount('/content/drive')
```

5. **Upload DAiSEE OpenFace CSV files**:
```python
# Cell 3: Upload files
from google.colab import files
uploaded = files.upload()  # Click to upload your CSV files
```

6. **Run Your LSTM Training**:
```python
# Cell 4: Train LSTM
import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load your OpenFace features
df = pd.read_csv('openface_features.csv')

# Extract 22 features (17 AUs + 2 gaze + 3 pose)
LSTM_FEATURES = [
    'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r',
    'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r',
    'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
    'gaze_angle_x', 'gaze_angle_y',
    'pose_Rx', 'pose_Ry', 'pose_Rz'
]

X = df[LSTM_FEATURES].values
y = df['label'].values  # Your engagement labels

# Create sequences (30 frames)
def create_sequences(X, y, seq_length=30):
    sequences, labels = [], []
    for i in range(len(X) - seq_length):
        sequences.append(X[i:i+seq_length])
        labels.append(y[i+seq_length])
    return np.array(sequences), np.array(labels)

X_seq, y_seq = create_sequences(X, y, seq_length=30)

# Normalize
scaler = StandardScaler()
X_seq_flat = X_seq.reshape(-1, 22)
X_seq_scaled = scaler.fit_transform(X_seq_flat).reshape(-1, 30, 22)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_seq_scaled, y_seq, test_size=0.2, random_state=42
)

# Build LSTM model
model = keras.Sequential([
    keras.layers.LSTM(128, return_sequences=True, input_shape=(30, 22)),
    keras.layers.Dropout(0.3),
    keras.layers.LSTM(64),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(4, activation='softmax')  # 4 engagement classes
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Train on GPU
with tf.device('/GPU:0'):
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        verbose=1
    )

# Save model
model.save('/content/drive/MyDrive/engagement_lstm.h5')
print("✅ Model saved to Google Drive!")
```

7. **Download trained model**:
   - It will be saved in your Google Drive: `MyDrive/engagement_lstm.h5`
   - Download and copy to: `smart-lms/ml/models/`

---

### **Solution 2: Install CUDA Toolkit (Local GPU) - More Control**

If you want to use your GTX 1650 locally:

#### Quick Install (PowerShell as Administrator):
```powershell
# 1. Install CUDA 11.8
winget install -e --id Nvidia.CUDA -v 11.8

# 2. Add to PATH (restart PowerShell after)
$env:Path += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin"

# 3. Install TensorFlow GPU
pip install tensorflow[and-cuda]

# 4. Verify
python -c "import tensorflow as tf; print('GPUs:', tf.config.list_physical_devices('GPU'))"
```

**Manual Installation** (if winget fails):
1. Download CUDA 11.8: https://developer.nvidia.com/cuda-11-8-0-download-archive
2. Run installer (takes ~15 minutes)
3. Restart computer
4. Run commands above

---

### **Solution 3: Use PyTorch Instead (Easier GPU Setup)**

PyTorch has better Windows GPU support out of the box.

#### Install PyTorch with CUDA:
```powershell
# Uninstall CPU version
pip uninstall torch torchvision torchaudio -y

# Install GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

#### PyTorch LSTM Training Code:
```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Check GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Define LSTM Model
class EngagementLSTM(nn.Module):
    def __init__(self):
        super(EngagementLSTM, self).__init__()
        self.lstm1 = nn.LSTM(input_size=22, hidden_size=128, 
                            num_layers=1, batch_first=True)
        self.dropout1 = nn.Dropout(0.3)
        self.lstm2 = nn.LSTM(input_size=128, hidden_size=64, 
                            num_layers=1, batch_first=True)
        self.dropout2 = nn.Dropout(0.3)
        self.fc1 = nn.Linear(64, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 4)  # 4 classes
    
    def forward(self, x):
        # x shape: (batch, 30, 22)
        x, _ = self.lstm1(x)
        x = self.dropout1(x)
        x, _ = self.lstm2(x)
        x = self.dropout2(x)
        x = x[:, -1, :]  # Take last timestep
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Initialize model and move to GPU
model = EngagementLSTM().to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Prepare data (assuming X_train, y_train are numpy arrays)
X_tensor = torch.FloatTensor(X_train).to(device)
y_tensor = torch.LongTensor(y_train).to(device)

dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Training loop
num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    
    for batch_X, batch_y in dataloader:
        # Forward pass (data already on GPU)
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(dataloader):.4f}')

# Save model
torch.save(model.state_dict(), 'engagement_lstm_pytorch.pth')
print("✅ Model saved!")
```

---

## 🎯 My Recommendation

**For your situation, I strongly recommend Solution 1 (Google Colab):**

### Why?
1. ✅ **Works immediately** - No installation headaches
2. ✅ **Free T4 GPU** - Actually better than your GTX 1650
3. ✅ **Training time**: ~10-15 minutes (vs 2-3 hours on CPU)
4. ✅ **No storage limits** - Use Google Drive for models
5. ✅ **Reproducible** - Share notebook with collaborators

### Google Colab GPU Specs:
- **NVIDIA T4**: 16 GB VRAM (vs GTX 1650's 4 GB)
- **40 GB RAM**: More than enough for LSTM
- **Free tier**: 12 hours continuous usage per session

### Steps to Get Started NOW:
```
1. Open: https://colab.research.google.com/
2. New Notebook
3. Runtime → Change runtime type → GPU (T4)
4. Paste the training code from above
5. Upload your OpenFace CSV files
6. Run all cells
7. Download trained model in 15 minutes
```

---

## 📊 Time Comparison

| Method | Setup Time | Training Time | Total Time |
|--------|-----------|---------------|------------|
| **CPU (current)** | 0 min | 2-3 hours | 2-3 hours |
| **Google Colab GPU** | 5 min | 10-15 min | 15-20 min |
| **Local CUDA Setup** | 30-60 min | 15-20 min | 45-80 min |
| **PyTorch CUDA** | 15-30 min | 15-20 min | 30-50 min |

---

## 🚀 Quick Start Script for Colab

Save this as `lstm_training_colab.ipynb` and upload to Google Colab:

```python
# ========== GOOGLE COLAB LSTM TRAINING SCRIPT ==========
# 1. Set GPU runtime: Runtime → Change runtime type → GPU

# Cell 1: Setup
!pip install -q pandas numpy scikit-learn tensorflow

import tensorflow as tf
print("✅ TensorFlow version:", tf.__version__)
print("✅ GPU available:", tf.config.list_physical_devices('GPU'))

# Cell 2: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cell 3: Upload OpenFace CSV files
from google.colab import files
print("📁 Upload your DAiSEE OpenFace CSV files:")
uploaded = files.upload()

# Cell 4: Data Preparation
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load all CSV files
all_data = []
for filename in uploaded.keys():
    df = pd.read_csv(filename)
    all_data.append(df)

df = pd.concat(all_data, ignore_index=True)
print(f"✅ Loaded {len(df)} frames from {len(uploaded)} files")

# Extract features
LSTM_FEATURES = [
    'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r',
    'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r',
    'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
    'gaze_angle_x', 'gaze_angle_y',
    'pose_Rx', 'pose_Ry', 'pose_Rz'
]

X = df[LSTM_FEATURES].values
y = df['engagement_label'].values  # Change to your label column

# Create sequences
def create_sequences(X, y, seq_length=30, stride=15):
    sequences, labels = [], []
    for i in range(0, len(X) - seq_length, stride):
        sequences.append(X[i:i+seq_length])
        labels.append(y[i+seq_length-1])
    return np.array(sequences), np.array(labels)

X_seq, y_seq = create_sequences(X, y)
print(f"✅ Created {len(X_seq)} sequences")

# Normalize
scaler = StandardScaler()
X_seq_flat = X_seq.reshape(-1, 22)
X_seq_scaled = scaler.fit_transform(X_seq_flat).reshape(-1, 30, 22)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_seq_scaled, y_seq, test_size=0.2, stratify=y_seq, random_state=42
)

print(f"✅ Training set: {len(X_train)} sequences")
print(f"✅ Test set: {len(X_test)} sequences")

# Cell 5: Build and Train LSTM
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

model = keras.Sequential([
    keras.layers.LSTM(128, return_sequences=True, input_shape=(30, 22)),
    keras.layers.Dropout(0.3),
    keras.layers.LSTM(64),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(4, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Train
callbacks = [
    EarlyStopping(patience=15, restore_best_weights=True),
    ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_accuracy')
]

print("🚀 Training started on GPU...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# Cell 6: Evaluate
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"✅ Test Accuracy: {test_acc*100:.2f}%")

# Cell 7: Save Model
import pickle

# Save model to Google Drive
model.save('/content/drive/MyDrive/engagement_lstm.h5')
print("✅ Model saved to Google Drive: engagement_lstm.h5")

# Save scaler
with open('/content/drive/MyDrive/lstm_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✅ Scaler saved to Google Drive: lstm_scaler.pkl")

# Cell 8: Download (optional - if not using Drive)
from google.colab import files
files.download('best_model.h5')
```

---

## ✅ Final Recommendation

**Start with Google Colab TODAY:**
1. Copy the script above
2. Upload to Colab
3. Train your LSTM in 15-20 minutes
4. Download model

**Then, if you want local GPU later:**
- Install PyTorch with CUDA (Solution 3)
- It's easier than TensorFlow CUDA setup on Windows

---

**🎯 Bottom Line**: Don't waste hours troubleshooting local GPU setup. Use Colab's free GPU, train your model in 15 minutes, then focus on integrating it into Smart LMS.
