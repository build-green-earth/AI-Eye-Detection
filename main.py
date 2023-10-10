import cv2
import numpy as np
from tkinter import Tk, filedialog

# Global variables
clicked = False
center = (-1, -1)

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global clicked, center
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = True
        center = (x, y)

# Create a Tkinter root window
root = Tk()
root.withdraw()

# Open a file dialog to select multiple images
file_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tif")])

# Initialize a list to store the processed images
processed_images = []

def remove_flash(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding to segment the bright regions
    _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

    # Find contours of the bright regions
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours based on area in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Iterate through the contours and remove the flash
    for contour in contours:
        # Fit an ellipse to the contour
        ellipse = cv2.fitEllipse(contour)

        # Check if the ellipse is within a certain aspect ratio range
        aspect_ratio = ellipse[1][0] / ellipse[1][1]
        if 0.5 <= aspect_ratio <= 2:
            # Generate a mask for the current contour
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

            # Inpaint the flash region using the mask
            image = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
            break

    return image


# Process each selected image
for file_path in file_paths:
    # Read the image from disk
    image = cv2.imread(file_path)
    image = cv2.resize(image, (2100, 1500))

    # Check if image was successfully read
    if image is not None:
        # Create a window and bind the mouse callback function
        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", mouse_callback)

        while True:
            # Display the image
            cv2.imshow("Image", image.copy())

            # Check for a click
            if clicked:
                center_x = int(center[0] * 1920 / 900)
                center_y = int(center[1] * 1920 / 900)

                center = [center_x, center_y]

                print(center_x, center_y)

                image = cv2.resize(image, (4480, 3200))

                # Draw circles with radii 45 and 150 in red
                small_circle_mask = np.zeros_like(image)
                large_circle_mask = np.zeros_like(image)

                # center = [300, 300]

                cv2.circle(small_circle_mask, center, 330, (255, 255, 255), -1)
                cv2.circle(large_circle_mask, center, 960, (255, 255, 255), -1)

                new_color = (0, 0, 0)
                image = cv2.bitwise_and(image, cv2.bitwise_not(small_circle_mask))
                image = cv2.add(image, cv2.bitwise_and(small_circle_mask, new_color))

                image = cv2.bitwise_and(image, large_circle_mask)

                center_x = center_x - 960
                center_y = center_y - 960

                image = image[center_y:center_y + 1920, center_x:center_x + 1920]

                # Store the processed image in the list
                processed_images.append(image)

                # Reset the clicked flag and center coordinates
                clicked = False
                center = (-1, -1)

            # Check for key press
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

        # Close the window
        cv2.destroyAllWindows()
    else:
        print(f"Failed to read the image file: {file_path}")

# Check if any images were processed
if len(processed_images) > 0:
    # Calculate the average image
    average_image = np.mean(processed_images, axis=0).astype(np.uint8)

    average_image = remove_flash(average_image)

    # x = 230
    # y = 500
    # width = 150
    # height = 150 
    # addImage = cv2.imread('output1.png')
    # roi = addImage[y:y+height, x:x+width]

    # roi1 = average_image[y:y+height, x:x+width]
    # result = cv2.addWeighted(roi, 0.5, roi1, 0.5, 0)
    # average_image[y:y+height, x:x+width] = result
    cv2.imwrite('output.png', average_image)

    # Display the average image
    cv2.imshow("Average Image", average_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No images were processed.")