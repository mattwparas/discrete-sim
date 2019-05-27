import numpy as np
import heapq
import time
import matplotlib.pyplot as plt

# Constants
PSC_TRANSFER_RATE = 1 # poisson (arrivals per day)
CSC_PROCESSING_RATE = 5 # exponential
ISCHEMIC_RATE = 4 #
HEMORRHAGIC_RATE = 6 #
NUMBER_OF_PSC_HOSPITALS = 5
# CSC_ARRIVAL_RATE = NUMBER_OF_PSC_HOSPITALS * PSC_TRANSFER_RATE # poisson
CSC_ARRIVAL_RATE = 5 # per day
NUMBER_OF_BEDS_AT_CSC = 50 # check on this
DURATION = 1000 # min
COST_PER_BED_PER_DAY = 12345 # dollars
CSC_IS_FULL = False
TRANSFER_NEEDED_PERCENTAGE = .10
NON_STROKE_PATIENT_DURATION = 5
PERCENTAGE_NON_STROKE = .80

# set the seed
np.random.seed(23)

class Patient:
    '''
    Represents a single entity in the system (i.e. a 'patient')
    Contains a unique ID (essentially used for comparison with other patients)
    Spawn Time - time that the patient was sent away from hospital
    Duration - The processing time they would see at the CSC
    '''
    def __init__(self, pid, current_time):
        self.id = pid
        self.spawn_time = current_time

        if np.random.uniform() < .15:
            self.stroke_type = "HEMORRHAGIC"
            self.duration = np.random.exponential(HEMORRHAGIC_RATE)
            self.transfer_needed = True
        else:
            self.stroke_type = "ISCHEMIC"
            self.duration = np.random.exponential(ISCHEMIC_RATE)

            if np.random.uniform() < TRANSFER_NEEDED_PERCENTAGE:
                self.transfer_needed = True
            else:
                self.transfer_needed = False


        # self.duration = np.random.exponential(CSC_PROCESSING_RATE)
        self.completion_time = self.spawn_time + self.duration

        # cost
        # self.cost = 0

    def update_completion_time(self, duration):
        self.completion_time += duration



class NonStrokePatient:
    '''
    Represents a single entity in the system (i.e. a 'patient')
    Contains a unique ID (essentially used for comparison with other patients)
    Spawn Time - time that the patient was sent away from hospital
    Duration - The processing time they would see at the CSC
    '''
    def __init__(self, pid, current_time):
        self.id = pid
        self.spawn_time = current_time

        self.duration = np.random.exponential(NON_STROKE_PATIENT_DURATION)
        self.completion_time = self.spawn_time + self.duration

        # cost
        # self.cost = 0

    def update_completion_time(self, duration):
        self.completion_time += duration


class Event:
    '''
    Event class
    These are the different kinds of events that take place at given location
    '''
    def __init__(self, patient, completion_time, event_type, hospital_id):
        self.patient = patient
        self.completion_time = completion_time
        self.event_type = event_type
        self.hospital_id = hospital_id

    def __lt__(self, other):
        return self.completion_time < other.completion_time

    def pprint(self):
        print("{} at time {}, hospital {}".format(self.event_type, self.completion_time, self.hospital_id))



