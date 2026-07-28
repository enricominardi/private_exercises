#%% packages
import torch
from torchvision import transforms
import torchvision
import kagglehub
import numpy as np
import torchvision
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
 
 
#%% Download latest version
path = kagglehub.dataset_download("arnavr10880/concrete-crack-images-for-classification")
 
print("Path to dataset files:", path)
 
#%% transformations
my_transforms = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.Grayscale(),
    transforms.ToTensor()
])
 
# %% hyperparameter
EPOCHS = 20
BATCH_SIZE = 256
LEARNING_RATE = 0.001
DEVICE = torch.device("cpu")
 
# %% datasets
full_dataset = torchvision.datasets.ImageFolder(root=path, transform=my_transforms)
train_size =  1000 #int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset=full_dataset, lengths=[train_size, val_size])
 
#%% dataloader
train_dataloader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_dataloader = torch.utils.data.DataLoader(dataset=val_dataset, batch_size=BATCH_SIZE, shuffle=True)
 
#%% model class
class ImageClassification(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(1, 6, 3)
        self.pool = torch.nn.MaxPool2d(2)
        self.conv2 = torch.nn.Conv2d(6, 16, 3)
        self.relu = torch.nn.ReLU()
        self.flatten = torch.nn.Flatten()
        self.fc1 = torch.nn.Linear(576, 128)
        self.fc2 = torch.nn.Linear(128, 1)
        self.sigmoid = torch.nn.Sigmoid()
 
    def forward(self, x):
        x = self.conv1(x)  # out: [BS, 6, 30, 30]
        x = self.relu(x)
        x = self.pool(x)  # out: [BS, 6, 15, 15]
        x = self.conv2(x) # out: [1, 16, 13, 13]
        x = self.relu(x)
        x = self.pool(x) # out: [1, 16, 6, 6]
        x = self.flatten(x)  # out: [BS, 576]
        x = self.fc1(x)  # out: [BS, 128]
        x = self.fc2(x) # out: [BS, 1]
        x = self.sigmoid(x)
        return x
 
model = ImageClassification().to(DEVICE)
# sample_tensor = torch.rand((1, 1, 32, 32))
# model(sample_tensor).shape
 
#%% Optimizer and Loss function
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
loss_fn = torch.nn.BCELoss()
 
#%% training loop
loss_train_total = []
for epoch in range(EPOCHS):
    loss_train_epoch = 0
    for i, (X_batch, y_batch) in enumerate(train_dataloader):
        X_batch = X_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)
        # zero gradients
        optimizer.zero_grad()
 
        # forward pass
        y_pred_batch = model(X_batch)
 
        # loss calc
        loss = loss_fn(y_pred_batch.float(), y_batch.reshape(-1, 1).float())
       
        # backward pass
        loss.backward()
 
        # update weights
        optimizer.step()
 
        # extract losses
        loss_train_epoch += loss.item()
    loss_train_total.append(loss_train_epoch)
    print(f"Epoch: {epoch}, Loss: {loss_train_epoch}")
# %%
sns.lineplot(x=list(range(EPOCHS)), y=loss_train_total)

# %% validation
y_pred_val_total, y_true_val_total = [], []
with torch.no_grad():
    for X_val_batch, y_true_val_batch in val_dataloader:
        y_pred_val_batch = model(X_val_batch).flatten().numpy().tolist()
        y_pred_val_total.extend(y_pred_val_batch)
        y_true_val_total.extend(y_true_val_batch.flatten().numpy().tolist())

# %% confusion matrix
y_pred_val_total_class = [1 if val >= 0.5 else 0 for val in y_pred_val_total]
cm = confusion_matrix(y_pred=y_pred_val_total_class, y_true=y_true_val_total)

# %% heatmap
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=['No Crack', 'Crack'],
            yticklabels=['No Crack', 'Crack'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')

# %% accuracy score
accuracy_score(y_pred=y_pred_val_total_class, y_true=y_true_val_total)