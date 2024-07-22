'''
    The dictionary contains multiple nested dictionaries, each representing a song with various audio features.

    Each top-level key (song title) has a corresponding value that is itself a dictionary containing audio feature data. To determine the size of each value, I'll count the number of key-value pairs within each nested dictionary.

    Let's take the first song "Hold Out" as an example:

    The dictionary 'trackAnalysis' contains 18 key-value pairs:

        1. danceability
        2. energy
        3. key
        4. loudness
        5. mode
        6. speechiness
        7. acousticness
        8. instrumentalness
        9. liveness
        10. valence
        11. tempo
        12. type
        13. id
        14. uri
        15. track_href
        16. analysis_url
        17. duration_ms
        18. time_signature

    After checking the other songs in the dictionary, I can confirm that each song's nested dictionary contains the same 18 key-value pairs.

'''

def main():
    print(trackAnalysis)

    # Convert dictionary to DataFrame
    df = pd.DataFrame(trackAnalysis).T

    # List of columns to remove
    columns_to_remove = ['type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature']

    # Remove the specified columns
    df = df.drop(columns=columns_to_remove)

    df = df.apply(pd.to_numeric, errors='coerce')  # Convert to numeric, replacing non-numeric with NaN
    correlation_matrix = df.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title('Correlation Matrix of Song Features')
    plt.tight_layout()
    plt.show()

    # Calculate variance for each metric
    variances = df.var()

    # Sort variances from lowest to highest
    sorted_variances = variances.sort_values()

    print("Variances of metrics (from most similar to least similar):")
    print(sorted_variances)

    # Find the metric with the lowest variance (most similar)
    most_similar_metric = sorted_variances.index[0]
    print(f"\nThe most similar metric among the songs is: {most_similar_metric}")

    # Calculate the mean value for the most similar metric
    mean_value = df[most_similar_metric].mean()
    print(f"The mean value for {most_similar_metric} is: {mean_value:.4f}")

    # Create a box plot to visualize the distribution of each metric
    plt.figure(figsize=(12, 6))
    df.boxplot()
    plt.title('Distribution of Audio Features Across Songs')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Code to parse through and print out all of the user's saved/liked tracks
    results = sp.current_user_saved_tracks()
    parse_tracks(results)
    while results['next']: # Keep calling the API to retrieve the user's saved tracks until all tracks have been iterated
        results = sp.next(results)
        parse_tracks(results)

if __name__ == '__main__':
    main()
