# 📸 Single Image Engagement Analyzer - User Guide

## Overview

The **Image Engagement Analyzer** (`analyze_image.py`) is a powerful tool that analyzes student engagement from a single photo using AI ensemble models and provides detailed explanations of the results.

## ✨ Features

### 1. **Comprehensive Engagement Analysis**
- **Engagement Score** (0-100%)
- **4 Emotional States**: Boredom, Engagement, Confusion, Frustration
- Each with confidence levels and detailed probabilities

### 2. **Explainable AI (XAI)**
- **Feature Importance Analysis**: Shows which facial regions contribute most
  - Eyes
  - Eyebrows  
  - Nose
  - Mouth
  - Face shape
- **Actionable Insights**: Specific recommendations based on detected states
- **Confidence Scores**: Transparency in predictions

### 3. **Rich Visualizations**
- Original image with engagement overlay
- Emotional state radar chart
- Feature importance bar chart
- Detailed emotion level breakdown
- AI insights and recommendations panel

### 4. **Multiple Output Formats**
- **JSON Report**: Machine-readable detailed analysis
- **PNG Visualization**: Comprehensive visual report
- **Console Output**: Human-readable summary

---

## 🚀 Quick Start

### Basic Usage

```bash
python analyze_image.py path/to/your/image.jpg
```

This will:
1. Analyze the image using balanced mode (default)
2. Generate a JSON report
3. Create a visualization PNG
4. Display results in console

### Example Output

```
======================================================================
  ✅ ANALYSIS RESULTS
======================================================================

Engagement Level: High
Engagement Score: 66.7%

Emotional States:
  • Boredom     : High       ( 40.8% confidence)
  • Engagement  : High       ( 49.2% confidence)
  • Confusion   : Very Low   ( 54.1% confidence)
  • Frustration : Very Low   ( 58.2% confidence)

======================================================================
AI INSIGHTS & RECOMMENDATIONS
======================================================================

Student shows good engagement (66.7%)
Generally positive learning state
⚠️ High boredom detected (40.8% confidence)
Recommendation: Introduce interactive elements or change pace

Most informative facial region: nose (21.8%)
```

---

## 📋 Command Line Options

### Prediction Modes

Choose between speed and accuracy:

```bash
# Fast mode - Quick analysis (~66ms, Transformer only)
python analyze_image.py image.jpg --mode fast

# Balanced mode - Default, good balance (~126ms, 2 models)
python analyze_image.py image.jpg --mode balanced

# Accurate mode - Maximum accuracy (~173ms, all 3 models)
python analyze_image.py image.jpg --mode accurate
```

### Output Control

```bash
# Skip visualization generation (faster)
python analyze_image.py image.jpg --no-viz

# Skip JSON report generation
python analyze_image.py image.jpg --no-report

# Both options combined
python analyze_image.py image.jpg --mode fast --no-viz --no-report
```

---

## 📊 Understanding the Results

### Engagement Score Interpretation

| Score Range | Level | Meaning |
|-------------|-------|---------|
| 75-100% | Very High 🎯 | Excellent engagement, student is highly focused |
| 50-74% | High ✅ | Good engagement, positive learning state |
| 25-49% | Moderate ⚠️ | Some distraction or confusion detected |
| 0-24% | Low ❌ | Significant disengagement, intervention needed |

### Emotional States

#### **Boredom**
- **Very Low**: Student is interested and engaged
- **Low**: Minor signs of repetition or monotony
- **High**: Clear signs of disinterest
- **Very High**: Strong indicators of boredom

#### **Engagement**
- **Very Low**: Student is disengaged
- **Low**: Minimal attention to content
- **High**: Good focus and attention
- **Very High**: Excellent concentration

#### **Confusion**
- **Very Low**: Clear understanding
- **Low**: Minor uncertainty
- **High**: Struggling with concepts
- **Very High**: Significant comprehension issues

#### **Frustration**
- **Very Low**: Calm and comfortable
- **Low**: Minor challenges
- **High**: Experiencing difficulty
- **Very High**: High stress or frustration

