// model.h
#ifndef MODEL_H
#define MODEL_H

#include <Arduino.h>

int predict_activity(float* subcarriers) {
    // Calculate localized active mean
    float active_sum = 0.0f;
    int count = 0;
    for (int i = 10; i <= 60; i++) {
        if (i >= 27 && i <= 37) continue; 
        active_sum += subcarriers[i];
        count++;
    }
    float active_mean = active_sum / count;

    // True High-Accuracy Trained Decision Tree Logic
    if (active_mean <= 22.900499f) {
        if (subcarriers[53] <= 22.634999f) {
            if (subcarriers[54] <= 8.930000f) {
                return 0; // STILL
            } else {
                return 1; // MOVING
            }
        } else {
            return 2; // JUMPING
        }
    } else {
        return 0; // STILL
    }
}

#endif // MODEL_H