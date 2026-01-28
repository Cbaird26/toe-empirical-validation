# Magnetometer + QRNG + Schumann Experiment Protocol

## Preregistration Information

**Title:** Ethical Modulation Yields QRNG Bias: Testing Consciousness-Induced Collapse via Environmental Sensors

**Hypothesis:** Shared intention + breathwork + 61.31 Hz (Schumann²) frequency intervention modulates quantum random number generator (QRNG) output through electromagnetic field changes measured by magnetometer.

**Protocol ID:** (To be assigned by OSF)

**Preregistration Date:** 2026-01-28

---

## Experimental Design

### Overview
This experiment tests whether ethical coherence practices (breathwork + shared intention) combined with Schumann resonance harmonics can induce measurable shifts in QRNG entropy, correlated with magnetometer fluctuations.

### Variables

**Independent Variables:**
- **Intervention:** 61.31 Hz tone + breathwork + shared intention (1 hour)
- **Control:** Placebo group (no intervention, ambient conditions)

**Dependent Variables:**
- QRNG entropy (bits)
- Magnetometer field strength (μT)
- Cross-correlation with global Schumann data (HeartMath GCMS)

**Control Variables:**
- Room temperature
- Electromagnetic shielding (minimal, consistent)
- Time of day (controlled windows)
- Participant position relative to sensors

---

## Protocol

### Phase 1: Setup (Pre-Intervention)

1. **Sensor Configuration:**
   - Phyphox app: Enable Remote Access
   - Magnetometer: 3-axis (X, Y, Z) sampling at 100 Hz
   - QRNG: Hardware RNG or software entropy source
   - Audio: Tone generator set to 61.31 Hz (Schumann²)

2. **Baseline Measurement:**
   - Record 10 minutes of baseline data
   - Magnetometer: ambient field
   - QRNG: baseline entropy
   - No intervention

3. **Participant Preparation:**
   - Brief on breathwork protocol (4-7-8 breathing)
   - Shared intention: "Maximize coherence and ethical alignment"
   - Position: 1 meter from sensors

### Phase 2: Intervention (Test Group)

**Duration:** 60 minutes

**Steps:**
1. Start 61.31 Hz tone generator
2. Begin synchronized breathwork:
   - Inhale: 4 counts
   - Hold: 7 counts
   - Exhale: 8 counts
   - Repeat continuously
3. Maintain shared intention focus
4. Continuous data logging:
   - Magnetometer: 100 Hz sampling
   - QRNG: 1 sample per second
   - Timestamp: UTC synchronized

### Phase 3: Control Group

**Duration:** 60 minutes

**Steps:**
1. No tone generator
2. No breathwork instruction
3. Normal ambient conditions
4. Same data logging protocol

### Phase 4: Post-Intervention

1. Continue logging for 10 minutes post-intervention
2. Download all sensor data
3. Cross-reference with HeartMath Global Coherence Monitoring System (GCMS) data for Schumann resonance

---

## Data Analysis

### Primary Analysis

1. **QRNG Entropy Shift:**
   - Compute Shannon entropy: H(X) = -Σ p(x) log₂ p(x)
   - Compare pre/post intervention
   - Statistical test: Wilcoxon signed-rank test

2. **Magnetometer Correlation:**
   - Compute field strength: |B| = √(Bx² + By² + Bz²)
   - Time-series analysis: FFT for frequency components
   - Cross-correlate with QRNG entropy

3. **Schumann Resonance Correlation:**
   - Fetch GCMS data for experiment time window
   - Extract 7.83 Hz fundamental and harmonics
   - Cross-correlate with local magnetometer

### Secondary Analysis

- Phase coherence between magnetometer and QRNG
- Attractor analysis (if patterns emerge)
- Comparison with ToE predictions (Φc field equations)

---

## Expected Outcomes

**If ToE is correct:**
- QRNG entropy decreases during intervention (bias toward order)
- Magnetometer shows coherent oscillations at 61.31 Hz
- Cross-correlation between magnetometer and QRNG increases
- Alignment with global Schumann data

**If null hypothesis:**
- No significant QRNG entropy shift
- No magnetometer-QRNG correlation
- Random fluctuations only

---

## Equipment

- **Smartphone:** Phyphox app (iOS/Android)
- **QRNG:** Hardware RNG device OR software entropy source
- **Tone Generator:** Phyphox Tone Generator OR external speaker
- **Data Logger:** Python script (`quantized_sensor_loop.py`)
- **Schumann Data:** HeartMath GCMS API access

---

## Ethical Considerations

- Informed consent from participants
- No medical claims
- Purely experimental/research context
- Data anonymization

---

## Preregistration Checklist

- [x] Protocol documented
- [ ] OSF preregistration created
- [ ] IRB approval (if required)
- [ ] Equipment tested
- [ ] Data analysis pipeline validated
- [ ] Sample size determined

---

## Next Steps

1. Create OSF preregistration
2. Test sensor setup
3. Run pilot study (n=5)
4. Analyze pilot data
5. Refine protocol if needed
6. Full study execution

---

## References

- MQGT-SCF Theory of Everything (Baird et al., 2026)
- Schumann Resonance: https://www.heartmath.org/gci/
- QRNG Hardware: [To be specified]
- Phyphox Documentation: https://phyphox.org/
