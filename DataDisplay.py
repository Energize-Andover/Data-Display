"""
#
# File:              DataDisplay.py
# Author:            danIv (Daniel Ivanovich)
# Created:           07/28/2018
# Description:       Uses GUI to display either CO2 levels or Temperatures.
#
"""

# -*- coding: utf-8 -*-

from tkinter import *
import pandas as pd
import numpy
import os
import threading
import time

pd.options.mode.chained_assignment = None  # Stop chained assignment warnings - I know what I'm doing

DEFAULT_DATA_PATH = os.path.join('CSVs', 'default_data.csv')
ROOM_SENSOR_PATH = os.path.join('CSVs', 'ahs_air.csv')
SAVED_DATA_PATH = os.path.join('CSVs', 'ahs_air_data.csv')
HOSTNAME = '10.12.4.98'
PORT = '8000'

request_thread = None
air_values = None

background_data_update = True


def save_data():
    if air_values is not None:
        print('Saving session data... please wait')
        air_values.to_csv(SAVED_DATA_PATH)


def stop():
    import sys
    save_data()
    sys.exit()


def get_air_value_df(hostname, port, selected_room, req_thread):
    df_dictionary = {
        'Date / Time': [],
        'Room': [],
        'Temperature': [],
        'Temperature Units': [],
        'CO2 Level': [],
        'CO2 Units': [],
        'Floor': [],
        'Wing': []
    }

    if req_thread.stopped():
        return None

    try:
        import argparse
        from bacnet_gateway_requests import get_value_and_units
        import datetime as dt

        # Read spreadsheet into a DataFrame.
        # Each row contains the following:
        #   - Location
        #   - Instance ID of CO2 sensor
        #   - Instance ID of temperature sensor
        if not os.path.isfile(ROOM_SENSOR_PATH):
            print('Error:\nCouldn\'t find ' + ROOM_SENSOR_PATH + '!\nShutting down program...')
            root.destroy()

        df = pd.read_csv(ROOM_SENSOR_PATH, na_filter=False, comment='#')
        if req_thread.stopped():
            return None

        chosen_room = df['Label'] == selected_room
        if req_thread.stopped():
            return None
        filtered_room = df[chosen_room]
        if req_thread.stopped():
            return None

        try:
            for row_index, row in filtered_room.iterrows():
                # Retrieve data
                temp_value, temp_units = get_value_and_units(row['Facility'], row['Temperature'], hostname, port)
                if req_thread.stopped():
                    return None
                co2_value, co2_units = get_value_and_units(row['Facility'], row['CO2'], hostname, port)
                if req_thread.stopped():
                    return None

                # Prepare to print
                temp_value = round(int(temp_value)) if temp_value else ''
                temp_units = temp_units.replace('deg ', '°') if temp_units else ''
                co2_value = round(int(co2_value)) if co2_value else ''
                co2_units = co2_units if co2_units else ''

                if req_thread.stopped():
                    return None

                # Update dictionary
                df_dictionary['Date / Time'].append(dt.datetime.now().strftime("%m/%d/%Y %H:%M"))
                if req_thread.stopped():
                    return None
                df_dictionary['Room'].append(row['Label'])
                if req_thread.stopped():
                    return None
                df_dictionary['Temperature'].append(temp_value)
                if req_thread.stopped():
                    return None
                df_dictionary['Temperature Units'].append(temp_units)
                if req_thread.stopped():
                    return None
                df_dictionary['CO2 Level'].append(co2_value)
                if req_thread.stopped():
                    return None
                df_dictionary['CO2 Units'].append(co2_units)
                if req_thread.stopped():
                    return None
                df_dictionary['Floor'].append(row['Floor'])
                if req_thread.stopped():
                    return None
                df_dictionary['Wing'].append(row['Wing'])
                if req_thread.stopped():
                    return None

                break

            if req_thread.stopped():
                return None

            return pd.DataFrame.from_dict(df_dictionary)

        except KeyboardInterrupt:
            stop()

    except KeyboardInterrupt:
        stop()


