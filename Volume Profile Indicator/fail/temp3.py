import pandas as pd
import matplotlib.pyplot as plt

# Sample data
data_dict = {
    'datetime': [
        '2024-07-01 09:00:00', '2024-07-01 09:05:00', '2024-07-01 09:10:00',
        '2024-07-01 09:15:00', '2024-07-01 09:20:00', '2024-07-01 09:25:00'
    ],
    'price': [100, 101, 100, 102, 100, 101],
    'volume': [500, 600, 700, 800, 650, 620]
}

def load_data():
    """
    Load sample trade data.
    """
    data = pd.DataFrame(data_dict)
    data['datetime'] = pd.to_datetime(data['datetime'])
    return data

def calculate_volume_profile(data):
    """
    Calculate the volume profile for the entire dataset.

    Parameters:
    data (pd.DataFrame): The trade data containing 'datetime', 'price', and 'volume'.

    Returns:
    pd.DataFrame: A DataFrame with 'price' and 'volume' columns.
    """
    volume_profile = data.groupby('price')['volume'].sum().reset_index()
    return volume_profile

def plot_volume_profile(volume_profile):
    """
    Plot the volume profile.

    Parameters:
    volume_profile (pd.DataFrame): The volume profile data with 'price' and 'volume' columns.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(volume_profile['price'], volume_profile['volume'], color='blue', edgecolor='black')
    ax.set_xlabel('Volume')
    ax.set_ylabel('Price')
    ax.set_title('Volume Profile')
    plt.show()

if __name__ == "__main__":
    data = load_data()
    data.set_index('datetime', inplace=True)
    volume_profile = calculate_volume_profile(data)
    plot_volume_profile(volume_profile)
