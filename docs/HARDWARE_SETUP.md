# Hardware Setup Guide

Complete wiring instructions for the AI Fruit Classification Conveyor System.

## ⚠️ Safety First

- **Disconnect power** before making any connections
- **Double-check polarity** to avoid damaging components
- **Use appropriate power supplies** (5V 3A for Raspberry Pi)
- **Insulate exposed connections** to prevent short circuits

## 📋 Components List

| Component | Quantity | Notes |
|-----------|----------|-------|
| Raspberry Pi 4 (8GB) | 1 | Main controller |
| 5V 3A Power Supply | 1 | For Raspberry Pi |
| Camera Module 5MP | 1 | 1080p capable |
| MG996R Servo Motor | 1 | 180° rotation |
| L298N Motor Driver | 1 | Dual H-bridge |
| JGB37-545 Conveyor Motor | 1 | 12V DC geared motor |
| 12V Power Supply | 1 | For motors (2A+) |
| IR/Proximity Sensor | 1 | For fruit detection |
| Breadboard | 1 | For prototyping |
| Jumper Wires | 20+ | Male-to-female, male-to-male |

## 🔌 Pin Connections

### GPIO Pin Configuration (BCM Mode)

```
Raspberry Pi 4 GPIO Pinout (BCM):
┌─────────┬──────────┐
│ 3.3V    │ 5V       │
│ GPIO 2  │ 5V       │
│ GPIO 3  │ GND      │
│ GPIO 4  │ GPIO 14  │
│ GND     │ GPIO 15  │
│ GPIO 17 │ GPIO 18  │ ← Servo PWM
│ GPIO 27 │ GND      │ ← Conveyor IN1/GND
│ GPIO 22 │ GPIO 23  │ ← Conveyor IN2/Sensor
│ 3.3V    │ GPIO 24  │
│ GPIO 10 │ GND      │
└─────────┴──────────┘
```

## 🎥 Camera Module Connection

**Camera Ribbon Cable:**

1. Locate the **CSI camera port** on Raspberry Pi (between HDMI and audio jack)
2. Gently pull up the black plastic clip
3. Insert ribbon cable with **blue side facing audio jack**
4. Contacts should face **away from the audio jack**
5. Push down the black clip to secure

```
┌─────────────────────────┐
│    Raspberry Pi 4       │
│                         │
│  [HDMI] [CSI] [Audio]  │
│           ↑             │
│      Camera Cable       │
│    (Blue side out)      │
└─────────────────────────┘
```

## 🎯 Servo Motor (MG996R) Wiring

**Servo Specs:**
- Operating Voltage: 4.8V - 6V
- Control Signal: PWM (50Hz)
- Rotation: 0° - 180°

**Connections:**

| Servo Wire | Color | Connect To |
|------------|-------|------------|
| Signal | Orange/Yellow | GPIO 18 (Pin 12) |
| Power | Red | 5V (Pin 2 or 4) |
| Ground | Brown/Black | GND (Pin 6) |

```
Servo Motor
┌─────────┐
│  MG996R │
└─┬──┬──┬─┘
  │  │  │
  O  R  B  (Orange, Red, Brown)
  │  │  │
  │  │  └──── GND (Pin 6)
  │  └─────── 5V (Pin 2)
  └────────── GPIO 18 (Pin 12)
```

> **Note**: For heavy-duty servo operation, consider using an external 5V power supply (with common ground).

## 🚗 Conveyor Motor + L298N Driver Wiring

**L298N Motor Driver Specs:**
- Operating Voltage: 5V - 35V
- Max Current: 2A per channel
- Logic Voltage: 5V

**Motor Driver Connections:**

### Power Connections

| L298N Terminal | Connect To |
|----------------|------------|
| 12V | 12V Power Supply (+) |
| GND | 12V Power Supply (-) AND Raspberry Pi GND |
| 5V Output | **DO NOT USE** (remove jumper if present) |

### Motor Connections

| L298N Terminal | Connect To |
|----------------|------------|
| OUT1 | Conveyor Motor (+) |
| OUT2 | Conveyor Motor (-) |

### Control Connections (Raspberry Pi)

| L298N Pin | GPIO Pin (BCM) | Physical Pin | Function |
|-----------|----------------|--------------|----------|
| ENA | GPIO 17 | Pin 11 | Speed control (PWM) |
| IN1 | GPIO 27 | Pin 13 | Direction control |
| IN2 | GPIO 22 | Pin 15 | Direction control |

**Wiring Diagram:**

```
                    12V Power Supply
                    ┌────┬────┐
                    │ +  │ -  │
                    └─┬──┴─┬──┘
                      │    │
             ┌────────┘    └────────┐
             │                      │
        ┌────▼────────────────────▼──┐
        │      L298N Motor Driver    │
        │                            │
        │  12V  GND  5V  ENA IN1 IN2 │
        └───────┬────────┬───┬───┬───┘
                │        │   │   │
                │    ┌───┘   │   │
                │    │   ┌───┘   │
                │    │   │   ┌───┘
        GND ────┘    │   │   │
        (Pi Pin 6)   │   │   │
                     │   │   │
    GPIO 17 ─────────┘   │   │
    (Pi Pin 11)          │   │
                         │   │
    GPIO 27 ─────────────┘   │
    (Pi Pin 13)              │
                             │
    GPIO 22 ─────────────────┘
    (Pi Pin 15)

        OUT1  OUT2
        └─┬────┬─┘
          │    │
       ┌──▼────▼──┐
       │ Conveyor │
       │  Motor   │
       └──────────┘
```

