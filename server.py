import pickle
import socket
import sys
import json
import math

search_type = "P"
data_type = "D"


def get_port():
    port = None
    if len(sys.argv) == 1:
        print("Por favor passe a Porta como argumento")
        exit()
    elif len(sys.argv) > 2:
        print("Muitos argumentos será assumido que a porta é o primeiro deles")
        port = sys.argv[1]
    else:
        port = sys.argv[1]
    return int(port)


def write_data(data):
    try:
        with open("data.json", "w") as datafile:
            json.dump(data, datafile)
            return "saved"
    except ValueError:
        return "error_on_saved"


def read_data():
    try:
        with open("data.json") as datafile:
            data = json.load(datafile)
            return data
    except FileNotFoundError:
        print("File not found while reading saved data, creating new file...")
        return []
    except ValueError:
        print("Decode error while reading saved data, saved data will be ignored")
        return []


def save_station(station):
    saved_data = read_data()

    if station not in saved_data:
        saved_data.append(station)
        return write_data(saved_data)
    return "already_saved"


def get_stations_of_fuel_type(type):
    stations = read_data()
    stations_of_type = filter(lambda station: station["fuelType"] == type, stations)
    return list(stations_of_type)


def get_stations_in_search_radius_of_type(longitude, latitude, radius, type):
    stations = get_stations_of_fuel_type(type)
    stations_in_search_radius = filter(
        lambda station: math.dist([longitude, latitude], [station["longitude"], station["latitude"]]) <= radius
        , stations)
    return list(stations_in_search_radius)


def get_cheaper_station_in_search_radius_of_type(longitude, latitude, radius, type):
    stations_in_search_radius = get_stations_in_search_radius_of_type(longitude, latitude, radius, type)
    if not stations_in_search_radius:
        return "0 stations in search radius"
    cheaper = min(stations_in_search_radius, key=lambda station: station["fuelPrice"])
    return cheaper


def start_server():
    server_port = get_port()
    server_ip = socket.gethostbyname(socket.gethostname())
    server_address = (server_ip, server_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)
    print(f'Server started.\nIp Address: {server_ip}\nPort: {server_port}\n')
    return server_socket


def server_loop(server_socket):
    while True:
        client_data, client_address = server_socket.recvfrom(512)
        client_message = pickle.loads(client_data)
        received_message_from_client(server_socket, client_message, client_address)


def received_message_from_client(server_socket, client_message, client_address):
    print(client_message)
    message_type = client_message["messageType"]
    if message_type == search_type:
        received_search_message(server_socket, client_message, client_address)
    elif message_type == data_type:
        received_data_message(server_socket, client_message, client_address)
    else:
        print("Unexpected message from client")


def received_search_message(server_socket, client_message, client_address):
    longitude = client_message["longitude"]
    latitude = client_message["latitude"]
    radius = client_message["searchRadius"]
    type = client_message["fuelType"]
    cheaper = get_cheaper_station_in_search_radius_of_type(longitude, latitude, radius, type)
    server_socket.sendto(pickle.dumps(cheaper), client_address)


def received_data_message(server_socket, client_message, client_address):
    station = {
        "fuelType": client_message["fuelType"],
        "fuelPrice": client_message["fuelPrice"],
        "longitude": client_message["longitude"],
        "latitude": client_message["latitude"]
    }
    message_to_client = save_station(station)

    server_socket.sendto(pickle.dumps(message_to_client), client_address)


def main():
    server_socket = start_server()
    server_loop(server_socket)


# TESTS
#
#
# received_message_from_client(None, client_mock_data, None)
# received_message_from_client(None, client_mock_search, None)
#
# client_mock_search = {
#     "messageType": "P",
#     "fuelType": 2,
#     "searchRadius": 2,
#     "latitude": 0,
#     "longitude": 0
# }
#
# client_mock_data = {
#     "messageType": "D",
#     "fuelType": 0,
#     "fuelPrice": 3299,
#     "longitude": 2,
#     "latitude": 2
# }
#
def write_mock_data():
    station1 = {
        "fuelType": 0,
        "fuelPrice": 3299,
        "longitude": 1,
        "latitude": 1
    }

    station2 = {
        "fuelType": 0,
        "fuelPrice": 2299,
        "longitude": 0,
        "latitude": 2
    }
    station3 = {
        "fuelType": 0,
        "fuelPrice": 1299,
        "longitude": 2,
        "latitude": 0
    }
    station4 = {
        "fuelType": 0,
        "fuelPrice": 3299,
        "longitude": 2,
        "latitude": 2
    }

    save_station(station1)
    save_station(station2)
    save_station(station3)
    save_station(station4)
