import os
import csv
import shutil
from collections import defaultdict
import argparse


def read_labels(csv_path):
    """
    Reads the primary CSV file and creates a dictionary mapping emotion labels to image names.
    """
    emotion_images = defaultdict(set)
    emotions_set = set()
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if present
        for row in reader:
            image_name = row[1]
            emotion = row[2].strip().lower()  # Handle case sensitivity
            emotion_images[emotion].add(image_name)
            emotions_set.add(emotion)
    return emotion_images, emotions_set


def read_secondary_labels(csv_path, valid_emotions, label_mapping, primary_image_names):
    """
    Reads the secondary CSV file and collects image names for emotions present in the primary CSV,
    ensuring no duplicate images are included.
    """
    emotion_images = defaultdict(set)
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if present
        for row in reader:
            image_name = row[1]
            emotion = row[2].strip().lower()  # Handle case sensitivity
            # Map emotion labels if necessary
            emotion = label_mapping.get(emotion, emotion)
            if emotion in valid_emotions:
                if image_name not in primary_image_names:
                    emotion_images[emotion].add(image_name)
    return emotion_images


def create_directories(output_dir, emotions, training_sizes):
    """
    Creates the train and test directories with subdirectories for each emotion label.
    """
    # Create test directory (same for all training conditions)
    test_dir = os.path.join(output_dir, 'test')
    for emotion in emotions:
        emotion_dir = os.path.join(test_dir, emotion)
        os.makedirs(emotion_dir, exist_ok=True)

    # Create training directories for each training size
    for size in training_sizes:
        train_dir = os.path.join(output_dir, f'train_{size}')
        for emotion in emotions:
            emotion_dir = os.path.join(train_dir, emotion)
            os.makedirs(emotion_dir, exist_ok=True)


def organize_dataset(image_dir, primary_csv_path, secondary_csv_path, output_dir):
    """
    Organizes the dataset by copying images into multiple training sets with increasing sizes
    and a fixed test set. Uses the secondary CSV file to fill up images if necessary.
    """
    # Define the training sizes
    training_sizes = [10, 20, 30, 40, 50]

    # Read labels from the primary CSV file
    primary_emotion_images, valid_emotions = read_labels(primary_csv_path)
    # Keep track of all primary image names to avoid duplicates
    primary_image_names = set()
    for images in primary_emotion_images.values():
        primary_image_names.update(images)

    # Read labels from the secondary CSV file, only for valid emotions
    secondary_emotion_images = defaultdict(set)
    if secondary_csv_path:
        # Define emotion label mapping between CSV files if necessary
        label_mapping = {
            'sadness': 'sad',
            'happiness': 'happy',
            'fearful': 'fear',
            # Add more mappings if necessary
        }
        secondary_emotion_images = read_secondary_labels(secondary_csv_path, valid_emotions, label_mapping,
                                                         primary_image_names)

    create_directories(output_dir, valid_emotions, training_sizes)

    # Combine primary and secondary images per emotion
    combined_emotion_images = {}
    for emotion in valid_emotions:
        images = set()
        images.update(primary_emotion_images[emotion])
        images.update(secondary_emotion_images.get(emotion, set()))
        combined_emotion_images[emotion] = images

    # Process each emotion category
    for emotion in valid_emotions:
        images = list(combined_emotion_images[emotion])
        # Sort images to maintain consistent order
        images.sort()
        # Ensure at least 60 images are available
        if len(images) < 60:
            print(f"Warning: Only {len(images)} images found for emotion '{emotion}'. Need at least 60.")
            continue  # Skip this emotion if not enough images
        # Select the first 60 images
        selected_images = images[:60]
        # Split into training and test sets
        test_images = selected_images[-10:]  # Last 10 images for testing
        training_images_full = selected_images[:-10]  # First 50 images for training

        # Copy test images
        for image_name in test_images:
            src_path = os.path.join(image_dir, image_name)
            dst_path = os.path.join(output_dir, 'test', emotion, image_name)
            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
            else:
                print(f"Warning: Image {image_name} not found in image directory.")

        # Create training sets with increasing sizes
        for size in training_sizes:
            train_images = training_images_full[:size]  # Select the first 'size' images
            train_dir = os.path.join(output_dir, f'train_{size}', emotion)
            for image_name in train_images:
                src_path = os.path.join(image_dir, image_name)
                dst_path = os.path.join(train_dir, image_name)
                if os.path.exists(src_path):
                    shutil.copy(src_path, dst_path)
                else:
                    print(f"Warning: Image {image_name} not found in image directory.")

    print("Dataset organized successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Organize facial expression images into train and test datasets with varying training sizes.')
    parser.add_argument('-i', '--image_dir', type=str, required=True, help='Path to your images directory.')
    parser.add_argument('-p', '--primary_csv', type=str, required=True,
                        help='Path to your primary CSV file containing labels.')
    parser.add_argument('-s', '--secondary_csv', type=str, help='Path to your secondary CSV file containing labels.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Path where you want the organized dataset.')

    args = parser.parse_args()

    organize_dataset(
        image_dir=args.image_dir,
        primary_csv_path=args.primary_csv,
        secondary_csv_path=args.secondary_csv,
        output_dir=args.output_dir
    )
