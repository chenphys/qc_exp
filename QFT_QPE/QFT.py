from qiskit import QuantumCircuit , Aer , execute, IBMQ ,transpile
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error
import numpy as np


def QFT_rotation(quantumcircuit,n):
    if n == 0: return quantumcircuit

    else:
        n -=1
        quantumcircuit.h(n)
        for qubit in range(n):
            quantumcircuit.cp(np.pi/(2**(n-qubit)),qubit,n)
        QFT_rotation(quantumcircuit,n)

def swap(quantumcircuit,n):
    for qubit in range(n//2):
        quantumcircuit.swap(qubit,n-qubit-1)
    return quantumcircuit

def QFT(quantumcircuit,n):
    QFT_rotation(quantumcircuit,n)
    swap(quantumcircuit,n)
    return quantumcircuit


def invQFT(quantumcircuit,n):
    circuit = QuantumCircuit(n)
    QFT(circuit,n)
    circuit = circuit.inverse()
    quantumcircuit.append(circuit,quantumcircuit.qubits[:n])
    return quantumcircuit.decompose()


if __name__ =='__main__':

    qc = QuantumCircuit(5)
    qc.x(0)
    QFT(qc,5)
    invQFT(qc,5)
    qc.measure_all()


    sim = Aer.get_backend('statevector_simulator')
    job = execute(qc,sim)
    result = job.result()
    statevector = result.get_statevector()
    print(statevector)
