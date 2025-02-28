
from page2 import flatten_tempdata

def create_test_data():
    # Mock data similar to what the API would return
    return [
        {'measurementDate': '2024-01-03', 'publishTime': '2024-01-03T16:45:00Z', 'temperature': 8.5, 'temperatureReferenceAverage': 6.0, 'temperatureReferenceHigh': 8.8, 'temperatureReferenceLow': 1.6},
        {'measurementDate': '2024-01-02', 'publishTime': '2024-01-02T16:45:00Z', 'temperature': 8.5, 'temperatureReferenceAverage': 6.0, 'temperatureReferenceHigh': 8.8, 'temperatureReferenceLow': 1.6},
        {'measurementDate': '2024-01-01', 'publishTime': '2024-01-01T16:45:00Z', 'temperature': 7.2, 'temperatureReferenceAverage': 5.9, 'temperatureReferenceHigh': 8.8, 'temperatureReferenceLow': 1.6}
    ]


def test_flatten_tempdata():
    mock_data = create_test_data()
    expected_result = [
        {'Date': '2024-01-03', 'Temperature': 8.5},
        {'Date': '2024-01-02', 'Temperature': 8.5},
        {'Date': '2024-01-01', 'Temperature': 7.2}
    ]
    
    result = flatten_tempdata(mock_data)
    
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
    print( "test_flatten_tempdata: PASSED")


def test_flatten_tempdata_failure():
    incorrect_data = [
        {'wrongKey': '2024-01-03', 'temp': 8.5},  # Wrong structure
        {'measurementDate': '2024-01-02'}  # Missing 'temperature'
    ]

    print("\nRunning test_flatten_tempdata_failure...")

    try:
        flatten_tempdata(incorrect_data)  # This should fail
        print("Test FAILED: Function did not show an error.")
    except KeyError:
        print("Test PASSED: Function shows KeyError  ")

# Run the test
test_flatten_tempdata()
test_flatten_tempdata_failure()
