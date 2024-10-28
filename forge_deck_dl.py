import os
import re
import requests

def extract_card_names(deck_file):
  """Extracts card names from a Forge deck file, 
  handling different sections, ignoring metadata, and removing counts."""
  with open(deck_file, 'r') as f:
    lines = f.readlines()
  card_names = []
  for line in lines:
    # Skip lines that are section headers or blank
    if line.startswith('[') or line.strip() == '':
      continue
    # Skip lines that don't start with a number or are likely metadata
    if not re.match(r'(\d+x?\s+)?[A-Za-z]', line):
      continue
    # Extract the card name without the count
    match = re.match(r'\d+x?\s+(.+?)( \(.+\))?\n', line)
    if match:
      card_names.append(match.group(1))
  return card_names

def download_card_image(card_name, output_dir):
  """Downloads card image(s) from Scryfall (handling double-faced cards),
  and saves them with the specified naming convention, skipping if 404."""
  try:
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={card_name}")
    response.raise_for_status()
    card_data = response.json()

    # Handle double-faced cards
    if card_data['layout'] == 'transform' or card_data['layout'] == 'modal_dfc':
      image_uris = card_data['card_faces'][0]['image_uris']  # Front face
      download_image(image_uris['normal'], card_name, output_dir)
      image_uris = card_data['card_faces'][1]['image_uris']  # Back face
      download_image(image_uris['normal'], f"{card_name} (back)", output_dir)
    else:  # Single-faced card
      download_image(card_data['image_uris']['normal'], card_name, output_dir)

  except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
      print(f"Skipping {card_name} (not found on Scryfall)")
    else:
      print(f"Error downloading {card_name}: {e}")

def download_image(image_url, card_name, output_dir):
  """Downloads a single image and saves it."""
  image_data = requests.get(image_url).content
  file_name = f"{card_name}.fullborder.jpg"
  file_path = os.path.join(output_dir, file_name)
  with open(file_path, 'wb') as f:
    f.write(image_data)
  print(f"Downloaded {file_name}")

# --- Example usage ---
deck_dir = '/Users/sun3ku/Library/Application Support/Forge/decks/commander'
output_dir = '/Users/sun3ku/Library/Caches/Forge/pics/cards/'

for filename in os.listdir(deck_dir):
  if filename.endswith('.dck'):
    deck_path = os.path.join(deck_dir, filename)
    card_names = extract_card_names(deck_path)
    for card_name in card_names:
      download_card_image(card_name, output_dir)
