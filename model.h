// model.h
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
int predict_activity(float* subcarriers) {
    // Calculate localized active mean (indices 10 to 60 inclusive, skipping dropped guard bands 27 to 37)
    float active_sum = 0.0f;
    int count = 0;
    for (int i = 10; i <= 60; i++) {
        if (i >= 27 && i <= 37) continue; // Skip dropped guard bands/null subcarriers
        active_sum += subcarriers[i];
        count++;
    }
    float active_mean = active_sum / count;

    // Decision Tree inference logic
    if (active_mean <= 22.900499f) {
        if (subcarriers[53] <= 22.634999f) {
            if (subcarriers[54] <= 8.930000f) {
                return 0;
            } else {
                return 1;
            }
        } else {
            return 2;
        }
    } else {
        return 0;
    }
}

#endif // MODEL_H
