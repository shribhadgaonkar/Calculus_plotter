"""
A utility for plotting mathematical functions using Matplotlib.

This module provides a function `plot_function` that allows users to easily
visualize mathematical functions over a specified domain.
"""
import matplotlib.pyplot as plt
import numpy as np

def plot_function(func, x_min, x_max, title=None, xlabel=None, ylabel=None):
  """
  Plots a given mathematical function over a specified range with customizations.

  Args:
    func (callable): A Python function that takes a single numerical argument (x)
                     and returns a numerical value (y). This is the function
                     to be plotted.
    x_min (float or int): The minimum value for the x-axis (domain start).
    x_max (float or int): The maximum value for the x-axis (domain end).
    title (str, optional): The title of the plot. Defaults to "Plot of the function"
                           if not provided.
    xlabel (str, optional): The label for the x-axis. Defaults to "x" if not provided.
    ylabel (str, optional): The label for the y-axis. Defaults to "y" if not provided.

  Raises:
    TypeError: If `func` is not a callable function.
    ValueError: If `x_min` or `x_max` cannot be converted to numbers, or if
                `x_max` is not greater than `x_min`.

  Example:
    >>> import math
    >>> def sin_func(x):
    ...   return math.sin(x)
    >>> plot_function(sin_func, 0, 2 * math.pi, title="Sine Wave", xlabel="Angle (radians)", ylabel="sin(x)")
    (This will display a plot of the sine function from 0 to 2*pi)
  """
  # Validate that func is a callable function
  if not callable(func):
    raise TypeError("The provided 'func' argument is not a callable function.")

  # Validate and convert x_min and x_max to floats
  try:
    x_min = float(x_min)
    x_max = float(x_max)
  except ValueError:
    raise ValueError("Both 'x_min' and 'x_max' must be convertible to numbers.")

  # Validate that x_max is greater than x_min
  if x_max <= x_min:
    raise ValueError("'x_max' must be greater than 'x_min'.")

  # Generate 100 evenly spaced x-values between x_min and x_max
  x_values = np.linspace(x_min, x_max, 100)
  y_values = []

  # Calculate y-values, handling potential errors during function evaluation
  for x_val in x_values:
    try:
      y_values.append(func(x_val))
    except Exception as e:
      # If func(x) raises an error, print a warning and use np.nan for that point
      print(f"Warning: Error evaluating function at x={x_val}: {e}")
      y_values.append(np.nan) # np.nan allows plotting to continue, skipping the bad point

  # Create the plot
  plt.plot(x_values, y_values)

  # Apply custom labels and title if provided, otherwise use defaults
  if xlabel:
    plt.xlabel(xlabel)
  else:
    plt.xlabel("x") # Default x-axis label

  if ylabel:
    plt.ylabel(ylabel)
  else:
    plt.ylabel("y") # Default y-axis label

  if title:
    plt.title(title)
  else:
    plt.title("Plot of the function") # Default plot title

  # Add a grid for better readability
  plt.grid(True)
  # Display the plot
  plt.show()

if __name__ == '__main__':
  # Example usage:
  def my_func(x):
    return x**2 # A simple quadratic function

  # Plot my_func from -5 to 5 with custom title and labels
  plot_function(my_func, -5, 5, title="Square Function", xlabel="Input Value", ylabel="Output Value (Squared)")

  # Example demonstrating error handling for function evaluation
  def problematic_func(x):
    if x == 0:
      raise ValueError("Division by zero!")
    return 1/x

  # This will print a warning for x=0 and plot the rest
  plot_function(problematic_func, -2, 2, title="Inverse Function with Error", xlabel="x", ylabel="1/x")
