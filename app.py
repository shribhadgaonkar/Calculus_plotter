"""
A Flask web application for plotting mathematical functions input by the user.

The application provides a web interface where users can enter a mathematical
function string (e.g., "x**2", "sin(x)"), a range (x_min, x_max), and optional
plot customizations. It then generates and displays the plot of the function.
"""
from flask import Flask, render_template, request, Response
import io
import base64
import numpy as np
import matplotlib
# Set Matplotlib backend to 'Agg' for server-side rendering (no GUI).
# This must be done before importing pyplot.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math # Make math functions available for eval
import os # For accessing environment variables, e.g., PORT

app = Flask(__name__)

# Define allowed global names for the eval() context.
# This is a security measure to restrict the functions and variables
# accessible within the user-provided function string.
ALLOWED_GLOBALS = {
    "np": np,       # NumPy for numerical operations if needed (e.g., np.array)
    "math": math,   # Full math module
    # Specific common math functions for convenience and clarity:
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "log": math.log,    # Natural logarithm
    "log10": math.log10, # Base-10 logarithm
    "sqrt": math.sqrt,
    "abs": abs,     # Built-in abs
    "pi": math.pi,  # Math constant pi
    "e": math.e     # Math constant e
}
# Note: Standard Python built-in functions (like len, dict, etc.) are also
# available by default in eval. The primary variable 'x' will be provided
# in the 'locals' dictionary during evaluation.

