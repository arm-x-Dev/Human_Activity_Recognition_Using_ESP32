import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def main():
    # Load processed CSI data
    print("Loading preprocessed CSI data...")
    df = pd.read_csv('processed_csi_data.csv')
    
    # Separate features and target
    X = df.drop(columns=['label'])
    y = df['label']
    
    print(f"Features shape: {X.shape}, Target shape: {y.shape}")
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")
    
    # Train a small Decision Tree Classifier (max_depth=3 to make it perfect for C++ TinyML deployment)
    max_depth = 3
    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(X_train, y_train)
    print(f"Trained DecisionTreeClassifier with max_depth={max_depth}.")
    
    # Predict on test set
    y_pred = clf.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # Check what labels are present in test set to avoid target_names mismatch
    unique_labels = sorted(y_test.unique())
    target_names = []
    label_map = {0: "Still", 1: "Moving", 2: "Jumping"}
    for label in unique_labels:
        target_names.append(label_map[label])
        
    class_report = classification_report(y_test, y_pred, target_names=target_names)
    
    print("\n================ MODEL METRICS ================")
    print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    
    print("\nConfusion Matrix:")
    print(conf_matrix)
    
    print("\nClassification Report:")
    print(class_report)
    
    # Text representation of decision tree rules
    print("\n================ DECISION TREE RULES ================")
    tree_rules = export_text(clf, feature_names=[str(c) for c in X.columns])
    print(tree_rules)
    
    # Save the trained model
    model_filename = 'csi_model.pkl'
    joblib.dump(clf, model_filename)
    print(f"Saved trained model to '{model_filename}' successfully.")

if __name__ == '__main__':
    main()
