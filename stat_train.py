import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def main():
    # Load processed CSI data
    print("Loading preprocessed CSI data...")
    df = pd.read_csv('processed_csi_data.csv')
    
    # Separate features and target
    X_raw = df.drop(columns=['label'])
    y = df['label']
    
    print(f"Original shape: {df.shape}")
    
    # Calculate statistical features across subcarriers for each packet (row)
    print("Extracting statistical features (Mean, Std Dev, Max, Min)...")
    X_stat = pd.DataFrame()
    X_stat['mean'] = X_raw.mean(axis=1)
    X_stat['std'] = X_raw.std(axis=1)
    X_stat['max'] = X_raw.max(axis=1)
    X_stat['min'] = X_raw.min(axis=1)
    
    print(f"New statistical features shape: {X_stat.shape}")
    print("\nFirst 5 rows of statistical features:")
    print(X_stat.head())
    
    # Split into train and test sets keeping class stratification
    # Using stratify=y to ensure labels are distributed proportionally
    X_train, X_test, y_train, y_test = train_test_split(
        X_stat, y, test_size=0.3, random_state=42, stratify=y
    )
    print(f"\nStratified Split:")
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")
    print(f"Train label distribution:\n{y_train.value_counts()}")
    print(f"Test label distribution:\n{y_test.value_counts()}")
    
    # Train Random Forest Classifier with exactly 3 trees and max depth of 3
    rf = RandomForestClassifier(n_estimators=3, max_depth=3, random_state=42)
    rf.fit(X_train, y_train)
    
    # Predict and calculate accuracies
    y_train_pred = rf.predict(X_train)
    y_test_pred = rf.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    # Unique labels present
    unique_labels = sorted(y_test.unique())
    target_names = []
    label_map = {0: "Still", 1: "Moving", 2: "Jumping"}
    for label in unique_labels:
        target_names.append(label_map[label])
        
    class_report = classification_report(y_test, y_test_pred, target_names=target_names)
    
    print("\n================ EVALUATION SUMMARY ================")
    print(f"Training Accuracy: {train_acc:.4f} ({train_acc * 100:.2f}%)")
    print(f"Testing Accuracy:  {test_acc:.4f} ({test_acc * 100:.2f}%)")
    
    print("\nClassification Report (Testing):")
    print(class_report)

if __name__ == '__main__':
    main()
