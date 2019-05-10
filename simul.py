import numpy as np

# Constants
PSC_TRANSFER_RATE = 10 # poisson (arrivals per minute)
CSC_PROCESSING_RATE = 3 # exponential
NUMBER_OF_PSC_HOSPITALS = 5
CSC_ARRIVAL_RATE = NUMBER_OF_PSC_HOSPITALS * PSC_TRANSFER_RATE # poisson
NUMBER_OF_BEDS_AT_CSC = 50 # check on this
DURATION = 100 # min
COST_PER_BED_PER_DAY = 12345 # dollars



# set the seed
np.random.seed(23)

class Patient:
    '''
    Represents a single entity in the system (i.e. a 'stroke patient')
    Contains a unique ID (essentially used for comparison with other patients)
    Spawn Time - time that the patient was sent away from hospital
    Duration - The processing time they would see at the CSC
    '''
    def __init__(self, pid, current_time):
        self.id = pid
        self.spawn_time = current_time
        self.duration = np.random.exponential(CSC_PROCESSING_RATE)
        self.completion_time = self.spawn_time + self.duration

class Event:
    '''
    Parent class for an event
    Takes in the event stuff and just wraps both types of events
    '''
    def __init__(self, patient, completion_time):
        self.patient = patient
        self.completion_time = completion_time

class Arrive(Event):
    '''
    Represents the arrival to the CSC
    '''
    pass

class Depart(Event):
    '''
    Represents the departure from the CSC
    '''
    pass

class CSCSpawner:
    '''
    This is just a star model so the CSC is at the center and it is fed by multiple hospitals
    We model the arrival rates to the hospital as the sum of the exit rates from the PSCs

    This discrete event simulation is an abstraction - we first generate all of the possible
    entities in the system into a big queue as the composition of the separate PSCs

    We then build up this queue to pull from later in the hospital
    '''
    def __init__(self):
        self.duration = DURATION
        self.current_time = 0
        self.number_spawned = 0
        self.spawning_rate = CSC_ARRIVAL_RATE
        self.spawning_queue = []

        while self.current_time < self.duration:
            self.spawn_patient()

    def spawn_patient(self):
        new_patient = Patient(self.number_spawned, self.current_time)
        self.spawning_queue.append(new_patient)
        self.current_time += np.random.exponential(1.0 / CSC_ARRIVAL_RATE)
        self.number_spawned += 1

    def pprint(self):
        print("Duration: {}".format(self.duration))
        print("Patients Spawned: {}".format(self.number_spawned))

# Make a sorted list of events
# arrivals = CSCSpawner()
# queue = [Arrive(x, x.spawn_time) for x in arrivals.spawning_queue]

class Hospital:
    '''
    This represents the actual Hospital - the CSC where the beds are limited
    We have a max beds field (max beds)
    beds = [list of patients who are being treated]
    rejected_count - exactly what it sounds like
    spawner_queue - queue of patients to populate the beds with
    '''
    def __init__(self):
        self.max_beds = NUMBER_OF_BEDS_AT_CSC
        self.beds = []
        self.rejected_count = 0
        self.spawner_queue = CSCSpawner().spawning_queue
        self.current_time = 0
        self.event_queue = [Arrive(x, x.spawn_time) for x in self.spawner_queue] # this is gonna be interesting
        self.duration = DURATION

    def sort_event_queue(self):
        self.event_queue = sorted(self.event_queue, key = lambda x: x.completion_time)
    
    def get_next_event(self):
        '''
        Getter to pop off the queue
        '''
        if self.event_queue:
            return self.event_queue.pop(0)
        else:
            return False

    def process_arrival(self, arrival):
        '''
        Process an arrival to the CSC
        If the beds are not full, log the arrival and create a departure event
        add it to the queue

        If the beds are full, increment the rejected count and move on to the next event
        '''
        patient_obj = arrival.patient
        # print(len(self.beds))
        if len(self.beds) < self.max_beds:
            print("Arrived: Patient #{}, at time {} with {} available beds".format(patient_obj.id, 
            self.current_time, self.max_beds - len(self.beds)))
            self.beds.append(patient_obj)
            departure_event = Depart(patient_obj, patient_obj.completion_time)
            self.event_queue.append(departure_event)
        else:
            print("Rejected: Patient #{}, beds full at time {}".format(patient_obj.id, self.current_time))
            self.rejected_count += 1

    def process_departure(self, departure):
        '''
        Process a departure from the CSC
        Increments the beds
        '''
        patient_obj = departure.patient
        print("Departed: Patient #{}, at time {}".format(patient_obj.id, self.current_time))
        self.beds = [x for x in self.beds if x.id != patient_obj.id]

    def process_events(self):
        # print(len(self.event_queue))
        event = self.get_next_event()

        if isinstance(event, Arrive):
            self.process_arrival(event)
            # pass

        elif isinstance(event, Depart):
            self.process_departure(event)
            # pass
        
        self.current_time = event.completion_time
        self.sort_event_queue()

    def run_simulation(self):
        while self.current_time < self.duration:
            self.process_events()

        print(self.rejected_count)

hospital = Hospital()

hospital.run_simulation()


# for patient in hospital.spawner_queue:
#     print(patient.completion_time)



# Arrive(15)












