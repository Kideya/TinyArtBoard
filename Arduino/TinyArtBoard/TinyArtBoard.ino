#include <FastLED.h>
#include "led_colors.h" 

#define DATA_PIN 10
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(255);
  FastLED.clear();

  // Farben aus ledColors übernehmen
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = ledColors[i];
  }

  FastLED.show();
}

void loop() {
  // Hier könntest du Effekte bauen – oder auch nichts machen.
}