import re
# import threading


class DarknetLogParser:

    def __init__(self, log_path: str):
        # re
        self.iteration_pattern = re.compile(r'(\d.*):(.*)')
        self.next_map_in_pattern = re.compile(r'next mAP calculation at (\d.*) iterations')
        self.map_info_pattern = re.compile(r'Last accuracy mAP@0.5 = (\d.*) %, best = (\d.*) %')

        # file path
        self.log_path = log_path

        # training indo
        self.next_map_calculation = -1
        self.map_calculation_iterations = []
        self.map_list = []
        self.best_map = -1
        self.losses = []
        self.taked_times = []
        self.hours_left = -1

    def follow(self, thefile):
        from_beginning = True
        while True:
            if from_beginning:
                for line in thefile.readlines():
                    yield line
                    # time.sleep(0.05)
            else:
                thefile.seek(0, 2)
                from_beginning = True

    def extract_iteration_info(self, line: str):
        info_splt = [i.strip() for i in line.split(',')]
        if len(info_splt) < 6:
            print('wtf', info_splt)
            return None
        avg_loss = float(info_splt[1].split()[0])
        taked_time = float(info_splt[3].split()[0])
        time_left = float(info_splt[5].split()[0])
        return (avg_loss, taked_time, time_left)

    def run(self):
        logfile = open(self.log_path, "r")

        loglines = self.follow(logfile)
        for line in loglines:
            line = line.strip()

            # Iteration info
            if self.iteration_pattern.match(line):
                extracted = self.extract_iteration_info(line)
                if extracted is not None:
                    loss, taked_time, time_left = extracted
                    self.losses.append(loss)
                    self.taked_times.append(taked_time)
                    self.hours_left = time_left
                continue

            # Next map calculation info
            if self.next_map_calculation == -1 or len(self.losses) > self.next_map_calculation:

                finded = self.next_map_in_pattern.findall(line)
                if len(finded) == 1:
                    next_map_calculation = int(finded[0])
                    if next_map_calculation not in self.map_calculation_iterations:

                        if self.next_map_calculation != -1:
                            self.map_calculation_iterations.append(self.next_map_calculation)
                        self.next_map_calculation = next_map_calculation

            if len(self.map_list) < len(self.map_calculation_iterations):
                finded = self.map_info_pattern.findall(line)
                if len(finded) == 1 and len(finded[0]) == 2:
                    last_map = float(finded[0][0])
                    best_map = float(finded[0][1])
                    self.map_list.append(last_map)
                    self.best_map = best_map
