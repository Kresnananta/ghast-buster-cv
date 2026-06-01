# Project Progress

This document tracks the development progress of **Ghast Buster CV**.

## Completed

- [x] Real-time camera with horizontal mirroring.
- [x] HSV hand tracking using mask, morphology, contour detection, and image moments.
- [x] Camera calibration tool with HSV trackbars.
- [x] Export HSV presets to `.json` files.
- [x] Import HSV presets from the main menu.
- [x] Modularized the project into several files: vision, renderer, game, menu, preset, asset loader, audio, and death screen.
- [x] Manual alpha blending for transparent PNG sprites.
- [x] Shield sprite follows the hand centroid.
- [x] Ghast enemy with idle GIF, shooting sprite, randomized movement, and sprite mirroring.
- [x] Fireball burst attack with a randomized number of shots.
- [x] Collision detection between the shield and fireballs.
- [x] Deflect particle effect.
- [x] HP system.
- [x] Score system.
- [x] Main menu.
- [x] Countdown before gameplay.
- [x] Death screen with retry, main menu, and final score.
- [x] Audio feedback using `pygame.mixer`.

## Pending Documentation

- [ ] Add main menu screenshot.
- [ ] Add gameplay screenshot.
- [ ] Add calibration screenshot.
- [ ] Add death screen screenshot.
- [ ] Add video demonstration link.

## Future Improvements

- [ ] Add high score persistence.
- [ ] Add difficulty scaling.
- [ ] Add pause menu.
- [ ] Add battle background music.
- [ ] Add stronger JSON preset validation.
- [ ] Add fallback handling when the camera is unavailable.