**Important Notes:**
- **Common Ground**: Connect Raspberry Pi GND to L298N GND
- **ENA Jumper**: Keep ENA jumper removed for PWM speed control
- **Motor Direction**: If motor runs backward, swap OUT1 and OUT2

## 📡 IR/Proximity Sensor (Fruit Detection)

**Typical IR Sensor:**
- Operating Voltage: 3.3V - 5V
- Output: Digital (HIGH when object detected)

**Connections:**

| Sensor Pin | Connect To |
|------------|------------|
| VCC | 5V (Pin 2) |
| GND | GND (Pin 6) |
| OUT | GPIO 23 (Pin 16) |

```
IR Sensor
┌─────────┐
│  ┌───┐  │
│  │ · │  │  (Detection area)
│  └───┘  │
└─┬──┬──┬─┘
  V  G  O  (VCC, GND, OUT)
  │  │  │
  │  │  └──── GPIO 23 (Pin 16)
  │  └─────── GND (Pin 6)
  └────────── 5V (Pin 2)
```

## 🔋 Power Supply Setup

### Option 1: Separate Power Supplies (Recommended)

```
5V 3A PSU ──────► Raspberry Pi 4 (USB-C)
                  │
                  └──► Servo Motor (via GPIO 5V - light loads only)

12V 2A PSU ─────► L298N Motor Driver
                  │
                  └──► Conveyor Motor
```

### Option 2: Single Power Supply with Regulators

If using a single 12V power supply:
- Use a **buck converter** to step down 12V to 5V (3A) for Raspberry Pi
- Power motors directly from 12V
- **Always use separate regulators** - don't backfeed Raspberry Pi from L298N 5V pin

## ⚡ Complete Wiring Schematic

```
┌──────────────────────────────────────────────────────────┐
│                    Raspberry Pi 4                        │
│                                                          │
│  5V ──┬── Servo (Red)                                   │
│  GND ─┼── Servo (Brown)                                 │
│       ├── L298N GND ──── 12V PSU (-)                    │
│       ├── IR Sensor GND                                 │
│  5V ──┴── IR Sensor VCC                                 │
│                                                          │
│  GPIO 18 ── Servo Signal (Orange)                       │
│  GPIO 17 ── L298N ENA                                   │
│  GPIO 27 ── L298N IN1                                   │
│  GPIO 22 ── L298N IN2                                   │
│  GPIO 23 ── IR Sensor OUT                               │
│                                                          │
│  CSI Port ── Camera Module                              │
└──────────────────────────────────────────────────────────┘

      12V PSU (+) ──── L298N 12V

┌──────────────────────┐
│   L298N Driver       │
│                      │
│  OUT1 ─┬─ Motor (+)  │
│  OUT2 ─┴─ Motor (-)  │
└──────────────────────┘
```

## 🧪 Testing Procedure

### 1. Test GPIO Pins
```bash
# Test individual GPIO
gpio readall  # If gpio utility installed
```

### 2. Test Servo
```bash
cd raspberry-pi
python motor_controller.py
```

### 3. Test Conveyor
```bash
# Run motor controller test
# Should move servo and start/stop conveyor
```

### 4. Test Camera
```bash
cd raspberry-pi
python camera_module.py
```

### 5. Test Sensor
```bash
# Monitor GPIO 23
gpio -g mode 23 in
gpio -g read 23
```

## 🐛 Hardware Troubleshooting

### Servo Not Moving
- Check PWM signal on GPIO 18
- Verify 5V power connection
- Test with external 5V power supply

### Conveyor Not Running
- Check 12V power supply
- Verify L298N connections
- Test motor directly with 12V
- Check ENA jumper is removed

### Camera Not Detected
```bash
vcgencmd get_camera
# Should show: supported=1 detected=1

# Enable camera interface
sudo raspi-config
# Interface Options → Camera → Enable
```

### Sensor Not Detecting
- Adjust sensitivity potentiometer on sensor
- Check detection range (usually 2-30cm)
- Test with reflective object

## 📐 Mechanical Assembly

### Conveyor Belt Setup
1. Mount conveyor motor securely
2. Align belt for smooth operation
3. Position servo at sorting junction
4. Mount camera above belt with clear view

### Sorting Mechanism
- Servo arm should deflect items at junction
- **Center (90°)**: Items continue straight
- **Left (30°)**: Items diverted left
- **Right (150°)**: Items diverted right

### Sensor Placement
- Position IR sensor **before** camera
- Allows time for image capture
- Height: Adjust to reliably detect fruit

```
Flow Direction: ─────────►

  IR Sensor    Camera    Servo Arm
      │          │          │
      ▼          ▼          ▼
┌──────────────────────────────────┐
│  ■         [ ]         /         │  Conveyor Belt
└──────────────────────────────────┘
    │          │          │
  Detect     Capture    Sort
```

## ✅ Final Checklist

- [ ] All power supplies connected properly
- [ ] Common ground established
- [ ] Servo tested (left, center, right)
- [ ] Conveyor motor tested (forward/stop)
- [ ] Camera detected and tested
- [ ] Sensor triggers reliably
- [ ] No loose connections
- [ ] Proper insulation on connections
- [ ] Emergency stop accessible

## 🔧 Calibration

After hardware setup, calibrate in [config.py](raspberry-pi/config.py):

```python
# Adjust these values based on your setup
SERVO_ANGLE_LEFT = 30      # Calibrate for left sorting
SERVO_ANGLE_CENTER = 90    # Calibrate for straight
SERVO_ANGLE_RIGHT = 150    # Calibrate for right sorting

CONVEYOR_SPEED = 75        # Adjust belt speed (0-100)
```

---

**Questions or issues? Check the [main README](README.md) for troubleshooting!**
