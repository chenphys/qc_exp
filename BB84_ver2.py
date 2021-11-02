from qiskit import QuantumCircuit , Aer , execute, IBMQ ,transpile
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import matplotlib.pyplot as plt
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error, depolarizing_error
import numpy as np

###################

###################
class BB84:
    def __init__(self,size,epslion = 0):
        self.size = size
        self.epslion = epslion
        self.alice = self.vector(self.size)
        self.x = self.vector(self.size)
        self.y = self.vector(self.size)

        self.circuit_list = []
        self.sim = Aer.get_backend('qasm_simulator')
        self.key_alice=[]
        self.key_bob=[]
        self.key_eve=[]
        self.key=[]
        self.bob=np.zeros(self.size)
        self.eve=np.zeros(self.size)
        self.noise = NoiseModel()
        self.error = pauli_error([('X',self.epslion),('Z',self.epslion),('I',1-2*self.epslion)])

    
    #make a random array of length consist of 0 or 1    
    def vector(self,length): return np.random.randint(0,2,length)
    
    
    #clear everytime before sending
    def clear(self):
        self.alice = self.vector(self.size)
        self.x = self.vector(self.size)
        self.y = self.vector(self.size)
        self.z = self.vector(self.size)

        self.circuit_list = []
        self.key_alice = []
        self.key_bob = []
        self.key_eve = []
        self.key = []
        self.bob = np.zeros(self.size)
        self.eve = np.zeros(self.size)
        return
    
    
    #sending and receiving the qubits without eve
    def sending(self):
        self.clear()

        for i in range(self.size):
            circuit = QuantumCircuit(1,1)
            if self.alice[i] == 1: circuit.x(0)
            if self.x[i] == 1:circuit.h(0)
            circuit.barrier()
            if self.y[i] == 1:circuit.h(0)
            circuit.measure(0,0)
            self.circuit_list.append(circuit)

        self.noise.add_all_qubit_quantum_error(self.error,'measure')
        self.job = execute(self.circuit_list,self.sim,shots = 1,noise_model = self.noise)
        self.result = self.job.result()
        self.counts = self.result.get_counts()
        for i in range(self.size):
            self.keys = list(self.counts[i].keys())
            self.bob[i]=self.keys[0]
        self.bob = self.bob.astype(int)

        return
    
    
    #sending and receiving the qubits with eve
    def sending_witheve(self):
        self.clear()

        for i in range(self.size):
            circuit = QuantumCircuit(2, 2)
            if self.alice[i] == 1: circuit.x(0)
            if self.x[i] == 1: circuit.h(0)
            circuit.barrier()
            if self.z[i] == 1:circuit.h(0)
            circuit.cx(0,1)
            if self.z[i] == 1:circuit.h(0)#if the basis eve use is constant, the error is lower for some reason
            circuit.measure(1,1)
            circuit.barrier()
            if self.y[i] == 1: circuit.h(0)
            circuit.measure(0,0)
            self.circuit_list.append(circuit)

        self.noise.add_all_qubit_quantum_error(self.error, 'measure')
        self.job = execute(self.circuit_list, self.sim, shots=1, noise_model=self.noise)
        self.result = self.job.result()
        self.counts = self.result.get_counts()
        for i in range(self.size):
            self.keys = list(self.counts[i].keys())
            a = self.keys[0]
            self.bob[i] = a[0]
            self.eve[i] = a[1]
        self.bob = self.bob.astype(int)
        self.eve = self.eve.astype(int)

        return
    
    
    #public the basis they use without eve
    def public(self):
        for i in range(self.size):
            if self.x[i] == self.y[i]:
                self.key_bob.append(self.bob[i])
                self.key_alice.append(self.alice[i])
                self.key.append(i)
        return
    
    
    #public the basis they use with eve    
    def public_witheve(self):
        for i in range(self.size):
            if self.x[i] == self.y[i]:
                self.key_bob.append(self.bob[i])
                self.key_alice.append(self.alice[i])
                self.key_eve.append(self.eve[i])
                self.key.append(i)
        return
    
    
    # show the resulting key and so without eve           
    def show(self):
        print('alice:', self.alice)
        print('x:', self.x)
        print('bob:',self.bob.astype(int))
        print('y:', self.y)

        print("alice's key:", self.key_alice)
        print("bob's key  :", self.key_bob)
        print('key:', self.key)
        return
    
    
    #show the resulting key and so with eve
    def show_witheve(self):
        print('alice:', self.alice)
        print('x:', self.x)
        print('bob:',self.bob.astype(int))
        print('y:', self.y)
        print('eve:',self.eve)
        print('z',self.z)

        print("alice's key:", self.key_alice)
        print("bob's key  :", self.key_bob)
        print("eve's key  :",self.key_eve)
        print('key:', self.key)
        return
    
    
    #run the whole experiment
    def run(self,show = True):
        self.sending()
        self.public()
        if show:self.show()


        return

    
    #run the whole experiment with eve
    def run_witheve(self,show = True):
        self.sending_witheve()
        self.public_witheve()
        if show:self.show_witheve()
        return 

            
    # value of P
    def P(self):
        if len(self.key_alice) != len(self.key_bob):
            print('you fucking donkey')
            return
        e = 0
        for i in range(len(self.key_alice)):
            if self.key_alice[i] != self.key_bob[i]:e+=1
        return e/len(self.key_alice)

    
    
#main code
if __name__ == '__main__':
    size = 40 
    error = 0.04
    bb = BB84(size,error)      #sending without eve (numeber of qubits sending,error of measurement)
    bb.run()                   #sending and public
    print(bb.P())              #P = # of differences in A and B's key/ the length of the key 
    
    bbev = BB84(size,error)      #sending with eve
    bbev.run_witheve()         
    print(bbev.P())

'''
#this part is to plot P(L) with e = 0.04
#I don't know what's the point of this part, L have nothing to do with the error, so this plot is meaningless. Unless I misunderstood the question.

    ptol = []
    #L = 10 to 100, intevral of 2
    
    for i in range(10,100,2):
        bb84 = BB84(i,0.04)
        bb84.run(show=False)
        ptol.append(bb84.P())
    x = np.arange(10,100,2)
    x.astype(int)
    plt.plot(x,ptol)
    print(ptol)
    plt.show()
'''
