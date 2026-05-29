import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score

def main():
    # Load processed CSI data
    print("Loading preprocessed CSI data...")
    df = pd.read_csv('processed_csi_data.csv')
    
    # 1. Extract hybrid feature set
    # Identify which columns in the active zone (10 to 60) exist in the dataframe
    active_cols = [col for col in df.columns if col.isdigit() and 10 <= int(col) <= 60]
    
    X_hybrid = pd.DataFrame()
    X_hybrid['subcarrier_13'] = df['13']
    X_hybrid['subcarrier_53'] = df['53']
    X_hybrid['subcarrier_54'] = df['54']
    X_hybrid['active_mean'] = df[active_cols].mean(axis=1)
    X_hybrid['active_std'] = df[active_cols].std(axis=1)
    
    y = df['label']
    
    print(f"Hybrid Features Shape: {X_hybrid.shape}")
    print("\nFeature matrix (first 5 rows):")
    print(X_hybrid.head())
    
    # 2. Stratified Split (70% train, 30% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X_hybrid, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # 3. Train Decision Tree Classifier (max_depth=3)
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X_train, y_train)
    
    # Predict and calculate accuracies
    y_train_pred = clf.predict(X_train)
    y_test_pred = clf.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    # 4. Print results
    print("\n================ EVALUATION SUMMARY ================")
    print(f"Training Accuracy: {train_acc:.4f} ({train_acc * 100:.2f}%)")
    print(f"Testing Accuracy:  {test_acc:.4f} ({test_acc * 100:.2f}%)")
    
    print("\n================ DECISION TREE RULES ================")
    tree_rules = export_text(clf, feature_names=list(X_hybrid.columns))
    print(tree_rules)
    
    # 5. Extract tree splits and generate comparison table
    tree = clf.tree_
    # Find all splits in the tree
    splits = []
    for i in range(tree.node_count):
        if tree.feature[i] != -2:  # Leaf node check
            feature_idx = tree.feature[i]
            feature_name = X_hybrid.columns[feature_idx]
            threshold = tree.threshold[i]
            splits.append((feature_name, threshold))
            
    # Calculate group averages for all features across the whole dataset
    averages = df.groupby('label').apply(lambda g: pd.Series({
        'subcarrier_13': g['13'].mean(),
        'subcarrier_53': g['53'].mean(),
        'subcarrier_54': g['54'].mean(),
        'active_mean': g[active_cols].mean(axis=1).mean(),
        'active_std': g[active_cols].std(axis=1).mean()
    }), include_groups=False)
    
    print("\n================ PHYSICAL THRESHOLD VS REAL AVERAGES ================")
    print(f"{'Feature Name':<16} | {'DT Threshold':<12} | {'Still (0) Avg':<13} | {'Moving (1) Avg':<14} | {'Jumping (2) Avg':<15}")
    print("-" * 80)
    
    # Track printed features to avoid duplicates in the comparison table
    printed_features = set()
    for feature_name, threshold in splits:
        if feature_name in printed_features:
            # We can print multiple thresholds if they exist, but let's just print each feature once for clarity
            continue
        printed_features.add(feature_name)
        
        still_avg = averages.loc[0, feature_name]
        moving_avg = averages.loc[1, feature_name]
        jumping_avg = averages.loc[2, feature_name]
        
        print(f"{feature_name:<16} | {threshold:<12.4f} | {still_avg:<13.4f} | {moving_avg:<14.4f} | {jumping_avg:<15.4f}")
        
    print("\n================ ALL HYBRID FEATURE AVERAGES BY CLASS ================")
    print(averages.to_string())

if __name__ == '__main__':
    main()
