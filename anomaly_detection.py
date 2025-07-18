import numpy as np
from sklearn.cluster import KMeans

def detect_anomalies_kmeans(adherence_histories, n_clusters=2, threshold=1.5):
    """
    Detect anomalies in adherence histories using K-Means clustering.
    adherence_histories: list of lists/arrays (each patient's adherence history)
    Returns: list of bools (True if anomalous)
    """
    X = np.array(adherence_histories)
    if len(X) < n_clusters:
        # Not enough samples for clustering; return all False (no anomalies)
        return [False] * len(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    distances = np.linalg.norm(X - centers[labels], axis=1)
    median_dist = np.median(distances)
    anomalies = distances > (threshold * median_dist)
    return anomalies.tolist()

# Example usage:
if __name__ == "__main__":
    histories = [
        [1,1,1,1,1,1,1],
        [1,0,1,1,0,1,1],
        [0,0,0,0,0,0,0],
        [1,1,1,0,1,1,0],
        [1,1,1,1,1,1,0],
        [0,1,0,1,0,1,0],
    ]
    anomalies = detect_anomalies_kmeans(histories)
    print("Anomalies:", anomalies) 