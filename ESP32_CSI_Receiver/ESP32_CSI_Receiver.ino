#include "WiFi.h"
#include "esp_wifi.h"
#include "model.h"  // Directs the compiler to look at your side-by-side model.h file

// A buffer to hold computed amplitudes for 128 subcarriers
float subcarrier_amplitudes[128];

// Custom callback function: Executes automatically every time a Wi-Fi packet is sniffed
void csi_rx_callback(void *ctx, wifi_csi_info_t *data) {
    if (!data || !data->buf) {
        return;
    }

    // Point to the raw incoming data buffer
    int8_t *csi_buf = (int8_t *)data->buf;
    
    // Convert Real and Imaginary components into an Absolute Amplitude value
    for (int i = 0; i < 128; i++) {
        float i_val = (float)csi_buf[i * 2];
        float r_val = (float)csi_buf[(i * 2) + 1];
        
        // Amplitude formula: sqrt(I^2 + R^2)
        subcarrier_amplitudes[i] = sqrt((i_val * i_val) + (r_val * r_val));
    }

    // Call the function from model.h to get the classification prediction
    int predicted_class = predict_activity(subcarrier_amplitudes);

    // Stream the outcome to your laptop's Serial Monitor
    Serial.print("Live Activity Detection: ");
    if (predicted_class == 0) {
        Serial.println("STILL");
    } else if (predicted_class == 1) {
        Serial.println("MOVING");
    } else if (predicted_class == 2) {
        Serial.println("JUMPING");
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("System Booting: CSI Receiver + TinyML Classifier...");

    // Put the Wi-Fi hardware into Station Mode and disconnect from local networks
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();

    // Standard Wi-Fi configuration and initialization framework
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    // Lock the radio antenna onto Channel 1 to intercept the transmitter board
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

    // Turn on sniffer/promiscuous mode to read frames without full network authentication
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));

    // Configure the internal CSI data engine parameters using universal fields
    wifi_csi_config_t csi_config = {
        .lltf_en = true,
        .htltf_en = true,
        .ltf_merge_en = true,
        .channel_filter_en = true,
        .manu_scale = false
    };
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));

    // Register our callback function using the updated v3.x core name
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&csi_rx_callback, NULL));

    Serial.println("System Ready. Listening for live signal interruptions...");
}

void loop() {
    // Keep the main thread loop asleep since everything runs inside the event-driven callback
    delay(1000);
}