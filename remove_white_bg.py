from PIL import Image

img = Image.open('products/website/assets/images/golem-logo-2.png')
img = img.convert('RGBA')
data = img.getdata()
newData = []

for item in data:
    # More aggressive white removal with lower threshold
    if item[0] > 150 and item[1] > 150 and item[2] > 150:
        # Make it transparent
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)
img.save('products/website/assets/images/golem-logo-2.png')
print("White background removed from golem-logo-2.png with aggressive threshold (150)")