import os

def split_file(file_path, chunk_size_mb=80):
    file_size = os.path.getsize(file_path)
    chunk_size = chunk_size_mb * 1024 * 1024  # 80MB per chunk
    
    with open(file_path, 'rb') as f:
        chunk_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            with open(f"{file_path}.part{chunk_num}", 'wb') as chunk_file:
                chunk_file.write(chunk)
            print(f"Created: {file_path}.part{chunk_num}")
            chunk_num += 1

# Isay apne model par chalayein
split_file('best_model.pt')