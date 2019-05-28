import numpy as np
import heapq
import time
import csv
import matplotlib.pyplot as plt
import copy

# Constants
ISCHEMIC_RATE = None # days
HEMORRHAGIC_RATE = None # days

DURATION = None # days
CSC_IS_FULL = False
TRANSFER_NEEDED_PERCENTAGE = None
NON_STROKE_PATIENT_DURATION = None
PERCENTAGE_NON_STROKE = None
NUMBER_OF_SIMULATIONS = None

# set the seed
# np.random.seed(23)

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


        # self.duration = np.random.exponential(cost_RATE)
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
    def __init__(self, pid, number_of_beds, transfer_rate, arrival_rate):
        self.pid = pid
        self.number_spawned = 0
        self.max_beds = number_of_beds
        self.bed_count = 0
        self.transfer_rate = transfer_rate
        self.arrival_rate = arrival_rate
        self.rejected_count = 0
        self.time_stamps = []
        self.should_be_there_stamps = []
        self.should_not_be_there_stamps = []
        self.stroke_patient_stamps = []
        self.stroke_patient_count = 0
        self.should_be_at_csc = 0
        self.should_not_be_at_csc = 0
        self.average_bed_count = 0
        self.average_stroke_count = 0
        self.average_should_be = 0
        self.average_should_not = 0
        self.should_be_rej = 0
        self.should_not_be_rej = 0
    
    def process_departure(self, departure_event):
        '''
        Departure is the same for every hospital
        Decrement the bed count, add the time stamp for logging
        '''
        self.bed_count -= 1
        self.time_stamps.append((self.bed_count, departure_event.patient.completion_time))

        patient_obj = departure_event.patient
        if isinstance(patient_obj, Patient):
            self.stroke_patient_count -= 1
            if patient_obj.transfer_needed:
                self.should_be_at_csc -= 1
            else:
                self.should_not_be_at_csc -= 1

        self.should_be_there_stamps.append((self.should_be_at_csc, departure_event.patient.completion_time))
        self.should_not_be_there_stamps.append((self.should_not_be_at_csc, departure_event.patient.completion_time))
        self.stroke_patient_stamps.append((self.stroke_patient_count, departure_event.patient.completion_time))
            
        return False

    def helper_TWA(self, time_stamp_array):

        average = 0
        # time weighted average
        for i in range(len(time_stamp_array) - 1):
            pair1 = time_stamp_array[i]
            pair2 = time_stamp_array[i+1]
            gap = pair2[1] - pair1[1]
            time_slice = gap / DURATION
            average += pair1[0] * time_slice

        return average


    def calculate_average(self):
        '''
        Time Weighted Average (TWA) for bed counts for each hospital
        '''

        self.average_bed_count = self.helper_TWA(self.time_stamps)
        self.average_should_be = self.helper_TWA(self.should_be_there_stamps)
        self.average_should_not = self.helper_TWA(self.should_not_be_there_stamps)
        self.average_stroke_count = self.helper_TWA(self.stroke_patient_stamps)




    def pprint(self):
        '''
        Self explanatory
        '''
        self.calculate_average()
        print("------------------------")
        print("Hospital ID: ", self.pid)
        print("Max Beds: ", self.max_beds)
        print("Number Rejected: ", self.rejected_count)
        print("Number of Stroke Patients Rejected who should be there: ", self.should_be_rej)
        print("Number of Stroke Patients Rejected who should not be there: ", self.should_not_be_rej)
        print("Average Number of beds filled: ", self.average_bed_count)
        print("Average Stroke Patient Count: ", self.average_stroke_count)
        print("Average # of stroke patients that should be there: ", self.average_should_be)
        print("Average # of stroke patients that shouldn't be there: ", self.average_should_not)

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


    def graph_distribution(self):
        '''
        Plots the number of beds at each time stamp (event time step)
        '''

        self.calculate_average()

        x_vals = list(range(self.max_beds + 1))
        y_vals = [0 for x in range(self.max_beds + 1)]


        # average = 0
        # time weighted average
        for i in range(len(self.time_stamps) - 1):
            pair1 = self.time_stamps[i]
            pair2 = self.time_stamps[i+1]
            gap = pair2[1] - pair1[1]
            time_slice = gap / DURATION

            y_vals[pair1[0]] += time_slice

        plt.figure(figsize = (20, 5))
        plt.plot(x_vals, y_vals, '-o')
        plt.xlabel("Number of Beds Filled")
        plt.ylabel("Percentage of Time in that State")
        plt.title("Distribution of Beds Filled")
        plt.show()

        return
        # self.calculate_average()
        # y_vals = [x[0] for x in self.time_stamps]
        # x_vals = [x[1] for x in self.time_stamps]

        # plt.figure(figsize = (20, 5))
        # plt.plot(x_vals, y_vals, '--b')
        # plt.axhline(y = self.average_bed_count)
        # plt.xlabel("Time Stamp")
        # plt.ylabel("Number of Patients")
        # if self.pid == 0:
        #     plt.title("Number of Patients over Time at CSC")
        # else:
        #     plt.title("Number of Patients over Time at PSC #{}".format(self.pid))
        # plt.show()

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
        if np.random.uniform() < self.transfer_rate and isinstance(patient, Patient):
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
        # self.time_stamps.append((self.bed_count, patient.completion_time))
        # return False
    


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

        if self.bed_count <= self.max_beds:
            CSC_IS_FULL = False
            self.bed_count += 1
            departure_event = Event(patient_obj, patient_obj.completion_time, "Departure", self.pid)

            if isinstance(patient_obj, Patient):
                self.stroke_patient_count += 1
                if patient_obj.transfer_needed:
                    self.should_be_at_csc += 1
                else:
                    self.should_not_be_at_csc += 1

            return departure_event

                # patient_obj = departure_event.patient

        # print("Rejected")
        CSC_IS_FULL = True
        self.rejected_count += 1
        if isinstance(patient_obj, Patient):
            if patient_obj.transfer_needed:
                self.should_be_rej += 1
            else:
                self.should_not_be_rej += 1

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

                if np.random.uniform() < PERCENTAGE_NON_STROKE:
                    new_patient = NonStrokePatient(number_spawned, current_time)
                    current_time += np.random.exponential(1.0 / hospital.arrival_rate)
                else:
                    new_patient = Patient(number_spawned, current_time)

                    # new_patient = Patient(number_spawned, current_time)
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
    def __init__(self, sid, hospital_dict, verbose = False):
        self.sid = sid
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

    simulation_num = len(list_of_simulations)

    avg_rej = 0
    avg_rej_should = 0
    avg_rej_should_not = 0
    avg_number_beds_filled = 0
    avg_stroke_patient_count = 0
    avg_should = 0
    avg_should_not = 0

    for simulation in list_of_simulations:
        for hospital in simulation.hospital_dict.values():
            if isinstance(hospital, CSC):
                hospital.calculate_average()
                avg_rej += hospital.rejected_count
                avg_rej_should += hospital.should_be_rej
                avg_rej_should_not += hospital.should_not_be_rej
                avg_number_beds_filled += hospital.average_bed_count
                avg_stroke_patient_count += hospital.average_stroke_count
                avg_should += hospital.average_should_be
                avg_should_not += hospital.average_should_not
    
    avg_rej /= simulation_num
    avg_rej_should /= simulation_num
    avg_rej_should_not /= simulation_num
    avg_number_beds_filled /= simulation_num
    avg_stroke_patient_count /= simulation_num
    avg_should /= simulation_num
    avg_should_not /= simulation_num

    print("---------------------------------------------------")
    print("################ Averaged Results #################")
    print("---------------------------------------------------")
    print("Number Rejected: ", avg_rej)
    print("Number of Stroke Patients Rejected who should be there: ", avg_rej_should)
    print("Number of Stroke Patients Rejected who should not be there: ", avg_rej_should_not)
    print("Percentage of Stroke Patients who were REJECTED \n \
        that should have been transferred {0:4.2f}%".format(100 * avg_rej_should / avg_rej))
    print("Average Number of beds filled: {0:4.2f}".format(avg_number_beds_filled))
    print("Average Stroke Patient Count: {0:4.2f}".format(avg_stroke_patient_count))
    print("Average # of stroke patients that should be there: {0:4.2f}".format(avg_should))
    print("Average # of stroke patients that shouldn't be there: {0:4.2f}".format(avg_should_not))
    print("---------------------------------------------------")

    return



