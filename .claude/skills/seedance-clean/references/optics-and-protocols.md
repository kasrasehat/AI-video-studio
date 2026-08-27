# Optics and Special Protocols

Read this reference only when the shot needs deliberate optics, extreme FOV,
special transitions, or mixed-speed/pressure effects.

## Shot sizes

| Abbreviation | Meaning | Visible area |
|---|---|---|
| ECU | Extreme close-up | one detail: eyes, hand, button, headlight |
| CU | Close-up | full face or one large element |
| MCU | Medium close-up | head and shoulders |
| MS | Medium shot | roughly to the waist |
| WS | Wide shot | full figure and surroundings |
| EWS | Extreme wide | location and scale |

## FOV anchors

Use these discrete FOV values in prompt text; do not use millimeters or invent
intermediate degree values.

| FOV | Approximate lens character | Use |
|---:|---|---|
| 180° | fisheye | spherical POV or dream-state distortion |
| 107° | architectural ultra-wide | huge interiors and epic establishes |
| 84° | wide | establishes and group blocking |
| 63° | observational wide | reportage and spatial intimacy |
| 47° | neutral human perspective | medium and general coverage |
| 29° | portrait compression | dialogue bust and isolation |
| 18° | close portrait | identity-preserving close work |
| 12° | tele detail | distant hands, objects, details on a wide field |
| 8° | extreme compression | observation and broadcast behavior |

For multishot prompts, state FOV per segment and add `no drift mid-segment` where
the segment must retain its optical geometry.

## Optical patterns

### Observation / hidden-vantage pattern

Use all three together:

1. An out-of-focus foreground obstruction over 20–30% of frame.
2. Fog, dust, shimmer, or another visible air layer between camera and subject.
3. A distant 8°–12° operator position.

Change occlusion type between beats while retaining one physical vantage.

### Sports broadcast

Use `8° super-tele`, `handheld 1–2 cm tremor`, and an operator anchored at
distance who finds and follows the action.

### Detail-on-wide

Use `84° wide FOV`, camera near ground level and close to a small foreground
object so it enlarges while the environment recedes deeply.

### Intimate wide

Use `63°–84° wide FOV` close to a centered face so the environment remains
readable without portrait blur.

### Compressed air column

At 8°–12°, explicitly describe visible depth: dust suspended in the compressed
air column or heat shimmer compressed across the foreground.

## Extreme-FOV multishot consistency stack

For multishot sequences using 8° or 107°, apply all four:

1. One sequence-wide identity and location lock.
2. A `LENS LOCK` opener with the exact FOV at every beat.
3. A `LENS CHECK` closer confirming the same FOV at every beat.
4. Color expressed through material, light, and compositional role.

## Whip-pan timing

Use enough time for blur to exist:

```text
0.0s to 0.3s — Subject A settled.
0.3s to 0.8s — camera accelerates into whip motion blur.
0.8s to 1.4s — Subject B resolves and settles.
```

A shorter whip often reads as a hard cut.

## Mixed time speeds

Separate real-time and slow-motion segments with hard cuts. Keep one speed mode
for the full duration of each segment and state it in `OUTPUT SETTINGS`.

## Pressure cracks without an impact

Describe a continuous pressure mechanism and visible propagation:

- the crowd presses with sustained body weight;
- fracture originates at an edge under stress;
- the crack travels edge-to-center in ordered stages;
- the surface remains under compression as fragments separate.

Use positive physical targets rather than an anti-impact negative clause.

## Giant scale

Express scale relative to a human body, such as `as tall as four adults stacked
head to toe`, and reinforce it with contact shadows, displaced air, ground
compression, and appropriately delayed mass.

## Color, light, and camera finish

- Fix white balance within a scene: 3200K, 4000K, 5600K, or 8500K are useful
  anchors rather than mandatory presets.
- Describe tonal latitude, highlight roll-off, and color response as visible
  behavior, not equipment names.
- Keep the camera on the shadow side and state its operator axis unless a designed
  axis change is part of the shot.
- Describe color as material receiving a light source in a compositional role:
  `a crimson silk scarf catches the cool corridor spill`, not `red and blue`.
