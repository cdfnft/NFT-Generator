from dataclasses import dataclass
from shutil import rmtree
from os import path, mkdir
from PIL import Image 
import random
import csv

# Change these
COLLECTION_NAME = "Duck Friends"
COLLECTION_DESCRIPTION = "1000 PFP collections by Chia for Chia."
TOTAL_IMAGES = 997 # Number of random unique images you want to generate

all_images = [] # This is used to store the images as they are generated
OUTPUT_DIR = f'./collection'

# Each image is made up a series of traits
@dataclass
class Trait:
    name: str
    variants: list[str]
    weights: list[int]

# Each image is made up a series of traits
# Make sure these traits match your component file names
# e.g., 'Pink' for Pink.png
# The weightings for each trait drive the rarity and add up to 100%
# Note traits in this list must be in order of Layer. I.e., Background first, Foreground last.
traits = [
    Trait(
        "Background", 
        ["Green", "Orange", "Purple", "Red", "White", "Yellow"],
        [20, 20, 20, 20, 10, 10]), # 30% + 20% + 10% + 40% = 100%
    Trait(
        "Base", 
        ["Blue Body", "Green Body", "White Body", "Yellow Body"], 
        [25, 25, 10, 40]),
    Trait(
        "Eye", 
        ["3D Glasses", "Black Eye", "Blue Eye", "Blue Rimmed Glasses", "Blue Shutter Glasses", "Darkness Clan Visor Pink", "Darkness Clan Visor Purple", "Fire", "Gold", "Green Eye", "Love", "Pink Eye", "Pink Shutter Glasses", "Purple Angry", "Purple Rimmed Glasses", "Rainbow", "Red Eye", "Relaxed Blue", "Relaxed Gold", "Relaxed Green", "Side Robot Laser", "Side Robot", "Sunglasses", "Visor Gold", "Visor Red"], 
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
    Trait(
        "Hat", 
        ["Army Bucket", "Backwards Blue", "Backwards Red", "Backwards XCH", "Beanie Orange", "Beanie Red", "Bow", "Chia Coin", "Cowboy", "Crown", "Green Mohawks", "Halo", "Headband", "Headphone", "Leaf", "Lincoln Red", "Lincoln", "None Hat", "Pink Mohawks", "Purple Mohawks", "Rice Hat", "Skull", "Viking Helmet", "Witch Hat"], 
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4]),
    Trait(
        "Cloth", 
        ["Army", "Black Hoodie", "Black Shirt", "Blue Sport", "Blue Tank Top", "Blue Tshirt", "Business Shirt Blue", "Business Shirt Red", "Cowboy Jacket", "Cyberpunk Jacket", "Jean Jacket", "Joker","None Cloth","Pink Shirt","Purple Shirt","Red Scarf", "Red Sport", "Shirt Stripes Blue", "Shirt Stripes Green","Sweater Wave","White Tank Top"], 
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 20, 4, 4, 4, 4, 4, 4, 4, 4]),
]

## For a Simple project you should only need to change values above this line

## Generate Traits
# A recursive function to generate unique image combinations
def create_new_image():
    new_image = {}
    
    # For each trait category, select a random trait based on the weightings
    for trait in traits:
        new_image[trait.name] = random.choices(trait.variants, trait.weights)[0]
    
    if (new_image in all_images):
        return create_new_image()
    else:
        return new_image



## Helper function for generating progress bars    
# Print iterations progress
def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '#', printEnd = "\r"):
    total = len(iterable)
    
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        
    # Initial Call
    printProgressBar(0)
    
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
        
    # Print New Line on Complete
    print()



# Generate the unique combinations based on trait weightings
for i in progressBar(range(TOTAL_IMAGES), prefix = 'Combining Images:', suffix = 'Complete', length = 32):
    new_trait_image = create_new_image()
    all_images.append(new_trait_image)
    
    
    
## Check the stats of the new images
# Returns true if all images are unique
def all_images_unique(all_images):
    seen = list()
    return not any(i in seen or seen.append(i) for i in all_images)

print("Are all images unique? %s" % (all_images_unique(all_images)))


#### Generate Images and Metadata 
# Add the file, name and description for each image
for i in range(TOTAL_IMAGES):
    # File metadata to suit MintGarden Bulk Generator
    # Feel free to change the values, do not change the keys.
    file_data = {
        "file": "%s.png" % (str(i + 1)),                        
        "name": "%s #%s" % (COLLECTION_NAME, str(i + 1)),         
        "description": (COLLECTION_DESCRIPTION)  
    }
    file_data.update(all_images[i])
    all_images[i] = file_data


# Note: Will delete existing files in Output Directory
# This is a feature, for quick re-generation
if path.isdir(OUTPUT_DIR):
    rmtree(OUTPUT_DIR)
mkdir(OUTPUT_DIR)


# Create the metadata.csv file ready for the MintGarden Bulk minter
metadata_file = open("./collection/metadata.csv", 'w', newline='')
writer = csv.writer(metadata_file, delimiter =';')

# Write the metadata headers
writer.writerow(all_images[0].keys())

# Create the .png files
for image in progressBar(all_images, prefix = 'Assembling Images & Metadata:', suffix = 'Complete', length = 20):
    layers = []

    # Load each of the Images Layers
    for trait in traits:
        layers.append(Image.open(f'./components/{image[trait.name]}.png').convert('RGBA'))

    # Create the composite
    composite = Image.alpha_composite(layers[0], layers[1])
    for next_layer in layers[2:]:
        composite = Image.alpha_composite(composite, next_layer)

    #Convert to RGB
    rgb_im = composite.convert('RGB')
    rgb_im.save(OUTPUT_DIR + "/" + image["file"])

    # Write the metadata for this item to metadata.csv
    writer.writerow(image.values())

metadata_file.close()

print("Successfully Assembled.\n")