import cv2
import numpy as np

class BlurTechniques:
    def __init__(self):
        """
        Initialize blur techniques with default parameters.
        """
        # Default parameters
        self.gaussian_kernel_size = (21, 21)
        self.pixelate_block_size = 15
        self.edge_preserving_diameter = 15
    
    def gaussian_blur(self, image, kernel_size=None):
        """
        Apply Gaussian blur to an image.
        
        Args:
            image: Input image
            kernel_size: Size of the Gaussian kernel (optional)
            
        Returns:
            Blurred image
        """
        if kernel_size is None:
            kernel_size = self.gaussian_kernel_size
        
        # Make sure the image is valid
        if image is None or image.size == 0:
            return image
        
        try:
            return cv2.GaussianBlur(image, kernel_size, 0)
        except Exception as e:
            print(f"Error applying Gaussian blur: {e}")
            return image
    
    def pixelate(self, image, block_size=None):
        """
        Apply pixelation effect to an image.
        
        Args:
            image: Input image
            block_size: Size of pixelation blocks (optional)
            
        Returns:
            Pixelated image
        """
        if block_size is None:
            block_size = self.pixelate_block_size
        
        # Make sure the image is valid
        if image is None or image.size == 0:
            return image
        
        try:
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Calculate new dimensions
            new_height = max(1, height // block_size)
            new_width = max(1, width // block_size)
            
            # Resize down
            temp = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # Resize back up
            return cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)
        except Exception as e:
            print(f"Error applying pixelation: {e}")
            return image
    
    def edge_preserving_blur(self, image, diameter=None):
        """
        Apply edge-preserving blur to an image.
        
        Args:
            image: Input image
            diameter: Filter diameter (optional)
            
        Returns:
            Blurred image with preserved edges
        """
        if diameter is None:
            diameter = self.edge_preserving_diameter
        
        # Make sure the image is valid
        if image is None or image.size == 0:
            return image
        
        try:
            return cv2.edgePreservingFilter(
                image, 
                flags=cv2.NORMCONV_FILTER,
                sigma_s=diameter,
                sigma_r=0.1
            )
        except Exception as e:
            print(f"Error applying edge-preserving blur: {e}")
            # Fallback to bilateral filter which also preserves edges
            try:
                return cv2.bilateralFilter(image, diameter, 75, 75)
            except Exception as e:
                print(f"Error applying bilateral filter: {e}")
                return image
    
    def set_gaussian_kernel_size(self, size):
        """Set the Gaussian blur kernel size."""
        self.gaussian_kernel_size = size
    
    def set_pixelate_block_size(self, size):
        """Set the pixelation block size."""
        self.pixelate_block_size = size
    
    def set_edge_preserving_diameter(self, diameter):
        """Set the edge-preserving filter diameter."""
        self.edge_preserving_diameter = diameter
