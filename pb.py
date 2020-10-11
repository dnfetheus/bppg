import random
import math
import sys
from functools import reduce


def code_packet(original_packet: list, height: int, width: int) -> list:
    # inicialização com 0 da matriz que receberá uma parte dos bits do pacote por iteração
    parity_matrix = [[0 for _ in range(width)] for _ in range(height)]
    # tamanho dos bits de dados por parte
    data_bits_len = height * width
    # tamanho dos bits de dados + bits de paridade de coluna por parte
    data_bits_with_column_len = data_bits_len + width
    # tamanho em bits total
    coded_bits_len = data_bits_with_column_len + height
    # tamanho estimado do pacote codificado
    coded_len = len(original_packet) + ((height + width) * (len(original_packet) / data_bits_len))
    # inicialização com 0 do pacote codigicado
    coded_packet = [0 for _ in range(int(coded_len))]

    # iteração no pacote por partes de dados da paridade
    for i in range(int(len(original_packet) / data_bits_len)):
        # preenchimento da matriz de dados
        for j in range(height):
            for k in range(width):
                parity_matrix[j][k] = original_packet[i * data_bits_len + width * j + k]

        # preenchimento da parte de dados do pacote codificado
        for j in range(data_bits_len):
            coded_packet[i * coded_bits_len + j] = original_packet[i * data_bits_len + j]

        # adição de bits de paridade de coluna
        for j in range(width):
            amt = 0

            for k in range(height):
                amt = amt + parity_matrix[k][j]

            if amt % 2 == 0:
                coded_packet[i * coded_bits_len + data_bits_len + j] = 0
            else:
                coded_packet[i * coded_bits_len + data_bits_len + j] = 1

        # adição de bits de paridade de linha
        for j in range(height):
            amt = reduce(lambda x, y: x + y, parity_matrix[j])

            if amt % 2 == 0:
                coded_packet[i * coded_bits_len + data_bits_with_column_len + j] = 0
            else:
                coded_packet[i * coded_bits_len + data_bits_with_column_len + j] = 1

    return coded_packet


def decode_packet(transmitted_packet: list, height: int, width: int) -> list:
    parity_matrix = [[0 for _ in range(width)] for _ in range(height)]
    data_bits_len = height * width
    data_bits_with_column_len = data_bits_len + width
    coded_bits_len = data_bits_with_column_len + height
    parity_columns = [0 for _ in range(width)]
    parity_rows = [0 for _ in range(height)]
    decoded_packet = [0 for _ in range(len(transmitted_packet))]

    n = 0

    # iteração do pacote transmitido por bits codificados
    for i in range(0, len(transmitted_packet), coded_bits_len):
        # preenchimento da matriz de dados
        for j in range(height):
            for k in range(width):
                parity_matrix[j][k] = transmitted_packet[i + width * j + k]

        # preenchimento do array de bits de paridade de coluna
        for j in range(width):
            parity_columns[j] = transmitted_packet[i + data_bits_len + j]

        # preenchimento do array de bits de paridade de linha
        for j in range(height):
            parity_rows[j] = transmitted_packet[i + data_bits_with_column_len + j]

        error_in_column = -1

        # verificação de erro em colunas
        for j in range(width):
            amt = 0

            for k in range(height):
                amt = amt + parity_matrix[k][j]

            if amt % 2 != parity_columns[j]:
                error_in_column = j
                break

        error_in_row = -1

        # verificação de erro em linhas
        for j in range(height):
            amt = reduce(lambda x, y: x + y, parity_matrix[j])

            if amt % 2 != parity_rows[j]:
                error_in_row = j
                break

        # correção de erro
        if error_in_row > -1 and error_in_column > -1:
            if parity_matrix[error_in_row][error_in_column] == 1:
                parity_matrix[error_in_row][error_in_column] = 0
            else:
                parity_matrix[error_in_row][error_in_column] = 1

        # passagem de dados da matriz pro pacote decodificado
        for j in range(height):
            for k in range(width):
                decoded_packet[data_bits_len * n + width * j + k] = parity_matrix[j][k]

        n = n + 1

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
    sys.stderr.write("\t" + self_name + " <tam_pacote> <reps> <prob. erro> <comprimento> <altura>\n\n")
    sys.stderr.write("Onde:\n")
    sys.stderr.write("\t- <tam_pacote>: tamanho do pacote usado nas simulacoes (em bytes).\n")
    sys.stderr.write("\t- <reps>: numero de repeticoes da simulacao.\n")
    sys.stderr.write("\t- <prob. erro>: probabilidade de erro de bits (i.e., probabilidade\n")
    sys.stderr.write("de que um dado bit tenha seu valor alterado pelo canal.)\n")
    sys.stderr.write("\t- <altura>: altura da matriz de paridade\n")
    sys.stderr.write("\t- <comprimento>: comprimento da matriz de paridade\n\n")

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
    height = int(sys.argv[4])
    width = int(sys.argv[5])

    if packet_length <= 0 or reps <= 0 or error_prob < 0 or error_prob > 1 or height <= 0 or width <= 0:
        print_help(sys.argv[0])

    random.seed()

    original_packet = generate_random_packet(packet_length)
    coded_packet = code_packet(original_packet, height, width)

    for i in range(reps):
        inserted_error_count, transmitted_packet = insert_errors(coded_packet, error_prob)
        total_inserted_error_count = total_inserted_error_count + inserted_error_count

        decoded_packet = decode_packet(transmitted_packet, height, width)
        bit_error_count = count_errors(original_packet, decoded_packet)

        if bit_error_count > 0:
            total_bit_error_count = total_bit_error_count + bit_error_count
            total_packet_error_count = total_packet_error_count + 1

    print('Numero de transmissoes simuladas: {0:d}\n'.format(reps))
    print('Numero de bits transmitidos: {0:d}'.format(reps * packet_length * 8))
    print('Numero de bits errados inseridos: {0:d}\n'.format(total_inserted_error_count))
    print('Taxa de erro de bits (antes da decodificacao): {0:.2f}%'.format(float(total_inserted_error_count) / float(reps * len(coded_packet)) * 100.0))
    print('Numero de bits corrompidos apos decodificacao: {0:d}'.format(total_bit_error_count))
    print('Taxa de erro de bits (apos decodificacao): {0:.2f}%\n'.format(float(total_bit_error_count) / float(reps * packet_length * 8) * 100.0))
    print('Numero de pacotes corrompidos: {0:d}'.format(total_packet_error_count))
    print('Taxa de erro de pacotes: {0:.2f}%'.format(float(total_packet_error_count) / float(reps) * 100.0))


if __name__ == '__main__':
    main()
