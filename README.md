### Parameters

- `-i`, `--image_dir`: Path to your images directory.
- `-c`, `--csv_path`: Path to your CSV file containing labels.
- `-o`, `--output_dir`: Path where you want the organized dataset to be saved.
- `-n`, `--num_images_per_emotion`: Number of images per emotion category.

### How to use:
```bash
python preprocess_dataset.py -i ".\images\" -c ".\data\500_picts_satz.csv" -o "<dataset name>" -n <num items>
```