class Hospital:
    '''
    Hospitals represent nodes
    Parent class for CSC and PSC
    Store a bunch of information regarding the rates
    Stores a bunch of meta data about the simulation process
    '''
    def __init__(self, pid, number_of_beds, processing_mean, transfer_rate, arrival_rate):
        self.pid = pid
        self.number_spawned = 0
        self.max_beds = number_of_beds
        self.bed_count = 0
        self.transfer_rate = transfer_rate
        self.processing_mean = processing_mean
        self.arrival_rate = arrival_rate
        self.rejected_count = 0
        self.time_stamps = []
        self.average_bed_count = 0
    
    def process_departure(self, departure_event):
        '''
        Departure is the same for every hospital
        Decrement the bed count, add the time stamp for logging
        '''
        self.bed_count -= 1
        self.time_stamps.append((self.bed_count, departure_event.patient.completion_time))
        return False

    def calculate_average(self):
        '''
        Time Weighted Average (TWA) for bed counts for each hospital
        '''
        average = 0
        # time weighted average
        for i in range(len(self.time_stamps) - 1):
            pair1 = self.time_stamps[i]
            pair2 = self.time_stamps[i+1]
            gap = pair2[1] - pair1[1]
            time_slice = gap / DURATION
            average += pair1[0] * time_slice

        self.average_bed_count = average


    def pprint(self):
        '''
        Self explanatory
        '''
        self.calculate_average()
        print("------------------------")
        print("Hospital ID: ", self.pid)
        print("Max Beds: ", self.max_beds)
        print("Number Rejected: ", self.rejected_count)
        print("Average Number of beds filled: ", self.average_bed_count)

    def graph_count(self):
        '''
        Plots the number of beds at each time stamp (event time step)
        '''
        self.calculate_average()
        y_vals = [x[0] for x in self.time_stamps]
        x_vals = [x[1] for x in self.time_stamps]

        plt.figure(figsize = (20, 5))
        plt.plot(x_vals, y_vals, '--b')
        plt.axhline(y = self.average_bed_count)
        plt.xlabel("Time Stamp")
        plt.ylabel("Number of Patients")
        if self.pid == 0:
            plt.title("Number of Patients over Time at CSC")
        else:
            plt.title("Number of Patients over Time at PSC #{}".format(self.pid))
        plt.show()

class PSC(Hospital):
    '''
    Child class for the PSC
    Processes Arrivals Differently
    Think of the parent class as the standard for nodes
    '''
    def process_arrival(self, arrival_event):
        '''
        If there are beds available at the hospital, process patient
        If it is a stroke patient to be transfered, send along with time-to-transfer

        If no beds available, ignore patient essentially (pretty bad)
        '''
        patient = arrival_event.patient
        # if self.bed_count < self.max_beds:
        if np.random.uniform() < .13:
            if not CSC_IS_FULL:
                # transfer immediately to the CSC
                transfer_time = 0
                arrival_event = Event(patient, patient.spawn_time + 0, "Arrival", 0)
                patient.update_completion_time(0)
                return arrival_event

        # else:
        self.bed_count += 1
        # generate a departure event, for the duration of their visit
        departure_event = Event(patient, patient.completion_time, "Departure", self.pid)
        return departure_event

        # CSC_IS_FULL = False
        # self.rejected_count += 1
        self.time_stamps.append((self.bed_count, patient.completion_time))
        return False
    


class CSC(Hospital):
    '''
    Child class for the CSC
    Processes arrivals differently from PSC
    '''
    def process_arrival(self, arrival_event):
        '''
        Take in a patient
        If the bed count has been reached, reject and set the CSC to be full
        if not, take in the patient and calculate a completion_time
        '''

        patient_obj = arrival_event.patient

        if self.bed_count < self.max_beds:
            CSC_IS_FULL = False
            self.bed_count += 1
            departure_event = Event(patient_obj, patient_obj.completion_time, "Departure", self.pid)
            return departure_event

        # print("Rejected")
        CSC_IS_FULL = True
        self.rejected_count += 1
        return False



def arrival_spawner(list_of_hospitals):
    '''
    This is just a star model so the CSC is at the center and it is fed by multiple hospitals
    We model the arrival rates to the hospital as the sum of the exit rates from the PSCs

    This discrete event simulation is an abstraction - we first generate all of the possible
    entities in the system into a big queue as the composition of the separate PSCs

    We then build up this queue to pull from later in the hospital
    '''

    spawning_queue = []
    number_spawned = 0

    for hospital in list_of_hospitals:
        if isinstance(hospital, PSC):
            current_time = 0
            while current_time < 2*DURATION:
                new_patient = Patient(number_spawned, current_time)
                new_event = Event(new_patient, current_time, "Arrival", hospital.pid)
                spawning_queue.append(new_event)
                current_time += np.random.exponential(1.0 / hospital.arrival_rate)
                number_spawned += 1
            
        else:
            current_time = 0
            while current_time < 2*DURATION:

                if np.random.uniform() < PERCENTAGE_NON_STROKE:
                    new_patient = NonStrokePatient(number_spawned, current_time)
                else:
                    new_patient = Patient(number_spawned, current_time)

                new_event = Event(new_patient, current_time, "Arrival", hospital.pid)
                spawning_queue.append(new_event)
                current_time += np.random.exponential(1.0 / hospital.arrival_rate)
                number_spawned += 1
        

    return spawning_queue


