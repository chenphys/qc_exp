from qiskit import QuantumCircuit , Aer , execute, IBMQ ,transpile
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error
import numpy as np
import QFT

def QPE(phi,n):
    circuit = QuantumCircuit(n+1,n)
    circuit.x(n)
    for qubit in range(n):
        circuit.h(qubit)
        circuit.cp(phi*(2**qubit),qubit,n)
    QFT.invQFT(circuit,n)
    circuit.measure(range(n),range(n))
    return circuit

if __name__ == '__main__':

    phi = 2*np.pi/3
    circuit = QPE(phi,3)
    sim = Aer.get_backend('statevector_simulator')
    job = execute(circuit,sim)
    statevector = job.result().get_statevector()
    print(statevector)
