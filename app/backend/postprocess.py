



# # open two images and make all pixels that are the same on both images black
# # (that is, remove the pixels that are the same)
# img1 = Image.open('pot2/pot_001.jpg')
# img2 = Image.open('pot2/pot_002.jpg')
# img1 = img1.convert('RGB')
# img2 = img2.convert('RGB')
# img = ImageChops.difference(img1, img2)
# img.show()
