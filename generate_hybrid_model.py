import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

def main():
    # Load processed CSI data
    df = pd.read_csv('processed_csi_data.csv')
    
    # Extract hybrid feature set
    active_cols = [col for col in df.columns if col.isdigit() and 10 <= int(col) <= 60]
    
    X_hybrid = pd.DataFrame()
    X_hybrid['subcarrier_13'] = df['13']
    X_hybrid['subcarrier_53'] = df['53']
    X_hybrid['subcarrier_54'] = df['54']
    X_hybrid['active_mean'] = df[active_cols].mean(axis=1)
    X_hybrid['active_std'] = df[active_cols].std(axis=1)
    
    y = df['label']
    
    # Train Decision Tree Classifier (max_depth=3) on stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X_hybrid, y, test_size=0.3, random_state=42, stratify=y
    )
    
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X_train, y_train)
    
    # Custom traversal function to generate C++ code
    tree = clf.tree_
    feature_map = {
        'subcarrier_13': 'subcarriers[13]',
        'subcarrier_53': 'subcarriers[53]',
        'subcarrier_54': 'subcarriers[54]',
        'active_mean': 'active_mean',
        'active_std': 'active_std'
    }
    
    def recurse(node, depth):
        indent = "    " * depth
        if tree.feature[node] != -2:  # TREE_UNDEFINED check
            feature_idx = tree.feature[node]
            feature_name = X_hybrid.columns[feature_idx]
            cpp_feature = feature_map[feature_name]
            threshold = tree.threshold[node]
            
            left_child = tree.children_left[node]
            right_child = tree.children_right[node]
            
            code = f"{indent}if ({cpp_feature} <= {threshold:.6f}f) {{\n"
            code += recurse(left_child, depth + 1)
            code += f"{indent}}} else {{\n"
            code += recurse(right_child, depth + 1)
            code += f"{indent}}}\n"
            return code
        else:
            predicted_class = np.argmax(tree.value[node][0])
            return f"{indent}return {predicted_class};\n"
            
    cpp_code = f"""// model.h
// Auto-generated Hybrid Decision Tree Classifier for ESP32 TinyML HAR
// Activity Class Mapping:
// 0 = STILL
// 1 = MOVING
// 2 = JUMPING

#ifndef MODEL_H
#define MODEL_H

/**
 * Predicts the human activity based on Wi-Fi CSI subcarrier amplitudes.
 * Uses a hybrid feature set containing localized active mean and specific raw subcarriers.
 * 
 * @param subcarriers Array containing the amplitude of the subcarriers (at least 128 elements).
 * @return 0 for STILL, 1 for MOVING, 2 for JUMPING.
 */
int predict_activity(float* subcarriers) {{
    // Calculate localized active mean (indices 10 to 60 inclusive, skipping dropped guard bands 27 to 37)
    float active_sum = 0.0f;
    int count = 0;
    for (int i = 10; i <= 60; i++) {{
        if (i >= 27 && i <= 37) continue; // Skip dropped guard bands/null subcarriers
        active_sum += subcarriers[i];
        count++;
    }}
    float active_mean = active_sum / count;

    // Decision Tree inference logic
{recurse(0, 1)}}}

#endif // MODEL_H
"""
    
    # Save code to model.h
    output_path = 'model.h'
    with open(output_path, 'w') as f:
        f.write(cpp_code)
        
    print(f"C++ header saved to '{output_path}' successfully.\n")
    print("================ GENERATED model.h CODE ================")
    print(cpp_code)

if __name__ == '__main__':
    main()
