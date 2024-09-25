import os
import csv
import shutil
from collections import defaultdict
import random
import argparse


def read_labels(csv_path):
    """
    Reads the CSV file and creates a dictionary mapping image names to emotion labels.
    Assumes that the image name is in column index 1 and the emotion label is in column index 2.
    """
    labels_dict = {}
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if present
        for row in reader:
            image_name = row[1]
            emotion = row[2]
            labels_dict[image_name] = emotion
    return labels_dict


def get_emotions(labels_dict):
    """
    Returns a set of unique emotions from the labels dictionary.
    """
    return set(labels_dict.values())


def create_directories(output_dir, emotions):
    """
    Creates the train and test directories with subdirectories for each emotion label.
    """
    for split in ['train', 'test']:
        split_dir = os.path.join(output_dir, split)
        os.makedirs(split_dir, exist_ok=True)
        for emotion in emotions:
            emotion_dir = os.path.join(split_dir, emotion)
            os.makedirs(emotion_dir, exist_ok=True)


def organize_dataset(image_dir, csv_path, output_dir, num_images_per_emotion):
    """
    Organizes the dataset by copying images into train and test directories with labeled subfolders.
    """
    # Read labels and get unique emotions
    labels_dict = read_labels(csv_path)
    emotions = get_emotions(labels_dict)
    create_directories(output_dir, emotions)

    # Collect images for each emotion
    emotion_images = defaultdict(list)
    for image_name, emotion in labels_dict.items():
        emotion_images[emotion].append(image_name)

    # Process each emotion category
    for emotion, images in emotion_images.items():
        # Shuffle images to ensure random distribution
        random.shuffle(images)
        # Select the specified number of images per emotion
        selected_images = images[:num_images_per_emotion]
        num_selected = len(selected_images)
        if num_selected < num_images_per_emotion:
            print(f"Warning: Only {num_selected} images found for emotion '{emotion}'")
        # Split into train and test sets (80% train, 20% test)
        split_idx = int(0.8 * num_selected)
        train_images = selected_images[:split_idx]
        test_images = selected_images[split_idx:]

        # Copy images to train directory
        for image_name in train_images:
            src_path = os.path.join(image_dir, image_name)
            dst_path = os.path.join(output_dir, 'train', emotion, image_name)
            shutil.copy(src_path, dst_path)

        # Copy images to test directory
        for image_name in test_images:
            src_path = os.path.join(image_dir, image_name)
            dst_path = os.path.join(output_dir, 'test', emotion, image_name)
            shutil.copy(src_path, dst_path)

    print("Dataset organized successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Organize facial expression images into train and test datasets.')
    parser.add_argument('-i', '--image_dir', type=str, required=True, help='Path to your images directory.')
    parser.add_argument('-c', '--csv_path', type=str, required=True, help='Path to your CSV file containing labels.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Path where you want the organized dataset.')
    parser.add_argument('-n', '--num_images_per_emotion', type=int, required=True, help='Number of images per emotion.')

    args = parser.parse_args()

    organize_dataset(
        image_dir=args.image_dir,
        csv_path=args.csv_path,
        output_dir=args.output_dir,
        num_images_per_emotion=args.num_images_per_emotion
    )
