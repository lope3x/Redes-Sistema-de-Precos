import pickle
import socket
import sys

search_type = "P"
data_type = "D"
timeout = 4
max_tries = 1


def send_data(data):
    ip, port = get_host_and_port()
    server_address = (ip, port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)
    num_of_tries = 0

    server_data = None

    while num_of_tries < max_tries:
        try:
            client_socket.sendto(pickle.dumps(data), server_address)
            server_data, _ = client_socket.recvfrom(512)
            num_of_tries = max_tries
        except:
            num_of_tries += 1

    server_message = pickle.loads(server_data)

    if server_data is None:
        print("Error, dado não foi enviado")
        return

    if isinstance(server_message, str):
        print(server_message)
    else:
        server_message['fuelPrice'] = server_message['fuelPrice'] / 1000
        print("Mais barato: \n")
        print(server_message)


def get_host_and_port():
    if len(sys.argv) != 3:
        print("Argumentos inválidos")
        exit()
    ip = sys.argv[1]
    port = sys.argv[2]
    print(ip, port)
    return ip, int(port)


def search_option():
    fuel_type = int(input("Tipo de Combustível:"))
    search_radius = int(input("Raio de Busca:"))
    latitude = int(input("Latitude do centro de busca:"))
    longitude = int(input("longitude do centro de busca:"))

    data = {
        "messageType": "P",
        "fuelType": fuel_type,
        "searchRadius": search_radius,
        "latitude": latitude,
        "longitude": longitude
    }

    send_data(data)


def data_option():
    fuel_type = int(input("Tipo de Combustível:"))
    fuel_price = int(input("Preço do Combustível:"))
    latitude = int(input("Latitude do posto:"))
    longitude = int(input("longitude do posto:"))

    data = {
        "messageType": "D",
        "fuelType": fuel_type,
        "fuelPrice": fuel_price,
        "longitude": longitude,
        "latitude": latitude
    }

    send_data(data)


def main():
    option = input("Por favor insira o tipo da mensagem (D ou P):")

    option = option.upper()
    if option == search_type:
        search_option()
    elif option == data_type:
        data_option()
    else:
        print("Opção invalida")


main()