@app.route('/')
def index():
    """
    Renders the main page (`index.html`) which contains the form for
    users to input the function and plotting parameters.
    """
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_view():
    """
    Handles the POST request from the function plotting form.

    It retrieves the function string, x-range, and optional plot customizations
    from the form data. It then attempts to parse and evaluate the function string
    using a restricted `eval()` environment. If successful, it generates a plot
    using Matplotlib, saves it to a BytesIO buffer, encodes it as a base64 string,
    and passes this image data (along with other form data and any potential errors)
    back to the `index.html` template for display.

    Expected form parameters:
        - function_string (str): The mathematical function involving 'x'.
        - x_min (str): The minimum value for the x-axis.
        - x_max (str): The maximum value for the x-axis.
        - title (str, optional): The title for the plot.
        - xlabel (str, optional): The label for the x-axis.
        - ylabel (str, optional): The label for the y-axis.

    Security Note:
        This function uses `eval()` to parse the user-provided function string.
        While `eval()` is restricted by providing a specific `ALLOWED_GLOBALS`
        dictionary, using `eval()` with arbitrary user input is inherently risky
        and should be replaced with a safer parsing mechanism (e.g., an AST
        parser or a dedicated math parsing library) in a production environment.

    Returns:
        Renders the `index.html` template with context variables including:
        - img_base64 (str, optional): The base64 encoded PNG image of the plot.
        - error (str, optional): An error message if any issue occurred.
        - form_data (dict): The original form data to repopulate the form.
        - plot_title (str, optional): The title used for the plot.
        - function_string_rendered (str, optional): The function string that was plotted.
    """
    form_data = request.form
    function_string = form_data.get('function_string')
    x_min_str = form_data.get('x_min')
    x_max_str = form_data.get('x_max')
    title = form_data.get('title', 'Plot of the function')
    xlabel = form_data.get('xlabel', 'x')
    ylabel = form_data.get('ylabel', 'y')

    if not function_string:
        return render_template('index.html', error="The function string f(x) cannot be empty. Please enter a function.", form_data=form_data)
    if not x_min_str or not x_max_str:
        return render_template('index.html', error="Both x_min and x_max must be provided. Please enter numerical values for the range.", form_data=form_data)

    try:
        x_min = float(x_min_str)
        x_max = float(x_max_str)
    except ValueError:
        return render_template('index.html', error="x_min and x_max must be valid numbers. Please ensure they are in a format like '3.14' or '-5'.", form_data=form_data)

    if x_max <= x_min:
        return render_template('index.html', error="x_max must be strictly greater than x_min. Please adjust the range.", form_data=form_data)

    # IMPORTANT: Using eval with user input is inherently risky.
    # For a production application, a more secure parsing method (e.g., Abstract Syntax Tree parsing
    # with a whitelist of allowed nodes, or a dedicated math parsing library) should be used.
    # This implementation assumes 'x' will be provided in the locals dict for eval.
    try:
        # Test if the function string can be evaluated at a sample point (e.g., x=1).
        # This helps catch syntax errors or disallowed names before generating many plot points.
        # The locals dict for eval must contain 'x' for the function to use it.
        # SECURITY WARNING: eval() is dangerous with untrusted input.
        # This is a demonstration and should be replaced with a safer parser in production.
        eval(function_string, ALLOWED_GLOBALS, {'x': 1}) # Test with a dummy value for x
        func_to_plot = lambda x_val: eval(function_string, ALLOWED_GLOBALS, {'x': x_val})
    except SyntaxError:
        # Handle syntax errors in the user's function string.
        return render_template('index.html', error="Syntax error in function string. Please check for typos or incorrect mathematical syntax (e.g., 'x^2' should be 'x**2').", form_data=form_data)
    except NameError as e:
        # Handle cases where the user tries to use undefined/disallowed names.
        undefined_name = str(e).split("'")[1] if "'" in str(e) else "an unknown function or variable"
        return render_template('index.html', error=f"Error in function string: The name '{undefined_name}' is not allowed or not defined. Please use common functions like sin, cos, exp, log, sqrt, or basic arithmetic. Check for typos.", form_data=form_data)
    except Exception as e:
        # Catch-all for other unexpected errors during function parsing/evaluation.
        return render_template('index.html', error=f"An unexpected error occurred while parsing the function: {e}. Please review your function string.", form_data=form_data)

    # Generate x values for the plot.
    x_values = np.linspace(x_min, x_max, 200) # Use 200 points for a smoother curve.
    y_values = []

    # Calculate y values, handling errors for individual points.
    for x_val in x_values:
        try:
            y_val = func_to_plot(x_val)
            # Ensure y_val is a real number or NaN, not complex, as Matplotlib might struggle
            # with complex numbers directly in some plots or require specific handling.
            if isinstance(y_val, complex):
                y_values.append(np.nan) # Represent complex results or unplottable points as NaN.
            else:
                y_values.append(y_val)
        except Exception:
            # If an error occurs for a specific x_val (e.g., log(0), 1/0),
            # append np.nan to allow the plot to continue for other points.
            y_values.append(np.nan)

    img_base64 = None
    try:
        # Plotting with Matplotlib
        fig = plt.figure(figsize=(8, 6)) # Create a new figure for each plot.
        plt.plot(x_values, y_values)

        # Set plot title and labels, using defaults if not provided by the user.
        plt.title(title if title else "Plot of the function")
        plt.xlabel(xlabel if xlabel else "x")
        plt.ylabel(ylabel if ylabel else "y")
        plt.grid(True) # Add a grid for better readability.

        # Save the plot to a BytesIO buffer instead of a file.
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png') # Save as PNG format.
        plt.close(fig) # Close the figure to free up memory, crucial in web apps.

        # Encode the image buffer to a base64 string for embedding in HTML.
        img_buffer.seek(0) # Rewind the buffer to the beginning.
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        img_buffer.close() # Close the buffer.
    except Exception as e:
        # Catch any errors that occur during the plot generation or saving process.
        return render_template('index.html', error=f"An unexpected error occurred while generating the plot: {e}. Please try again or adjust inputs.", form_data=form_data)

    # Render the template, passing the base64 image and other relevant data.
    return render_template('index.html',
                           img_base64=img_base64,
                           form_data=form_data,
                           plot_title=title, # Pass title for display above plot
                           function_string_rendered=function_string # Pass func string for display
                           )

if __name__ == '__main__':
    # Determine port from environment variable or default to 5000.
    # Bind to '0.0.0.0' to make the app accessible from outside the Docker container.
    port = int(os.environ.get('PORT', 5000))
    # debug=True is useful for development but should generally be False in production.
    app.run(host='0.0.0.0', port=port, debug=True)
