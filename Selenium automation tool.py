import threading
import time
import tkinter as tk
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

def close_tab(browser,original):
    chld=browser.window_handles[1]
    browser.switch_to.window(chld)
    browser.close()
    browser.switch_to.window(original)

class Account():
    def __init__(self, account_number, interface):
        self.thread = threading.Thread(target=self.func)
        self.account_number = account_number
        self.interface = interface
        self.running = False
        self.stopped = threading.Event()  # Event to signal thread to stop
        self.state="init"

    def func(self):
        
        option=Options()
        #option.add_argument('--headless')
        self.browser=uc.Chrome(options=option)
        self.browser.get("https://freecash.com/earn")
        while not self.stopped.is_set():
            if self.running:
                original=self.browser.current_window_handle
                while self.running:
                    try:
                        frame=self.browser.find_element(By.XPATH,"//iframe[@title='timewall']")
                        self.browser.switch_to.frame(frame)
                        button= self.browser.find_elements(By.XPATH,"/html/body/div[@id='sc-page-wrapper']/div[@id='sc-page-content']/div/div/div/div/div/div/div/div/div/div/div/div/ul/li/a")
                        time_string = self.browser.find_elements(By.CLASS_NAME,"clickTimer")
                        adtime=int(time_string[0].text)
                        button[0].click()
                        time.sleep(adtime+5)
                        
                      
                        close_tab(self.browser,original)
                        time.sleep(3)
                    except Exception as e:
                        self.browser.switch_to.window(original)
                        self.running = False
                        self.interface.after(0, self.update_buttons, tk.DISABLED, tk.NORMAL)
                        self.interface.after(0, self.update_state, "error")
                        break
            time.sleep(3)
        
    def start(self):
        self.thread.start()

    def create_interface(self):
        self.stop_button = tk.Button(self.interface, text=f'Stop {self.account_number}', command=self.stop_loop, state=tk.DISABLED)
        self.stop_button.pack()
        self.continue_button = tk.Button(self.interface, text=f'Continue {self.account_number}', command=self.continue_loop, state=tk.NORMAL)
        self.continue_button.pack()
        self.end_button=tk.Button(self.interface,text=f'end{self.account_number}',command=self.end)
        self.end_button.pack()
        self.state_label=tk.Label(self.interface,text=self.state)
        self.state_label.pack()
    
    def stop_loop(self):
        self.running = False
        self.interface.after(0, self.update_buttons, tk.DISABLED, tk.NORMAL)
        self.interface.after(0, self.update_state, "stopped")

    def continue_loop(self):
        self.running = True
        self.stopped.clear()  # Clear the event to signal thread to continue
        self.interface.after(0, self.update_buttons, tk.NORMAL, tk.DISABLED)
        self.interface.after(0, self.update_state, "running")
    
    def update_state(self,newstate):
        self.state_label.config(text=newstate)

    def update_buttons(self, stop_state, continue_state):
        self.stop_button.config(state=stop_state)
        self.continue_button.config(state=continue_state)

    def end(self):
        self.interface.after(0, self.update_buttons, tk.DISABLED, tk.DISABLED)
        self.stopped.set()
        try:
            self.browser.close()
        except:
            pass

class Interface():
    def __init__(self):
        self.accounts = []
        self.account_number = 0
        self.interface = tk.Tk()
        self.interface.geometry('200x200')
        self.add_button = tk.Button(self.interface, text="Add account", command=self.add_account)
        self.add_button.pack()
        self.close_button = tk.Button(self.interface, text="Close", command=self.close)
        self.close_button.pack()

    def close(self):
        for account in self.accounts:
            account.end()  # Stop all running threads
            account.thread.join()  # Wait for threads to finish
        self.interface.destroy()
        

    def run(self):
        self.interface.mainloop()

    def add_account(self):
        
        self.account_number += 1
        print(self.account_number)
        new_account = Account(self.account_number, self.interface)
        self.accounts.append(new_account)
        new_account.create_interface()
        new_account.start()

if __name__ == '__main__':
    interface_instance = Interface()
    interface_instance.run()