def get_air_values_df(hostname, port, selected_floor, selected_wing, background_updater):
    df_dictionary = {
        'Date / Time': [],
        'Room': [],
        'Temperature': [],
        'Temperature Units': [],
        'CO2 Level': [],
        'CO2 Units': [],
        'Floor': [],
        'Wing': []
    }

    try:
        import argparse
        from bacnet_gateway_requests import get_value_and_units
        import datetime as dt

        # Read spreadsheet into a DataFrame.
        # Each row contains the following:
        #   - Location
        #   - Instance ID of CO2 sensor
        #   - Instance ID of temperature sensor
        if not os.path.isfile(ROOM_SENSOR_PATH):
            print('Error:\nCouldn\'t find ' + ROOM_SENSOR_PATH + '!\nShutting down program...')
            root.destroy()

        df = pd.read_csv(ROOM_SENSOR_PATH, na_filter=False, comment='#')

        matching_floor = df['Floor'] == str(selected_floor)
        matching_wing = df['Wing'] == selected_wing

        filtered_rooms = df[matching_floor & matching_wing]

        # Iterate over the rows of the DataFrame, getting temperature and CO2 values for each location
        for row_index, row in filtered_rooms.iterrows():
            while True:
                if background_updater and not background_data_update:
                    time.sleep(5)
                    continue
                else:
                    try:
                        # Retrieve data
                        temp_value, temp_units = get_value_and_units(row['Facility'], row['Temperature'], hostname,
                                                                     port)
                        co2_value, co2_units = get_value_and_units(row['Facility'], row['CO2'], hostname, port)

                        # Prepare to print
                        temp_value = round(int(temp_value)) if temp_value else ''
                        temp_units = temp_units.replace('deg ', '°') if temp_units else ''
                        co2_value = round(int(co2_value)) if co2_value else ''
                        co2_units = co2_units if co2_units else ''

                        # Update dictionary
                        df_dictionary['Date / Time'].append(dt.datetime.now().strftime("%m/%d/%Y %H:%M"))
                        df_dictionary['Room'].append(row['Label'])
                        df_dictionary['Temperature'].append(temp_value)
                        df_dictionary['Temperature Units'].append(temp_units)
                        df_dictionary['CO2 Level'].append(co2_value)
                        df_dictionary['CO2 Units'].append(co2_units)
                        df_dictionary['Floor'].append(row['Floor'])
                        df_dictionary['Wing'].append(row['Wing'])

                        break

                    except KeyboardInterrupt:
                        stop()

        return pd.DataFrame.from_dict(df_dictionary)
    except KeyboardInterrupt:
        stop()


def update_loaded_data(updated_df):
    global air_values
    air_values = updated_df
    if air_values is not None:
        air_values['Wing'] = air_values['Wing'].to_string()
        fill_fields(floor.get(), str(wing.get()), measurement.get())


def add_to_cache(new_data_df):
    global air_values
    if air_values is None:
        air_values = new_data_df
    else:
        air_values = pd.concat([air_values, new_data_df], ignore_index=True)

    if air_values is not None:
        if air_values['Floor'].dtype != numpy.float64:
            air_values['Floor'] = air_values['Floor'].astype(str).astype(int)
        fill_fields(floor.get(), str(wing.get()), measurement.get())


class RequestThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, selected_floor, selected_wing):
        super(RequestThread, self).__init__()
        self._stop_event = threading.Event()
        self.selected_floor = selected_floor
        self.selected_wing = selected_wing

        req_thread = threading.Thread(target=self.request_data, args=())
        req_thread.daemon = True  # Daemonize thread
        req_thread.start()  # Start the execution

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def request_data(self):
        global background_data_update
        background_data_update = False

        if not os.path.isfile(ROOM_SENSOR_PATH):
            print('Error:\nCouldn\'t find ' + ROOM_SENSOR_PATH + '!\nShutting down program...')
            root.destroy()

        rooms = pd.read_csv(ROOM_SENSOR_PATH, na_filter=False, comment='#')
        if self.stopped():
            background_data_update = True
            return
        matching_floor = rooms['Floor'] == str(self.selected_floor)
        if self.stopped():
            background_data_update = True
            return
        matching_wing = rooms['Wing'] == self.selected_wing
        if self.stopped():
            background_data_update = True
            return

        rooms = rooms[matching_floor & matching_wing]
        if self.stopped():
            background_data_update = True
            return

        if self.stopped():
            background_data_update = True
            return

        data_df = None
        if self.stopped():
            background_data_update = True
            return

        for row_index, row in rooms.iterrows():
            if not self.stopped():
                df = get_air_value_df(HOSTNAME, PORT, row['Label'], self)
                if df is None:
                    self.stop()
                    continue
                data_df = pd.concat([data_df, df], ignore_index=True) if data_df is not None else df
                time.sleep(1)
            else:
                background_data_update = True
                return
        add_to_cache(data_df)
        if self.stopped():
            background_data_update = True
            return
        background_data_update = True


