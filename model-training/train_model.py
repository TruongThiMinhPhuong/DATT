"""
Example Training Script for Fruit Classification Model
This demonstrates how to train a custom model using your own dataset

Dataset Structure Expected:
dataset/
├── train/
│   ├── fresh_fruit/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   ├── spoiled_fruit/
│   │   ├── image1.jpg
│   │   └── ...
│   └── other/
│       ├── image1.jpg
│       └── ...
└── validation/
    ├── fresh_fruit/
    ├── spoiled_fruit/
    └── other/
"""

import os
import sys
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.001

# Dataset paths
TRAIN_DIR = 'dataset/train'
VAL_DIR = 'dataset/validation'

# Output
MODEL_OUTPUT_PATH = '../backend/models/fruit_classifier.h5'


def create_data_generators():
    """Create data generators with augmentation"""
    
    # Training data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Validation data (no augmentation, only rescaling)
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        VAL_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator


def build_model(num_classes=3):
    """
    Build transfer learning model using MobileNetV2
    
    Args:
        num_classes: Number of output classes
        
    Returns:
        Compiled Keras model
    """
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Build model
    inputs = keras.Input(shape=(*IMG_SIZE, 3))
    
    # Pre-trained base
    x = base_model(inputs, training=False)
    
    # Add custom layers
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model, base_model


def fine_tune_model(model, base_model, train_gen, val_gen):
    """
    Fine-tune the model by unfreezing some layers
    
    Args:
        model: Keras model
        base_model: Base MobileNetV2 model
        train_gen: Training data generator
        val_gen: Validation data generator
    """
    
    # Unfreeze the base model
    base_model.trainable = True
    
    # Freeze early layers, fine-tune later layers
    for layer in base_model.layers[:100]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE/10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("\nFine-tuning model...")
    
    # Fine-tune
    history_fine = model.fit(
        train_gen,
        epochs=10,
        validation_data=val_gen,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(patience=2, factor=0.5)
        ]
    )
    
    return history_fine


def main():
    """Main training function"""
    
    print("=" * 60)
    print("Fruit Classification Model Training")
    print("=" * 60)
    
    # Check if dataset exists
    if not os.path.exists(TRAIN_DIR):
        print(f"❌ Training directory not found: {TRAIN_DIR}")
        print("\nPlease organize your dataset as follows:")
        print("dataset/")
        print("├── train/")
        print("│   ├── fresh_fruit/")
        print("│   ├── spoiled_fruit/")
        print("│   └── other/")
        print("└── validation/")
        print("    ├── fresh_fruit/")
        print("    ├── spoiled_fruit/")
        print("    └── other/")
        return
    
    # Create data generators
    print("\n📊 Loading dataset...")
    train_gen, val_gen = create_data_generators()
    
    print(f"\nFound {train_gen.samples} training images")
    print(f"Found {val_gen.samples} validation images")
    print(f"Classes: {list(train_gen.class_indices.keys())}")
    
    # Build model
    print("\n🏗️  Building model...")
    model, base_model = build_model(num_classes=len(train_gen.class_indices))
    model.summary()
    
    # Initial training
    print("\n🚀 Starting initial training...")
    
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            'best_model_temp.h5',
            monitor='val_accuracy',
            save_best_only=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7
        )
    ]
    
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks
    )
    
    # Fine-tuning
    print("\n🎯 Fine-tuning model...")
    history_fine = fine_tune_model(model, base_model, train_gen, val_gen)
    
    # Evaluate
    print("\n📈 Evaluating model...")
    val_loss, val_accuracy = model.evaluate(val_gen)
    print(f"\nValidation Accuracy: {val_accuracy*100:.2f}%")
    print(f"Validation Loss: {val_loss:.4f}")
    
    # Save model
    print(f"\n💾 Saving model to {MODEL_OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    model.save(MODEL_OUTPUT_PATH)
    
    print("\n✅ Training complete!")
    print(f"Model saved to: {MODEL_OUTPUT_PATH}")
    
    # Save TensorFlow Lite version for mobile deployment
    print("\n📱 Converting to TensorFlow Lite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    tflite_path = MODEL_OUTPUT_PATH.replace('.h5', '.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"TFLite model saved to: {tflite_path}")
    
    print("\n" + "=" * 60)
    print("Training Summary")
    print("=" * 60)
    print(f"Final Validation Accuracy: {val_accuracy*100:.2f}%")
    print(f"Total Training Samples: {train_gen.samples}")
    print(f"Total Validation Samples: {val_gen.samples}")
    print(f"Model Size: {os.path.getsize(MODEL_OUTPUT_PATH) / 1024 / 1024:.2f} MB")
    print("=" * 60)


if __name__ == "__main__":
    # Set GPU memory growth (if using GPU)
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)
    
    main()