def all_entries_empty(list_strings):
    return not list(filter(lambda x: x, list_strings))

# average length of stay in hospital is 4.5 days

if __name__ == "__main__":

    hospital_list = []

    print("Reading the Config File...")
    with open('hospitals.csv', 'r', encoding='utf-8-sig') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        rows = [row for row in readCSV]

        i = 0

        while 'Parameters' not in rows[i]:
            i += 1

        i += 1
        ISCHEMIC_RATE = float(rows[i][1])
        # i += 1
        HEMORRHAGIC_RATE = float(rows[i+1][1])
        # i += 1
        NON_STROKE_PATIENT_DURATION = float(rows[i+2][1])
        # i += 1
        PERCENTAGE_NON_STROKE = float(rows[i+3][1])
        # i += 1
        TRANSFER_NEEDED_PERCENTAGE = float(rows[i+4][1])
        # i += 1
        DURATION = float(rows[i+5][1])
        # i += 1
        NUMBER_OF_SIMULATIONS = int(rows[i+6][1])
        i += 7

        while 'CSC Configuration:' not in rows[i]:
            # print(i)
            i += 1
            # advance while we still have 
        if 'CSC Configuration:' in rows[i]:
            i += 1

            while 'PSC Configuration:' not in rows[i]:
                if not all_entries_empty(rows[i]):
                    # print(rows[i])
                    hospital_index = 0
                    hospital_name = rows[i][1]
                    number_beds_ICU = int(rows[i][2])
                    arrival_rate_ICU = float(rows[i][3])

                    hospital_list.append(CSC(hospital_index, 
                                            number_beds_ICU,
                                            0.0,
                                            arrival_rate_ICU))

                i += 1
                # print(i)
            i += 1
            while i < len(rows):
                if not all_entries_empty(rows[i]):
                    # print(rows[i])
                    hospital_index += 1
                    hospital_name = rows[i][1]
                    hospital_transfer_rate = float(rows[i][2])
                    arrival_rate_patients_to_hospital = float(rows[i][3])

                    hospital_list.append(PSC(hospital_index,
                                            0,
                                            hospital_transfer_rate,
                                            arrival_rate_patients_to_hospital))
                i += 1

        else:
            print("Something wrong with the config file, please reset back to base state")
            # exit

    print("     -> Finished Reading the Config File!\n")

    print("Building the simulations...\n")

    hospital_dict = build_hospital_dict(hospital_list)

    simulations = []

    for i in range(NUMBER_OF_SIMULATIONS):

        print("Starting Simulation # {}...".format(i + 1))

        my_hospital_dict = copy.deepcopy(hospital_dict)

        mySimulation = Simulation(i, my_hospital_dict)
        # mySimulation.set_verbose(False)
        mySimulation.run_simulation()

        for hospital in my_hospital_dict.values():
            if isinstance(hospital, CSC):
                # pass
                hospital.pprint()
                # print(hospital.time_stamps)
                # hospital.graph_count()

                hospital.graph_distribution()


        simulations.append(mySimulation)
        print("     -> Finished Simulation # {}!\n".format(i + 1))

    combine_simulations(simulations)
    # for hospital in hospital_list:
    #     if isinstance(hospital, CSC):
    #         # pass
    #         hospital.pprint()
    #         # print(hospital.time_stamps)
    #         hospital.graph_count()