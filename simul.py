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
        else:
            self.stroke_type = "ISCHEMIC"
            self.duration = np.random.exponential(ISCHEMIC_RATE)


        # self.duration = np.random.exponential(CSC_PROCESSING_RATE)
        self.completion_time = self.spawn_time + self.duration

        # cost
        # self.cost = 0

    def update_completion_time(self, duration):
        self.completion_time += duration

class Event:
    '''
    Parent class for an event
    Takes in the event stuff and just wraps both types of events
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
    
    def process_departure(self, departure_event):
        self.bed_count -= 1
        self.time_stamps.append((self.bed_count, departure_event.patient.completion_time))
        return False

    def pprint(self):
        print("------------------------")
        print("Hospital ID: ", self.pid)
        print("Max Beds: ", self.max_beds)
        print("Number Rejected: ", self.rejected_count)

    def graph_count(self):
        y_vals = [x[0] for x in self.time_stamps]
        x_vals = [x[1] for x in self.time_stamps]

        plt.plot(x_vals, y_vals, 'o')
        plt.show()

class PSC(Hospital):
    def process_arrival(self, arrival_event):

        # print(self.bed_count)

        patient = arrival_event.patient

        if self.bed_count < self.max_beds:

            if np.random.uniform() < .13:
                # transfer immediately to the CSC
                arrival_event = Event(patient, patient.spawn_time + 0, "Arrival", 0)
                return arrival_event
            
            else:
                self.bed_count += 1
                # generate a departure event, for the duration of their visit
                departure_event = Event(patient, patient.completion_time, "Departure", self.pid)
                return departure_event

        # print("Rejected")
        self.rejected_count += 1

        self.time_stamps.append((self.bed_count, patient.completion_time))

        return False
    


class CSC(Hospital):
    def process_arrival(self, arrival_event):

        patient_obj = arrival_event.patient

        if self.bed_count < self.max_beds:

            self.bed_count += 1

            # print(self.bed_count)

            departure_event = Event(patient_obj, patient_obj.completion_time, "Departure", self.pid)

            return departure_event

        # print("Rejected")
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

    return spawning_queue


def build_hospital_dict(list_of_hospitals):
    hdict = {}
    for hospital in list_of_hospitals:
        hdict[hospital.pid] = hospital
    return hdict

class Simulation:
    def __init__(self, hospital_dict, event_queue):
        self.hospital_dict = hospital_dict
        self.event_queue = event_queue
        heapq.heapify(self.event_queue)
        self.current_time = 0
        self.duration = DURATION

    def get_hospital(self, hid):
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
        temp_hospital = self.get_hospital(event.hospital_id)
        
        if event.event_type == "Arrival":

            print("Arrived: Patient #{}, at time {}, at hospital {}".format(event.patient.id, 
            self.current_time, event.hospital_id))

            new_event = temp_hospital.process_arrival(event)

        elif event.event_type == "Departure":

            print("Departure: Patient #{}, at time {}, at hospital {}".format(event.patient.id, 
            self.current_time, event.hospital_id))
            
            new_event = temp_hospital.process_departure(event)
        
        if new_event:
            heapq.heappush(self.event_queue, new_event)

        self.current_time = event.completion_time
        
        return

    def process_arrival(self, arrival):
        '''
        Process an arrival to any hospital
        If the beds are not full, log the arrival and create a departure event
        add it to the queue

        If the beds are full, increment the rejected count and move on to the next event
        '''
        # patient_obj = arrival.patient

        temp_hospital = self.get_hospital(arrival.hospital_id)

        new_event = temp_hospital.process_arrival(arrival)

        if new_event:
            heapq.heappush(self.event_queue, new_event)

    def process_departure(self, departure):
        '''
        2 cases:
            - process a departure from the PSC in which the patient is being transfered to the CSC
            - process a departure from the CSC
        '''
        # patient_obj = departure.patient

        temp_hospital = self.get_hospital(departure.hospital_id)

        new_event = temp_hospital.process_departure(departure)

        if new_event:
            heapq.heappush(self.event_queue, new_event)

    def run_simulation(self):

        # number_of_events = 0.0
        # bed_count = 0.0

        while self.current_time < self.duration:
            # print(self.current_time)
            next_event = self.get_next_event()

            self.process_event(next_event)

            # self.process_events()
            # bed_count += self.bed_count
            # number_of_events += 1

        # average_bed_count = bed_count / number_of_events

        # print("Average Bed Count : {}".format(average_bed_count))




if __name__ == "__main__":
    
    hospital_list = [
        PSC(1, 25, 4, .14, 4),
        PSC(2, 25, 4, .14, 4),
        PSC(3, 25, 4, .14, 4),
        PSC(4, 25, 4, .14, 4),
        PSC(5, 25, 4, .14, 4),
        CSC(0, 25, 4, .14, 4)
    ]
    
    event_queue = arrival_spawner(hospital_list)

    hospital_dict = build_hospital_dict(hospital_list)

    mySimulation = Simulation(hospital_dict, event_queue)

    mySimulation.run_simulation()

    for hospital in hospital_list:
        # pass
        hospital.pprint()
        # print(hospital.time_stamps)
        hospital.graph_count()