def build_hospital_dict(list_of_hospitals):
    '''
    Map hospital ID to hospital via dictionary from list of hospitals generated
    '''
    hdict = {}
    for hospital in list_of_hospitals:
        hdict[hospital.pid] = hospital
    return hdict

class Simulation:
    '''
    Parent class for Simulation
    '''
    def __init__(self, hospital_dict, verbose = False):
        self.hospital_dict = hospital_dict
        self.event_queue = arrival_spawner(hospital_list)
        heapq.heapify(self.event_queue)
        self.current_time = 0
        self.duration = DURATION
        self.verbose = False

    def set_verbose(self, verbosity):
        '''
        print levels for the simulation (on or off)
        '''
        self.verbose = verbosity

    def get_hospital(self, hid):
        '''
        getter helper
        '''
        return self.hospital_dict[hid]

    def get_next_event(self):
        '''
        Getter to pop off the queue
        '''
        if self.event_queue:
            return heapq.heappop(self.event_queue)
        else:
            return False

    def process_event(self, event):
        '''
        process either event
        '''
        temp_hospital = self.get_hospital(event.hospital_id)
        
        if event.event_type == "Arrival":
            if self.verbose:
                print("Arrived: Patient #{}, at time {}, at hospital {}".format(event.patient.id, 
                self.current_time, event.hospital_id))

            new_event = temp_hospital.process_arrival(event)

        elif event.event_type == "Departure":
            if self.verbose:
                print("Departure: Patient #{}, at time {}, at hospital {}".format(event.patient.id, 
                self.current_time, event.hospital_id))
                
            new_event = temp_hospital.process_departure(event)
        
        if new_event:
            heapq.heappush(self.event_queue, new_event)

        self.current_time = event.completion_time
        
        return

    def run_simulation(self):
        '''
        run it baby
        '''
        while self.current_time < self.duration:
            next_event = self.get_next_event()

            self.process_event(next_event)


def combine_simulations(list_of_simulations):
    '''
    average results from the simulation somehow
    '''
    return

# average length of stay in hospital is 4.5 days

if __name__ == "__main__":

    # constructor -> pid, number_of_beds, processing_mean, transfer_rate, arrival_rate:

    # PSCs -> default the number of beds to None
    # PSCs -> processing_mean doesn't matter
    # PSCs -> transfer_rate is important
    # arrival_rate -> arrival rate of normal patient
    # assume the CSC does not transfer Non-Stroke-Patients to CSC


    # CSC:
    #   Number of beds -> Number of beds in the ICU
    #   Processing_mean -> doesn't matter
    #   Transfer rate is not important
    #   Arrival Rate -> Arrival Rate of patients to the ICU
    #   
    
    hospital_list = [
        PSC(1, 25, 4, .14, 4),
        PSC(2, 25, 4, .14, 4),
        PSC(3, 25, 4, .14, 4),
        PSC(4, 25, 4, .14, 4),
        PSC(5, 25, 4, .14, 4),
        CSC(0, 15, 4, .14, 4)
    ]
    
    # event_queue = arrival_spawner(hospital_list)

    hospital_dict = build_hospital_dict(hospital_list)
    mySimulation = Simulation(hospital_dict)
    mySimulation.set_verbose(True)
    mySimulation.run_simulation()
    for hospital in hospital_list:
        # pass
        hospital.pprint()
        # print(hospital.time_stamps)
        hospital.graph_count()