### Feature Importance

Shows which facial regions were most informative:

- **Eyes** (19%): Gaze direction, blink rate, eye openness
- **Eyebrows** (18%): Expression indicators, concentration
- **Nose** (22%): Central anchor point, head pose
- **Mouth** (22%): Smile, tension, speaking
- **Face Shape** (19%): Overall head position, posture

Higher percentages indicate greater contribution to the engagement prediction.

---

## 🎯 Use Cases

### 1. **Live Lecture Analysis**
Capture student photos during class and analyze engagement patterns:

```bash
python analyze_image.py lecture_snapshot.jpg --mode fast
```

### 2. **Historical Data Analysis**
Analyze previously captured frames:

```bash
# Process multiple images
for image in captured_frames/*.jpg; do
    python analyze_image.py "$image" --mode balanced
done
```

### 3. **Research & Testing**
Generate detailed reports for research purposes:

```bash
python analyze_image.py test_image.jpg --mode accurate
```

### 4. **Quick Checks**
Fast engagement check without full reports:

```bash
python analyze_image.py snapshot.jpg --mode fast --no-viz --no-report
```

---

## 📁 Output Files

### Generated Files (per image)

1. **JSON Report**: `analysis_<imagename>.json`
   - Complete analysis data
   - Machine-readable format
   - Includes all probabilities and metrics

2. **Visualization**: `analysis_<imagename>.png`
   - 6-panel comprehensive visualization
   - Original image + engagement overlay
   - Emotional radar chart
   - Feature importance bars
   - Emotion level breakdown
   - AI insights panel

### Example File Structure

```
captured_frames/
├── student_photo.jpg                          # Original image
├── analysis_student_photo.json                # JSON report
└── analysis_student_photo.png                 # Visualization
```

---

## 🔍 Explainable AI Insights

### What Makes This "Explainable"?

1. **Feature Attribution**
   - Shows which facial regions contribute most
   - Quantifies importance (percentages)
   - Helps understand what the model "looks at"

2. **Confidence Scores**
   - Every prediction includes confidence level
   - Full probability distributions available
   - Transparency in uncertainty

3. **Actionable Recommendations**
   - Specific interventions based on detected states
   - Contextual advice for instructors
   - Evidence-based suggestions

4. **Visual Explanations**
   - Radar charts show emotional state balance
   - Bar charts reveal feature importance
   - Color-coded severity levels

### Example Insights

```
✓ Low boredom indicates sustained interest

⚠️ High boredom detected (40.8% confidence)
Recommendation: Introduce interactive elements or change pace

⚠️ Confusion detected (65.3% confidence)
Recommendation: Clarify current topic or provide examples

Most informative facial region: eyes (24.5%)
```

---

## 🎨 Visualization Components

The generated PNG includes 6 panels:

### 1. **Original Image + Score**
- Full-color original photo
- Engagement level with emoji
- Percentage score
- Color-coded (green/yellow/red)

### 2. **Emotional States Radar**
- 4 emotions plotted on radar chart
- Shows confidence for each state
- Easy pattern recognition

### 3. **Feature Importance Bars**
- Horizontal bars for each facial region
- Percentage contribution
- Color gradient for visual appeal

### 4. **Emotion Level Breakdown**
- Detailed 4-level probabilities
- Grouped bar chart
- Shows full distribution

### 5. **AI Insights Panel**
- Text box with key findings
- Specific recommendations
- Highlighted warnings

---

## 🛠️ Technical Details

### Model Architecture
- **Ensemble of 3 Models**:
  1. Transformer (Vision Transformer) - 59.6% accuracy
  2. BiLSTM Enhanced - 58.6% accuracy
  3. Fusion Model - 57.4% accuracy
- **Feature Extraction**: MediaPipe Face Mesh (35 dimensions)
- **Sequence Length**: 30 frames (single image repeated)

### Performance

| Mode | Speed | Models Used | Accuracy |
|------|-------|-------------|----------|
| Fast | ~66ms | Transformer only | Good |
| Balanced | ~126ms | Transformer + BiLSTM | Better |
| Accurate | ~173ms | All 3 models | Best |

