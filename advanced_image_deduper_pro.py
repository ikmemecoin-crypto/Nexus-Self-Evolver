Create a production-ready, fully commented command-line Python tool that intelligently finds and manages duplicate and near-duplicate images in a user-specified folder and all subfolders. Requirements:

Use Pillow for image processing and implement perceptual hashing (pHash) – not simple average hash – to detect near-duplicates robustly against resizing, minor edits, and compression.
Support a configurable similarity threshold (default 85%) using Hamming distance – lower distance = more similar.
Recursively scan the directory, group images into clusters: exact duplicates (hash match) and near-duplicate groups.
For each group with more than one image:
Keep the highest-resolution (or earliest modified) image as the "master"
Move duplicates/near-duplicates to a "duplicates_found" subfolder with original path preserved in substructure
Optionally delete instead of move (via --delete flag)

Generate a detailed Pandas DataFrame report saved as "dedupe_report.csv" with columns: group_id, master_path, duplicate_paths (list), similarity_scores, action_taken, original_sizes, resolutions.
Use argparse for CLI options:
--folder (required)
--threshold (0-100, default 85)
--delete (flag)
--threads N (multithreaded hashing with concurrent.futures for speed)
--verbose

Full error handling (missing folders, corrupt images, permissions), progress bar with tqdm, and logging.
Make it fast and memory-efficient (process in batches if needed). Include a main() function and if name == "main".
Add a bonus visualization: generate a simple contact sheet (grid thumbnail image) using Pillow for each near-duplicate group >2 images, saved in the duplicates folder.

This task is deliberately very hard because it combines:

Advanced image hashing algorithm implementation from scratch (pHash requires DCT – Gemini must get the math right)
Clustering logic
File system operations with path preservation
Multithreading
Pandas reporting
CLI polish
Visualization bonus
Real-world robustness

Gemini 1.5 Flash will have to reason deeply to get this perfect. Most models would produce buggy or incomplete versions.