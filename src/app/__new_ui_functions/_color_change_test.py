import re
import matplotlib.pyplot as plt
from webcolors import hex_to_rgb

# Path to your QSS file
qss_file_path = "/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/Modern_GUI_PyDracula_PySide6_or_PyQt6/themes/py_dracula_light.qss"


# Function to convert hex to RGB tuple (R, G, B)
def hex_to_rgb_tuple(hex_code):
    rgb = hex_to_rgb(hex_code)
    return f"rgb({rgb.red}, {rgb.green}, {rgb.blue})"


# Read and parse the QSS file
def process_qss_file(qss_file_path):
    with open(qss_file_path, "r") as f:
        qss_content = f.read()

    # Regex for RGB colors in the format rgb(R, G, B)
    rgb_pattern = r'rgb\((\d+),\s*(\d+),\s*(\d+)\)'
    # Regex for hex color codes in the format #RRGGBB
    hex_pattern = r'#[0-9A-Fa-f]{6}'

    # Find all RGB and Hex color codes
    rgb_matches = re.findall(rgb_pattern, qss_content)
    hex_matches = re.findall(hex_pattern, qss_content)

    # Convert hex matches to RGB format
    hex_colors_as_rgb = [hex_to_rgb_tuple(hex_code) for hex_code in hex_matches]

    # Combine RGB codes and converted hex colors, remove duplicates by converting to a set
    all_colors = list(set([f"rgb({r}, {g}, {b})" for r, g, b in rgb_matches] + hex_colors_as_rgb))

    return all_colors


# Function to plot color swatches in groups of 5 with RGB labels on top
def plot_color_swatches_in_groups(colors, group_size=5):
    # Split colors into groups
    for i in range(0, len(colors), group_size):
        group = colors[i:i + group_size]

        fig, ax = plt.subplots(figsize=(6, len(group)))  # Adjust figure size based on the number of colors in the group
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(group))

        # Hide axes
        ax.set_xticks([])
        ax.set_yticks([])

        # Create a color swatch for each color in the group
        for j, color in enumerate(group):
            # Extract the RGB values from the color label (rgb(R, G, B))
            rgb_values = tuple(map(int, re.findall(r'\d+', color)))
            rect = plt.Rectangle((0, j), 10, 1, color=[x / 255.0 for x in rgb_values])
            ax.add_patch(rect)
            # Move the label on top of the color bar, centered
            ax.text(5, j + 0.5, color, va='center', ha='center', color='black', fontsize=10)

        plt.show()


if __name__ == "__main__":
    # Extract colors from the QSS file
    colors = process_qss_file(qss_file_path)

    # Plot the color swatches in groups of 5
    plot_color_swatches_in_groups(colors, group_size=5)