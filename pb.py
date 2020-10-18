import random
import math
import sys
from functools import reduce


def code_packet(original_packet: list, rows: int, cols: int) -> list:
    data_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    block_data_len = rows * cols
    block_without_rows_len = block_data_len + cols
    block_len = block_without_rows_len + rows
    coded_packet_len = len(original_packet) * (1 + ((rows + cols) / block_data_len))
    coded_packet = [0 for _ in range(int(coded_packet_len))]

    for i in range(int(len(original_packet) / block_data_len)):
        for j in range(rows):
            for k in range(cols):
                data_matrix[j][k] = original_packet[i * block_data_len + cols * j + k]

        for j in range(block_data_len):
            coded_packet[i * block_len + j] = original_packet[i * block_data_len + j]

        for j in range(cols):
            amt = reduce(lambda x, y: x + y, [data_matrix[k][j] for k in range(rows)])
            coded_packet[i * block_len + block_data_len + j] = amt % 2

        for j in range(rows):
            amt = reduce(lambda x, y: x + y, data_matrix[j])
            coded_packet[i * block_len + block_without_rows_len + j] = amt % 2

    return coded_packet


def decode_packet(transmitted_packet: list, rows: int, cols: int) -> list:
    data_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    block_data_len = rows * cols
    block_without_rows_len = block_data_len + cols
    block_len = block_without_rows_len + rows
    parity_columns = [0 for _ in range(cols)]
    parity_rows = [0 for _ in range(rows)]
    decoded_packet = [0 for _ in range(len(transmitted_packet))]

    for i in range(0, len(transmitted_packet), block_len):
        block_index = int(i / block_len)

        for j in range(rows):
            for k in range(cols):
                data_matrix[j][k] = transmitted_packet[i + cols * j + k]

        for j in range(cols):
            parity_columns[j] = transmitted_packet[i + block_data_len + j]

        for j in range(rows):
            parity_rows[j] = transmitted_packet[i + block_without_rows_len + j]

        wrong_column_index = -1

        for j in range(cols):
            amt = reduce(lambda x, y: x + y, [data_matrix[k][j] for k in range(rows)])

            if amt % 2 != parity_columns[j]:
                wrong_column_index = j
                break

        wrong_row_index = -1

        for j in range(rows):
            amt = reduce(lambda x, y: x + y, data_matrix[j])

            if amt % 2 != parity_rows[j]:
                wrong_row_index = j
                break

        if wrong_row_index > -1 and wrong_column_index > -1:
            data_matrix[wrong_row_index][wrong_column_index] = int(not data_matrix[wrong_row_index][wrong_column_index])

        for j in range(rows):
            for k in range(cols):
                decoded_packet[block_data_len * block_index + cols * j + k] = data_matrix[j][k]

    return decoded_packet


def generate_random_packet(length: int) -> list:
    return [random.randint(0, 1) for _ in range(8 * length)]


def geom_rand(p: float) -> int:
    u_rand = 0

    while u_rand == 0:
        u_rand = random.uniform(0, 1)

    return int(math.log(u_rand) / math.log(1 - p))


def insert_errors(coded_packet: list, error_prob: float) -> tuple:
    i = -1
    n = 0

    transmitted_packet = list(coded_packet)

    while 1:
        r = geom_rand(error_prob)
        i = i + 1 + r

        if i >= len(transmitted_packet):
            break

        if transmitted_packet[i] == 1:
            transmitted_packet[i] = 0
        else:
            transmitted_packet[i] = 1

        n = n + 1

    return n, transmitted_packet


def count_errors(original_packet: list, decoded_packet: list) -> int:
    errors = 0

    for i in range(len(original_packet)):
        if original_packet[i] != decoded_packet[i]:
            errors = errors + 1

    return errors


def print_help(self_name: str) -> None:
    sys.stderr.write("Simulador de metodos de FEC/codificacao.\n\n")
    sys.stderr.write("Modo de uso:\n\n")
    sys.stderr.write("\t" + self_name + " <tam_pacote> <reps> <prob. erro> <linhas> <colunas>\n\n")
    sys.stderr.write("Onde:\n")
    sys.stderr.write("\t- <tam_pacote>: tamanho do pacote usado nas simulacoes (em bytes).\n")
    sys.stderr.write("\t- <reps>: numero de repeticoes da simulacao.\n")
    sys.stderr.write("\t- <prob. erro>: probabilidade de erro de bits (i.e., probabilidade\n")
    sys.stderr.write("de que um dado bit tenha seu valor alterado pelo canal.)\n")
    sys.stderr.write("\t- <linhas>: número de linhas da matriz de dados\n")
    sys.stderr.write("\t- <colunas>: número de colunas da matriz de dados\n\n")

    sys.exit(1)


def main() -> None:
    total_bit_error_count = 0
    total_packet_error_count = 0
    total_inserted_error_count = 0

    if len(sys.argv) != 6:
        print_help(sys.argv[0])

    packet_length = int(sys.argv[1])
    reps = int(sys.argv[2])
    error_prob = float(sys.argv[3])
    rows = int(sys.argv[4])
    cols = int(sys.argv[5])

    if packet_length <= 0 or reps <= 0 or error_prob < 0 or error_prob > 1 or rows <= 0 or cols <= 0:
        print_help(sys.argv[0])

    random.seed()

    original_packet = generate_random_packet(packet_length)
    coded_packet = code_packet(original_packet, rows, cols)

    for i in range(reps):
        inserted_error_count, transmitted_packet = insert_errors(coded_packet, error_prob)
        total_inserted_error_count = total_inserted_error_count + inserted_error_count

        decoded_packet = decode_packet(transmitted_packet, rows, cols)
        bit_error_count = count_errors(original_packet, decoded_packet)

        if bit_error_count > 0:
            total_bit_error_count = total_bit_error_count + bit_error_count
            total_packet_error_count = total_packet_error_count + 1

    print('Numero de transmissoes simuladas: {0:d}\n'.format(reps))
    print('Numero de bits transmitidos: {0:d}'.format(reps * len(coded_packet)))
    print('Numero de bits errados inseridos: {0:d}\n'.format(total_inserted_error_count))
    print('Taxa de erro de bits (antes da decodificacao): {0:.2f}%'.format(float(total_inserted_error_count) / float(reps * len(coded_packet)) * 100.0))
    print('Numero de bits corrompidos apos decodificacao: {0:d}'.format(total_bit_error_count))
    print('Taxa de erro de bits (apos decodificacao): {0:.2f}%\n'.format(float(total_bit_error_count) / float(reps * packet_length * 8) * 100.0))
    print('Numero de pacotes corrompidos: {0:d}'.format(total_packet_error_count))
    print('Taxa de erro de pacotes: {0:.2f}%'.format(float(total_packet_error_count) / float(reps) * 100.0))


if __name__ == '__main__':
    main()