### Requirements
- **Python 3.11+**
- **TensorFlow 2.18+**
- **MediaPipe** for face detection
- **Matplotlib** + **Seaborn** for visualization
- **OpenCV** for image processing

---

## 📝 Example Workflow

### Complete Analysis Pipeline

```bash
# Step 1: Capture or select an image
IMAGE="student_frame_001.jpg"

# Step 2: Run analysis with balanced mode
python analyze_image.py "$IMAGE" --mode balanced

# Step 3: Review console output
# Engagement Level: High
# Engagement Score: 66.7%

# Step 4: Open visualization
# analysis_student_frame_001.png

# Step 5: Review JSON for detailed data
# analysis_student_frame_001.json
```

---

## 🚨 Troubleshooting

### "No face detected in the image"

**Causes:**
- Face not visible or turned away
- Poor lighting conditions
- Image too blurry
- Face too small in frame

**Solutions:**
- Ensure face is clearly visible
- Use good lighting
- Face should be front-facing
- Minimum face size: ~100x100 pixels

### Slow Performance

**Solutions:**
- Use `--mode fast` for speed
- Skip visualization with `--no-viz`
- Ensure GPU drivers are updated (if using GPU)

### Import Errors

```bash
# Reinstall dependencies
pip install tensorflow==2.18.0 mediapipe matplotlib seaborn opencv-python
```

---

## 🎓 Best Practices

### For Instructors

1. **Regular Snapshots**: Take periodic photos during lectures
2. **Compare Patterns**: Look for engagement trends over time
3. **Act on Insights**: Use recommendations to adjust teaching
4. **Privacy**: Always obtain student consent for photos

### For Researchers

1. **Use Accurate Mode**: Maximum precision for research
2. **Save All Reports**: Keep JSON files for analysis
3. **Document Context**: Note lecture topic, time, etc.
4. **Validate Results**: Cross-reference with other metrics

### For Developers

1. **Batch Processing**: Process multiple images programmatically
2. **Parse JSON**: Extract data for custom analysis
3. **Integrate**: Use as part of larger system
4. **Monitor Performance**: Track inference times

---

## 📚 Related Documentation

- **ENSEMBLE_GUIDE.md** - Comprehensive ensemble system documentation
- **ENSEMBLE_IMPLEMENTATION.md** - Technical implementation details
- **ensemble_validation_report.json** - Model validation results

---

## 💡 Tips & Tricks

### Batch Processing

```python
# Python script for batch analysis
import os
import glob

images = glob.glob("captured_frames/*.jpg")
for img in images:
    os.system(f'python analyze_image.py "{img}" --mode balanced')
```

### Custom Thresholds

Edit the `explain_prediction` method in `analyze_image.py` to adjust thresholds:

```python
# Change engagement level thresholds
if engagement_score >= 75:  # Very High
elif engagement_score >= 50:  # High
elif engagement_score >= 25:  # Moderate
else:  # Low
```

### Extract Specific Data

```python
# Python script to extract engagement scores
import json
import glob

scores = []
for json_file in glob.glob("**/analysis_*.json", recursive=True):
    with open(json_file) as f:
        data = json.load(f)
        scores.append(data['prediction']['engagement_score'])

print(f"Average engagement: {sum(scores)/len(scores):.1f}%")
```

---

## 🎉 Success Stories

### Validation Results

From our validation on real student data:

- **Average Improvement**: +30.84% over baseline
- **Session 1**: 66.7% ensemble vs 48.1% baseline → **+18.6%**
- **Session 2**: 100.0% ensemble vs 48.2% baseline → **+51.8%**
- **Session 3**: 66.7% ensemble vs 44.5% baseline → **+22.2%**

The ensemble approach with explainable AI provides significantly better engagement detection compared to traditional methods!

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Test with sample images provided

---

**Version**: 1.0  
**Last Updated**: November 24, 2025  
**Status**: Production Ready ✅