class BACnetThread(object):
    """
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.used_combos = None
        self.updated_values = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread

    def run(self):
        """ Method that runs forever """
        while True:
            # Updates the already-requested rooms
            if air_values is not None:
                # Find which floor-wing combinations have been used so far
                self.used_combos = air_values.groupby(
                    ['Wing', 'Floor']).size().reset_index()

                for row_index, row in self.used_combos.iterrows():
                    if row['Floor'] == '' and row['Wing'] == '':
                        self.used_combos.drop(row_index)
                        continue
                    df = get_air_values_df(HOSTNAME, PORT, row['Floor'], row['Wing'], True)
                    self.updated_values = pd.concat([self.updated_values, df],
                                                    ignore_index=True) if self.updated_values is not None else df
                    time.sleep(1)

                update_loaded_data(self.updated_values)

                self.updated_values = None

            time.sleep(self.interval)


class BACnetThread(object):
    """
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=10):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.used_combos = None
        self.updated_values = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()

    def run(self):
        """ Method that runs forever """
        while True:
            # Updates the already-requested rooms
            if air_values is not None:
                # Find which floor-wing combinations have been used so far
                self.used_combos = air_values.groupby(
                    ['Wing', 'Floor']).size().reset_index()

                for row_index, row in self.used_combos.iterrows():
                    if row['Floor'] == '' and row['Wing'] == '':
                        self.used_combos.drop(row_index)
                        continue
                    df = get_air_values_df(HOSTNAME, PORT, row['Floor'], row['Wing'], True)
                    self.updated_values = pd.concat([self.updated_values, df],
                                                    ignore_index=True) if self.updated_values is not None else df

                update_loaded_data(self.updated_values)

                self.updated_values = None

            time.sleep(self.interval)


thread = BACnetThread()


def update_labels(avg_measure, max_measure, max_measure_room, unit, data_timestamp):
    row_labels[0].config(text="Data last updated at: {0} EST".format(data_timestamp))
    row_labels[1].config(text=(str(round(avg_measure, 2)) + ' ' + str(unit)))
    row_labels[2].config(text=(str(round(max_measure, 2)) + ' ' + str(unit)))
    row_labels[3].config(text=str(max_measure_room))


def fill_fields(selected_floor, selected_wing, selected_measurement):
    enough_info = False
    measurement_column = 'CO2 Level' if selected_measurement == 0 else 'Temperature'
    unit_column = 'CO2 Units' if selected_measurement == 0 else 'Temperature Units'

    selected_df = None
    global request_thread

    # Check if the session cache has data, request the data otherwise
    if air_values is not None:
        matching_floor = air_values['Floor'] == selected_floor
        matching_wing = air_values['Wing'] == selected_wing
        filtered_rooms = air_values[matching_floor & matching_wing]
        if len(filtered_rooms) >= 1 and len(filtered_rooms[measurement_column]) != 0:
            # The session cache has non-empty data for the wing
            enough_info = True
            selected_df = air_values
        else:
            if request_thread is None:
                request_thread = RequestThread(selected_floor, selected_wing)
                request_thread.start()
            else:
                request_thread.stop()
                request_thread.join()
                request_thread = RequestThread(selected_floor, selected_wing)
                request_thread.start()

    else:
        if request_thread is None:
            request_thread = RequestThread(selected_floor, selected_wing)
            request_thread.start()
        else:
            request_thread.stop()
            request_thread.join()
            request_thread = RequestThread(selected_floor, selected_wing)
            request_thread.start()

    # Check if the output file from the last session has data

    if not enough_info:
        if os.path.isfile(SAVED_DATA_PATH):
            df = pd.read_csv(SAVED_DATA_PATH, index_col=0)
            if len(df[(df['Floor'] == selected_floor) & (df['Wing'] == selected_wing)]) >= 1 and len(
                    df[measurement_column]) != 0:
                # The session cache has non-empty data for the wing
                enough_info = True
                selected_df = df

    # Fallback to an emergency file
    if not enough_info:
        if os.path.isfile(DEFAULT_DATA_PATH):
            df = pd.read_csv(DEFAULT_DATA_PATH, index_col=0)
            if len(df[(df['Floor'] == selected_floor) & (df['Wing'] == selected_wing)]) >= 1 and len(
                    df[measurement_column]) != 0:
                enough_info = True
                selected_df = df

    if enough_info:

        matching_floor = selected_df['Floor'] == selected_floor
        matching_wing = selected_df['Wing'] == selected_wing

        filtered_rooms = selected_df[matching_floor & matching_wing]

        if not filtered_rooms.empty:
            filtered_rooms[measurement_column] = pd.to_numeric(filtered_rooms[measurement_column], errors='coerce')
            filtered_rooms[unit_column] = filtered_rooms[unit_column].astype(str)

        for row_index, row in filtered_rooms[measurement_column].iteritems():
            if filtered_rooms[unit_column].get(row_index) == '' or filtered_rooms[unit_column].get(row_index) == 'nan':
                continue
            unit = filtered_rooms[unit_column].get(row_index)
            break

        avg_measure = filtered_rooms[measurement_column].mean()

        max_measure = 0
        max_measure_room = 'None'

        for row_index, row in filtered_rooms.iterrows():
            if row[measurement_column] > max_measure:
                max_measure = row[measurement_column]
                max_measure_room = row['Room']

        data_timestamp = filtered_rooms['Date / Time'].get(filtered_rooms['Date / Time'].last_valid_index())

        update_labels(avg_measure, max_measure, max_measure_room, unit, data_timestamp)


