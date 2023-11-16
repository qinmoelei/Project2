from pyfinite import ffield
import numpy as np

F = ffield.FField(8)
g_0 = int("02", 16)


def gp_pow(base, exponent):
    result = base
    for i in range(1, exponent):
        result = F.Multiply(result, base)
    return result


# encoder/recover P
def calculate_P(data_chunks):
    # data_chunks 是两重list，[[01,02,03],[02,03,01],[03,01,02],....]
    chunk_length = len(data_chunks[0])
    parity_chunk_p = [int("00", 16)] * chunk_length
    for i, chunk in enumerate(range(chunk_length)):
        for j in range(len(data_chunks)):
            parity_chunk_p[i] = F.Add(parity_chunk_p[i], data_chunks[j][i])
    return parity_chunk_p


# encoder/recover Q
def calculate_Q(data_chunks):
    chunk_length = len(data_chunks[0])
    parity_chunk_Q = [int("00", 16)] * chunk_length
    g_0 = int("02", 16)
    for i, chunk in enumerate(range(chunk_length)):
        for j in range(len(data_chunks)):
            parity_chunk_Q[i] = F.Add(
                parity_chunk_Q[i], F.Multiply(data_chunks[j][i], gp_pow(g_0, j))
            )
    return parity_chunk_Q


# recover one data
def recover_one_data(data_chunks, parity_chunk_p, missing_index):
    chunk_length = len(data_chunks[0])
    data_chunks[missing_index] = [int("00", 16)] * chunk_length
    preserve_P = calculate_P(data_chunks)

    data = [int("00", 16)] * chunk_length
    for i in range(chunk_length):
        data[i] = F.Subtract(parity_chunk_p[i], preserve_P[i])
    data_chunks[missing_index] = data
    return data_chunks


# recover one data one Q
def recover_one_data_one_Q(data_chunks, parity_chunk_p, missing_index):
    chunk_length = len(data_chunks[0])
    data_chunks[missing_index] = [int("00", 16)] * chunk_length
    data_chunks = recover_one_data(data_chunks, parity_chunk_p, missing_index)
    Q = calculate_Q(data_chunks)
    return Q, data_chunks


# recover one data one P
def recover_one_data_from_Q(data_chunks, parity_chunk_Q, missing_index):
    chunk_length = len(data_chunks[0])
    data_chunks[missing_index] = [int("00", 16)] * chunk_length
    now_Q = calculate_Q(data_chunks)
    recover_Q = [
        F.Subtract(full, current) for full, current in zip(parity_chunk_Q, now_Q)
    ]
    data = [
        F.Multiply(recover, F.Inverse(gp_pow(g_0, missing_index)))
        for recover in recover_Q
    ]
    data_chunks[missing_index] = data
    return data_chunks


def recover_one_data_one_P(data_chunks, parity_chunk_Q, missing_index):
    data_chunks = recover_one_data_from_Q(data_chunks, parity_chunk_Q, missing_index)

    P = calculate_P(data_chunks)
    return P, data_chunks


def recover_PQ(data_chunks):
    P = calculate_P(data_chunks)
    Q = calculate_Q(data_chunks)
    return P, Q


def recover_two_data(data_chunks, parity_chunk_Q, parity_chunk_P, missing_indexes):
    chunk_length = len(data_chunks[0])
    if len(missing_indexes) > 2:
        print("we can not recover more than two data")
        return None
    data_chunks[missing_indexes[0]] = [int("00", 16)] * chunk_length
    data_chunks[missing_indexes[1]] = [int("00", 16)] * chunk_length
    Pxy = calculate_P(data_chunks)
    Qxy = calculate_Q(data_chunks)
    Dxdenominator = F.Add(gp_pow(g_0, missing_indexes[1] - missing_indexes[0]),int("01", 16))
    Dxnumerator = [
        F.Add(F.Multiply(F.Inverse(gp_pow(g_0, missing_indexes[0])), F.Add(q, qxy))
        , F.Multiply(
            (gp_pow(g_0, missing_indexes[1] - missing_indexes[0])),
            F.Add(p, pxy),
        ))
        for q, qxy, p, pxy in zip(parity_chunk_Q, Qxy, parity_chunk_P, Pxy)
    ]
    print("Dxdenominator",Dxdenominator)
    print("Dxnumerator",Dxnumerator)
    print(0,F.Multiply(Dxnumerator[0], F.Inverse(Dxdenominator)))
    print(1,F.Multiply(Dxnumerator[1], F.Inverse(Dxdenominator)))
    Dx = [F.Multiply(numerator, F.Inverse(Dxdenominator)) for numerator in Dxnumerator]
    Dy = [F.Add(F.Add(p, pxy), dx) for p, pxy, dx in zip(parity_chunk_P, Pxy, Dx)]
    data_chunks[missing_indexes[0]] = Dx
    data_chunks[missing_indexes[1]] = Dy

    return data_chunks


