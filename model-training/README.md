# Model Training

Scripts for training custom fruit classification models.

## Quick Start

### 1. Prepare Your Dataset

Organize your images in this structure:

```
dataset/
├── train/
│   ├── fresh_fruit/
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   ├── spoiled_fruit/
│   │   ├── img1.jpg
│   │   └── ...
│   └── other/
│       ├── img1.jpg
│       └── ...
└── validation/
    ├── fresh_fruit/
    ├── spoiled_fruit/
    └── other/
```

**Recommendations:**
- **Fresh Fruit**: 500-1000+ images of fresh, healthy fruits
- **Spoiled Fruit**: 500-1000+ images of rotten, damaged fruits
- **Other**: 300-500+ images of non-fruit objects
- **Validation**: 20-30% of your total images for each category

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the Model

```bash
python train_model.py
```

The script will:
1. Load and augment your dataset
2. Train using transfer learning (MobileNetV2)
3. Fine-tune the model  
4. Save to `../backend/models/fruit_classifier.h5`
5. Create TensorFlow Lite version for deployment

## Dataset Sources

### Public Datasets

- **Fruits 360**: https://www.kaggle.com/moltean/fruits
- **Fruit Recognition**: https://www.kaggle.com/chrisfilo/fruit-recognition
- **Fresh and Rotten**: https://www.kaggle.com/sriramr/fruits-fresh-and-rotten-for-classification

### Creating Your Own Dataset

1. **Capture Images**: Use your Raspberry Pi camera
2. **Label Manually**: Organize into folders
3. **Data Augmentation**: The training script handles this automatically

## Training Tips

- **More data is better**: Aim for 500+ images per class
- **Balanced dataset**: Similar number of images in each category
- **Quality over quantity**: Ensure images are clear and well-lit
- **Variety**: Include different angles, lighting, and backgrounds
- **Real conditions**: Use images similar to production environment

## Model Configuration

Edit `train_model.py` to adjust:

```python
IMG_SIZE = (224, 224)    # Input image size
BATCH_SIZE = 32          # Batch size for training
EPOCHS = 20              # Number of training epochs
LEARNING_RATE = 0.001    # Initial learning rate
```

## Evaluating Your Model

After training, check:
- **Validation Accuracy**: Target 85%+ for good performance
- **Confusion Matrix**: Ensure no systematic misclassification
- **Real-world Testing**: Test with actual conveyor belt images

## Deployment

After training:

1. Model is saved to `../backend/models/fruit_classifier.h5`
2. Backend will automatically use this model
3. Restart `classifier_service.py` to load the new model

## Troubleshooting

### Low Accuracy
- Increase dataset size
- Add more diverse images
- Increase training epochs
- Try different augmentation strategies

### Overfitting
- Add more dropout
- Increase data augmentation
- Reduce model complexity
- Get more training data

### Out of Memory
- Reduce batch size
- Use smaller image size
- Use mixed precision training
- Enable GPU memory growth

## Advanced: Custom Architecture

To use a different base model:

```python
from tensorflow.keras.applications import EfficientNetB0

base_model = EfficientNetB0(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
```

Popular alternatives:
- **EfficientNetB0-B7**: Better accuracy, larger size
- **MobileNetV3**: More efficient for edge devices
- **ResNet50**: Classic architecture, good baseline

---

For questions, see the main [README](../README.md).