root = Tk()
root.title("AHS Air Data")
root.configure(background='white')
root.resizable(False, False)

wing = StringVar(root, value='A')  # The selected wing
floor = IntVar(root, value=1)  # The selected floor
measurement = IntVar(root, value=1)  # The selected measurement


def set_wing():
    fill_fields(floor.get(), str(wing.get()), measurement.get())


def set_floor():
    for radio_index in range(1, len(wing_radios)):
        if floor.get() == 1:
            wing_radios[radio_index].grid_remove()
        else:
            wing_radios[radio_index].grid()
    fill_fields(floor.get(), str(wing.get()), measurement.get())


def set_measurement():
    fill_fields(floor.get(), str(wing.get()), measurement.get())


# Setup table layout
COLUMN_TITLES = ['Floor', 'Wing', 'Measurement', 'Average', 'Maximum', 'Room Number With Maximum']
col_number = 0
row_labels = []
wing_radios = []

for col in COLUMN_TITLES:
    label = Label(text=col, fg="Blue", bg="White", width="30")

    label.grid(row=0, column=col_number, pady=(10, 0), sticky='we', ipady="2")

    # Add floor options
    if col_number == 0:
        FLOOR_NAMES = ['1st', '2nd', '3rd']
        current_row = 1

        for floor_name in FLOOR_NAMES:
            Radiobutton(text=floor_name, fg="Black", bg="White", variable=floor, value=int(floor_name[0]),
                        command=set_floor).grid(row=current_row, column=col_number, sticky='we')
            current_row += 1

    # Add wing options
    elif col_number == 1:
        WING_LETTERS = ['A', 'B', 'C', 'D']
        current_row = 1
        for index, wing_letter in enumerate(WING_LETTERS):
            if index == len(WING_LETTERS) - 1:
                btn = Radiobutton(text=wing_letter, fg="Black", bg="White", variable=wing, value=wing_letter,
                                  command=set_wing)
                wing_radios.append(btn)
                btn.grid(row=current_row, column=col_number, sticky='we', pady=(0, 10))
            else:
                btn = Radiobutton(text=wing_letter, fg="Black", bg="White", variable=wing, value=wing_letter,
                                  command=set_wing)
                wing_radios.append(btn)
                btn.grid(row=current_row, column=col_number, sticky='we')

            current_row += 1

        row_label = Label(bg="White", fg="Blue", relief=FLAT, text="Data last updated at: 1/1/1970 00:00")
        row_labels.append(row_label)
        row_label.grid(row=current_row, column=0, columnspan=len(COLUMN_TITLES), sticky='we', ipady="2", padx=10,
                       pady=(0, 20))

    # Add measurement options

    elif col_number == 2:
        MEASUREMENTS = ['CO2', 'Temperature']
        current_row = 1

        for index, measure in enumerate(MEASUREMENTS):
            Radiobutton(text=measure, fg="Black", bg="White", variable=measurement, value=index,
                        command=set_measurement).grid(row=current_row, column=col_number, sticky='we')
            current_row += 1

    else:
        # Create empty cell for value
        row_label = Label(bg="White", fg="Black", relief=RIDGE, width="30")
        row_labels.append(row_label)

        row_label.grid(row=1, column=col_number, sticky='we', ipady="2", padx=5)

    col_number += 1

root.grid_columnconfigure(0, weight=1)
fill_fields(floor.get(), str(wing.get()), measurement.get())
try:
    for radio_index in range(1, len(wing_radios)):
        wing_radios[radio_index].grid_remove()  # Hide radios by default
    root.protocol("WM_DELETE_WINDOW", stop)
    root.mainloop()
except KeyboardInterrupt:
    stop()