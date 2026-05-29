import os
import joblib
import pandas as pd
import numpy as np

def generate_cpp_header(model_path, data_path, output_path):
    # 2. Load the trained model
    print(f"Loading model from '{model_path}'...")
    clf = joblib.load(model_path)
    
    # Load dataset to get original feature column names
    print(f"Loading data from '{data_path}' to map feature columns...")
    df = pd.read_csv(data_path)
    X_columns = df.drop(columns=['label']).columns.tolist()
    
    # 3. Custom function to inspect decision tree and generate C++ nested if-else
    tree = clf.tree_
    
    def recurse(node, depth):
        indent = "    " * depth
        # Check if it is a leaf node
        if tree.feature[node] != -2:  # -2 is the value for TREE_UNDEFINED (leaf)
            feature_idx = tree.feature[node]
            # Map index to the original subcarrier index (column name)
            subcarrier_idx = X_columns[feature_idx]
            threshold = tree.threshold[node]
            
            left_child = tree.children_left[node]
            right_child = tree.children_right[node]
            
            code = f"{indent}if (subcarriers[{subcarrier_idx}] <= {threshold:.6f}f) {{\n"
            code += recurse(left_child, depth + 1)
            code += f"{indent}}} else {{\n"
            code += recurse(right_child, depth + 1)
            code += f"{indent}}}\n"
            return code
        else:
            # Leaf node: get the predicted class
            predicted_class = np.argmax(tree.value[node][0])
            return f"{indent}return {predicted_class};\n"
            
    # Generate the full header content
    header_content = f"""// model.h
// Auto-generated Decision Tree Classifier for ESP32 TinyML HAR
// Activity Class Mapping:
// 0 = STILL
// 1 = MOVING
// 2 = JUMPING

#ifndef MODEL_H
#define MODEL_H

/**
 * Predicts the human activity based on Wi-Fi CSI subcarrier amplitudes.
 * @param subcarriers Array containing the amplitude of the subcarriers (at least 128 elements).
 * @return 0 for STILL, 1 for MOVING, 2 for JUMPING.
 */
int predict_activity(float* subcarriers) {{
{recurse(0, 1)}}}

#endif // MODEL_H
"""
    
    # Write to file
    print(f"Generating C++ header file at '{output_path}'...")
    with open(output_path, 'w') as f:
        f.write(header_content)
    print("C++ header file exported successfully.")

def main():
    model_path = 'csi_model.pkl'
    data_path = 'processed_csi_data.csv'
    output_path = 'model.h'
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_path}' not found. Please run train.py first.")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file '{data_path}' not found. Please run preprocess.py first.")
        
    generate_cpp_header(model_path, data_path, output_path)

if __name__ == '__main__':
    main()
