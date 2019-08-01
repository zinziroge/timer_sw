import RPi.GPIO as GPIO
import time
import os, sys, time
import Tkinter as Tk # python 2.7
import threading


SW_1_PIN = 18 # BCM, PHY 12pin
SW_2_PIN = 24 # BCM, PHY 18pin
TIMER_PERIOD_SEC = 0.05
SW_BOUNCE_T_MSEC = 300 # chattering time


def setup_io():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(
        SW_1_PIN, GPIO.IN,
        pull_up_down=GPIO.PUD_UP)
    GPIO.setup(
        SW_2_PIN, GPIO.IN,
        pull_up_down=GPIO.PUD_UP)


def main():
    while(True):
        print(SW_1_PIN, GPIO.input(SW_1_PIN))
        print(SW_2_PIN, GPIO.input(SW_2_PIN))

        time.sleep(0.1)


#######################################
class TimerScore(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.pack()
        self.focus_set()
        self.bind("<Key>", self.callback_keyPress)
        self.create_widgets()
        self.btn_stop["state"] = "disable"

        self.init_gpio_event()
        self.does_p1_play = False
        self.does_p2_play = False

    def init_gpio_event(self):
        GPIO.add_event_detect(
            SW_1_PIN, GPIO.FALLING,
            bouncetime=SW_BOUNCE_T_MSEC)
        GPIO.add_event_callback(
            SW_1_PIN, self.callback_detect_sw)
        GPIO.add_event_detect(
            SW_2_PIN, GPIO.FALLING,
            bouncetime=SW_BOUNCE_T_MSEC)
        GPIO.add_event_callback(
            SW_2_PIN, self.callback_detect_sw)

    def create_widgets(self):
        cur_t = "{0:06.2f}".format(0)

        # player 1
        self.p1_time_text = Tk.StringVar()
        self.p1_time_text.set(cur_t)
        self.lbl_p1 = Tk.Label(
            self,
            text="Player 1",
            width=10, font=("", 30))
        self.lbl_p1_time = Tk.Label(
            self,
            textvariable=self.p1_time_text,
            width=10, height=2, font=("", 40))

        # player 2
        self.p2_time_text = Tk.StringVar()
        self.p2_time_text.set(cur_t)
        self.lbl_p2 = Tk.Label(
            self, text="Player 2",
            width=10, font=("", 30))
        self.lbl_p2_time = Tk.Label(
            self,
            textvariable=self.p2_time_text,
            width=10, height=2, font=("", 40))
            
        self.btn_start = Tk.Button(
            self, text="Start",
            width=20, font=("", 30),
            command=self.callback_btn_start)
        self.btn_stop = Tk. Button(
            self, text="Stop",
            width=20, font=("", 30),
            command=self.callback_btn_stop)
        self.btn_reset = Tk. Button(
            self, text="Reset",
            width=10, font=("", 10),
            command=self.callback_btn_reset)

        # grid
        self.lbl_p1.grid(row=0, column=0)
        self.lbl_p2.grid(row=0, column=1)
        self.lbl_p1_time.grid(row=1, column=0)
        self.lbl_p2_time.grid(row=1, column=1)
        self.btn_start.grid(
            row=2, column=0, columnspan=2)
        self.btn_stop.grid(
            row=3, column=0, columnspan=2)
        self.btn_reset.grid(
            row=4, column=1)

    def start_timer(self):
        self.does_p1_play = True
        self.does_p2_play = True
        self.btn_start["state"] = "disable"
        self.btn_stop["state"] = "normal"

        self.start_time = time.time() # second
        self.timer_thread = threading.Timer(
            TIMER_PERIOD_SEC, self.timer_event)
        self.timer_thread.start()

    def timer_event(self):
        t = "{0:06.2f}".format(
            time.time() - self.start_time)
        print(t)

        if(self.does_p1_play):
            self.p1_time_text.set(t)
        if(self.does_p2_play):
            self.p2_time_text.set(t)

        if(not self.does_p1_play and
           not self.does_p2_play):
            # don't creat next timer
            print("stop timer")
            self.callback_btn_stop()
        else:
            # start next timer
            self.timer_thread = threading.Timer(
                TIMER_PERIOD_SEC, self.timer_event)
            self.timer_thread.start()

    def callback_detect_sw(self, gpio_pin):
        # start timer
        if(gpio_pin == SW_1_PIN or
           gpio_pin == SW_2_PIN):
            if(not self.does_p1_play and
               not self.does_p2_play):
                # start
                print("start timer, cause button pushed.")
                self.start_timer()
                return

        # stop some player's timer
        t = "{0:06.2f}".format(
            time.time() - self.start_time)
        print(gpio_pin, t)

        if(gpio_pin == SW_1_PIN):
            if(self.does_p1_play):
                # stop player1's timer
                self.does_p1_play = False
                self.p1_time_text.set(t)
                print("stop player1's timer")

        if(gpio_pin == SW_2_PIN):
            if(self.does_p2_play):
                # stop player2's timer
                self.does_p2_play = False
                self.p2_time_text.set(t)
                print("stop player2's timer")

    def callback_btn_start(self):
        self.start_timer()

    def callback_btn_stop(self):
        self.timer_thread.cancel()
        self.btn_start["state"] = "normal"
        self.btn_stop["state"] = "disable"
        self.does_p1_play = False
        self.does_p2_play = False

    def callback_btn_reset(self):
        cur_t = "{0:06.2f}".format(0)
        self.p1_time_text.set(cur_t)
        self.p2_time_text.set(cur_t)
        self.btn_start["state"] = "normal"
        self.btn_stop["state"] = "disable"
        self.does_p1_play = False
        self.does_p2_play = False
        if(self.timer_thread.is_alive()):
            self.timer_thread.cancel()

    def callback_keyPress(self, event):
        if(event.keysym == "q"):
            exit()


#######################################
if __name__ == "__main__":
    setup_io()

    root = Tk.Tk()
    # root.geometry("400x300")
    # root.attributes("-zoomed", True)
    root.attributes("-fullscreen", True)
    app = TimerScore(master=root)
    app.mainloop()
    root.destroy()
    # main()