class RAID6:
    def __init__(self):
        self.F = ffield.FField(8)

    def encode_data(self, data_chunks):
        """
        对数据块进行编码，生成 P 和 Q 奇偶校验块。
        """
        parity_chunk_p = calculate_P(data_chunks)
        parity_chunk_q = calculate_Q(data_chunks)
        return parity_chunk_p, parity_chunk_q

    def recover_data(
        self, data_chunks, parity_chunk_p, parity_chunk_q, missing_type, missing_indices
    ):
        missing_indices.sort()
        if missing_type == "missing_P":
            parity_chunk_p = calculate_P(data_chunks)
            return parity_chunk_p
        if missing_type == "missing_Q":
            parity_chunk_q = calculate_Q(data_chunks)
            return parity_chunk_q
        if missing_type == "missing_one_data":
            data_chunks = recover_one_data(
                data_chunks, parity_chunk_p, missing_indices[0]
            )
            return data_chunks
        if missing_type == "missing_one_data_one_Q":
            Q, data_chunks = recover_one_data_one_Q(
                data_chunks, parity_chunk_p, missing_indices[0]
            )
            return Q, data_chunks
        if missing_type == "recover_one_data_one_P":
            P, data_chunks = recover_one_data_one_P(
                data_chunks, parity_chunk_q, missing_indices[0]
            )
            return P, data_chunks
        if missing_type == "recover_two_data":
            data_chunks=recover_two_data(data_chunks, parity_chunk_q, parity_chunk_p, missing_indices)
            return data_chunks


if __name__ == "__main__":
    raid=RAID6()
    datachunks = [
        [int("01", 16), int("02", 16), int("03", 16)],
        [int("02", 16), int("02", 16), int("03", 16)],
        [int("03", 16), int("02", 16), int("03", 16)],
        [int("04", 16), int("02", 16), int("ff", 16)],
    ]

    print("datachunks",datachunks)
    chunk_length=len(datachunks[0])
    chunk_num=len(datachunks)
    P,Q=raid.encode_data(datachunks)
    print("P",P)
    print("Q", Q)


    print("if P or Q is missing")
    P,Q=raid.encode_data(datachunks)
    print("P",P)
    print("Q",Q)



    print("if one data is missing")
    missing_index=2
    datachunks[missing_index]=[int("00", 16)]*3
    print("missing datachunks",datachunks,"P",P,"Q",Q)
    datachunks=raid.recover_data(
         datachunks, P, Q, "missing_one_data", [missing_index]
    )
    print("recover datachunks",datachunks,"P",P,"Q",Q)



    print("if one data and Q is missing")
    missing_index=3
    datachunks[missing_index]=[int("00", 16)]*3
    Q=None
    print("missing datachunks",datachunks,"P",P,"Q",Q)  
    Q,datachunks=raid.recover_data(
         datachunks, P, Q, "missing_one_data_one_Q", [missing_index]
    )
    print("recover datachunks",datachunks,"P",P,"Q",Q)




    print("if one data and P is missing")
    missing_index=1
    datachunks[missing_index]=[int("00", 16)]*3
    P=None
    print("missing datachunks",datachunks,"P",P,"Q",Q)  
    P,datachunks=raid.recover_data(
         datachunks, P, Q, "recover_one_data_one_P", [missing_index]
    )
    print("recover datachunks",datachunks,"P",P,"Q",Q)


    print("if two datasets are missing")
    missing_indexes=[1,2]
    for index in missing_indexes:
        datachunks[index]=[int("00", 16)]*3
    print("missing datachunks",datachunks,"P",P,"Q",Q)  
    datachunks=raid.recover_data(
         datachunks, P, Q, "recover_two_data", missing_indexes
    )
    print("recover datachunks",datachunks,"P",P,"Q",Q)
    # P,Q=raid.encode_data(datachunks)
    # print("P",P)
    # print("Q",Q)