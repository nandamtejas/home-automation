from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.uix.list import OneLineListItem, IRightBodyTouch,TwoLineAvatarListItem
from kivymd.uix.selectioncontrol import MDSwitch
from android.permissions import request_permissions, Permission, check_permission
from android.runnable import run_on_ui_thread
from jnius import autoclass
from plyer import notification
from pykivdroid.stt import STT

# stt initialization
stt = STT(language = 'en-US',prefer_offline = False)


# for permissions https://developer.android.com/reference/android/Manifest.permission

reds = ['ready', 'ted','braid','read','brad','trade','frad','fred','criag','tried','play','red','trade','good','did','dead','friend','our tv','turn','rent','threatened','mad','bread']
greens = ['green','cream','dream','team']
blues = ['blue','glue','clue','shoe','true','do']
all_leds_on = ["on all","turn on all led's","orlon","turn on all led","turn all on","turn on all","all on","alone","turn everything on","turn on everything"]
all_leds_off =  ["of all","turn of all","turn off all led's","turn off all led","turn of all led","turn off all","all off","off all","all of","of all","turn everything off","turn everything of","turn off everything","turn of everything"]
only_red_on = ['turn on ted led','turn on braid led','turn on bread led','only friend led','only red led','only read led','only red','only read','led red','led red on','red one','red wine','red on','red dawn','red color led on','turn on the red color one','turn on red led']
only_green_on = ['green','cream','only cream','only cream on','turn on cream led','only green on','only green led','only green','turn on green led','turn only green led','green on','green led','green led on','led green']
only_blue_on = ['blue','blue on','led blue on','blue color','only blue','only blue on','turn on blue led','turn only blue led','blue one','blue color','on blue']


only_red_on.extend(
    ['turn on ' + r + ' led' for r in only_red_on if not 'turn on ' + r + ' led' in only_red_on] + 
    ['turn '+r+' on' for r in only_red_on if not 'turn '+r+' on' in only_red_on] + 
    ['turn '+r+' led on' for r in only_red_on if 'turn '+r+' led on' not in only_red_on] + 
    ['only '+r+' led on' for r in only_red_on if 'only '+r+' led on' not in only_red_on] + 
    [r+' led only' for r in only_red_on if r+' led only' not in only_red_on] 
)

only_green_on.extend(
    ['turn on ' + r + ' led' for r in only_green_on if not 'turn on ' + r + ' led' in only_green_on] + 
    ['turn '+r+' on' for r in only_green_on if not 'turn '+r+' on' in only_green_on] + 
    ['turn '+r+' led on' for r in only_green_on if 'turn '+r+' led on' not in only_green_on] + 
    ['only '+r+' led on' for r in only_green_on if 'only '+r+' led on' not in only_green_on] + 
    [r+' led only' for r in only_green_on if r+' led only' not in only_green_on]
)

only_blue_on.extend(
    ['turn on ' + r + ' led' for r in only_blue_on if not 'turn on ' + r + ' led' in only_blue_on] + 
    ['turn '+r+' on' for r in only_blue_on if not 'turn '+r+' on' in only_blue_on] + 
    ['turn '+r+' led on' for r in only_blue_on if 'turn '+r+' led on' not in only_blue_on] + 
    ['only '+r+' led on' for r in only_blue_on if 'only '+r+' led on' not in only_blue_on] + 
    [r+' led only' for r in only_blue_on if r+' led only' not in only_blue_on]
)

only_red_on.extend(reds)
only_green_on.extend(greens)
only_blue_on.extend(blues)

only_red_off = []
only_green_off = []
only_blue_off = []

only_red_off.extend(
    [" off ".join(a.split(" on ")) for a in only_red_on if ' on ' in a] + 
    ["off ".join(a.split("on ")) for a in only_red_on if a.startswith('on ')] +
    [a + " off" for a in reds] + [a + " of" for a in reds] + ["off " + a for a in reds] + ["of " + a for a in reds]
)

only_green_off.extend(
    [" off ".join(a.split(" on ")) for a in only_green_on if ' on ' in a] + 
    ["off ".join(a.split("on ")) for a in only_green_on if a.startswith('on ')] +
    [a + " off" for a in greens] + [a + " of" for a in greens] + ["off " + a for a in greens] + ["of " + a for a in greens]
)

only_blue_off.extend(
    [" off ".join(a.split(" on ")) for a in only_blue_on if ' on ' in a] + 
    ["off ".join(a.split("on ")) for a in only_blue_on if a.startswith('on ')] +
    [a + " off" for a in blues] + [a + " of" for a in blues] + ["off " + a for a in blues] + ["of " + a for a in blues]
)

print(only_red_on)
print(only_green_on)
print(only_blue_on)
print(only_red_off)
print(only_green_off)
print(only_blue_off)

kv = '''
<IconTooltipButton@MDFloatingActionButton+MDTooltip>

ScreenManager: 
    Main:


<Main>:
    name: "Main"
    BoxLayout:
        orientation:'vertical'

        MDToolbar:
            title: 'Home Automation'
            specific_text_color: 1,1,1,1
            halign: "center"
            elevation: 100
            right_action_items: [['bluetooth-connect', lambda x: app.ss()],['bluetooth-off', lambda x: app.ble.BluetoothAdapter.getDefaultAdapter().disable()]]

        MDBottomNavigation:
            id: navigation 
            panel_color: 1,1,1,1
            text_color_active: 0,0,0,1
                

            MDBottomNavigationItem:
                id: speech_id
                name: 'screen speech'
                text: 'Speech'
                icon: 'voice'
                    

                IconTooltipButton:
                    id: speech
                    icon: 'microphone'
                    md_bg_color: app.theme_cls.primary_light
                    tooltip_text: self.icon + " input" 
                    user_font_size: '64sp'
                    pos_hint: {'center_x':0.5,'center_y':0.5}
                    on_release: root.tap_target_start()


            MDBottomNavigationItem:
                id: switch_id
                name: 'screen switch'
                text: 'Switch'
                icon: 'toggle-switch'
                ScrollView:
                    MDList:
                        id: lists

<ListItemWithSwitch>:
    text: ''
    pos_hint:{'center_x':0.8,'center_y':0.5}
    RightSwitch:
        id: root.text
        pos_hint:{'center_x':0.9,'center_y':0.5}
        on_active: app.check_send(root.text,*args)


<Item>:
    IconLeftWidget:
        icon: root.source
'''

class AndroidBluetoothClass:
    
    def getAndroidBluetoothSocket(self,DeviceName):
        self.paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in self.paired_devices:
            if device.getName() == DeviceName:
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                self.ReceiveData = self.BufferReader(self.InputStream(socket.getInputStream()))
                self.SendData = socket.getOutputStream()
                try:
                    socket.connect()
                except Exception as e:
                    notification.notify(title="BLUETOOTH",message="Bluetooth Connection Failed")
                    app.open_dialogbox(title="Bluetooth Connection Error", text=f"Bluetooth failed to connect the device {DeviceName}", size_hint = (0.5,0.5))
                    return self.ConnectionEstablished
                self.ConnectionEstablished = True
                notification.notify(title="BLUETOOTH",message="Bluetooth Connection Successful")
                app.open_dialogbox(title="Bluetooth Connection", text=f"Bluetooth successfully connected to {DeviceName}",size_hint = (0.65,0.5))
                print('Bluetooth Connection successful')
        return self.ConnectionEstablished


    def BluetoothSend(self, Message, *args):
        try:
            if self.ConnectionEstablished == True:
                self.SendData.write(Message)
                self.SendData.flush()
            else:
                notification.notify(title="BLUETOOTH",message="Bluetooth device not connected")
                app.open_dialogbox(title="Bluetooth Connection Error", text="Bluetooth device not connected properly!!",size_hint = (0.8,0.8))
        except Exception as e:
            print(str(e))
            self.EnableBluetooth()
            if args:
                print(args[0])
                self.getAndroidBluetoothSocket(args[0])


    def BluetoothReceive(self,*args):
        DataStream = ''
        if self.ConnectionEstablished == True:
            DataStream = str(self.ReceiveData.readline())
        return DataStream

    def EnableBluetooth(self):
        if not self.BluetoothAdapter.getDefaultAdapter().isEnabled():
            self.BluetoothAdapter.getDefaultAdapter().enable()
    
    def DisableBluetooth(self):
        self.BluetoothAdapter.getDefaultAdapter().disable()

    def getAllPairedDevices(self):
        if not self.BluetoothAdapter.getDefaultAdapter().isEnabled():
            self.EnableBluetooth()
        return [{"Name": device.getName(), "Address": device.getAddress()} for device in self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()]


    def __init__(self):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.BufferReader = autoclass('java.io.BufferedReader')
        self.InputStream = autoclass('java.io.InputStreamReader')
        self.ConnectionEstablished = False
        self.paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()


    def __del__(self):
        print('class AndroidBluetooth destroyer')


class ListItemWithSwitch(OneLineListItem):
    pass

class RightSwitch(IRightBodyTouch,MDSwitch):
    pass
        
class Item(TwoLineAvatarListItem):
    source = StringProperty()

class Main(Screen):

    def tap_target_start(self):
        app.builder.get_screen("Main").ids.speech.md_bg_color = app.theme_cls.primary_light
        
        if app.tap_target_view.state == "close":
            if not check_permission(Permission.RECORD_AUDIO):
                request_permissions([Permission.RECORD_AUDIO])
            app.tap_target_view.start()
            app.tap_target_view.on_open(self.listen_speech())
        else:
            app.tap_target_view.stop()
            app.tap_target_view.on_close(self.stop_listening())            

    def listen_speech(self):
        if stt.listening:
            self.stop_listening()
            return

        a = "Listening"
        b = "Recognizing"

        self.results_text = ''
        self.partial_text = ''
        try:
            stt.start()
            app.tap_target_view.title_text = a
            Clock.schedule_interval(self.check_state, 1 / 5)
        except NotImplementedError:
            pass

    def stop_listening(self):
        a = "Listening"
        b = "Recognizing"

        try:
            stt.stop()
            self.update()
            Clock.unschedule(self.check_state)
        except NotImplementedError:
            pass

    def check_state(self, dt):
        # if the recognizer service stops, change UI
        if not stt.listening:
            self.stop_listening()

    def update(self):
        app.builder.get_screen("Main").ids.speech.md_bg_color = app.theme_cls.primary_light
        if app.tap_target_view.state != 'close':
            app.tap_target_view.stop()
        self.partial_text = '\n'.join(stt.partial_results)
        self.results_text = stt.results[-1] if stt.results != [] else 'empty'
        print(f"{stt.results[-1] = }"  if stt.results != [] else 'empty')
        
        if self.results_text.lower() in only_red_on:
            app.send_data(message = b"red")
        elif self.results_text.lower() in only_red_off:
            app.send_data(message = b"red off")
        elif self.results_text.lower() in only_green_on:
            app.send_data(message = b"green")
        elif self.results_text.lower() in only_green_off:
            app.send_data(message = b"green off")
        elif self.results_text.lower() in only_blue_on:
            app.send_data(message = b"blue")
        elif self.results_text.lower() in only_blue_off:
            app.send_data(message = b"blue off")
        elif self.results_text.lower() in all_leds_on:
            app.send_data(message = b"all")
        elif self.results_text.lower() in all_leds_off:
            app.send_data(message = b"all off")
        
        print(f"{self.results_text.lower() = }")
        

sm = ScreenManager()
sm.add_widget(Main(name="Main"))

class TestApp(MDApp):

    def build(self):
        self.device = None
        self.ble = AndroidBluetoothClass()
        self.ble.BluetoothAdapter.getDefaultAdapter().enable()
        self.builder = Builder.load_string(kv)
        self.tap_target_view = MDTapTargetView(
            widget = self.builder.get_screen("Main").ids.speech,
            title_text = "This is demo",
            title_text_size = "25dp",
            title_position = "bottom",
            description_text = " ",
            widget_position = "center",
            target_radius = '60dp',
            outer_circle_color = (0.1,0.5,1),
            draw_shadow = True
        )
        for t in ["RED","GREEN","BLUE"]:
           self.builder.get_screen("Main").ids.lists.add_widget(ListItemWithSwitch(text=t))
        request_permissions([
          Permission.INTERNET,
          Permission.BLUETOOTH,
          Permission.BLUETOOTH_ADMIN
        ])
        return self.builder

    def check_send(self,msg,checkbox,value):
        text = None
        if msg == "RED":
            text = b"red"
        elif msg == "GREEN":
            text = b"green"
        elif msg == "BLUE":
            text = b"blue"
        if value:
            self.send_data(message=text)
        else:
            self.send_data(message=text + b" off")

        if text is None:
            self.send_data(message=b"all off")


    @run_on_ui_thread
    def send_data(self,message:bytes):
        if not self.device:
            self.open_dialogbox(title = "Bluetooth Error", text = "Bluetooth not connected")
            return
        print(f"{message = }")
        self.ble.BluetoothSend(message,self.device)
        
    
    def open_dialogbox(self,title,text,**kwargs):
        ok_btn = MDFlatButton(text = "OK", text_color = self.theme_cls.primary_color,on_release=self.close_dialog)
        buttons = kwargs['buttons'] if 'buttons' in kwargs else [ok_btn]
        items = kwargs['Items'] if 'Items' in kwargs else []
        size = kwargs['size_hint'] if 'size_hint' in kwargs else (0.65,0.55)
        if items != []:
            self.dialog = MDDialog(title = title,text=text,type='confirmation', items=items, buttons = buttons, size_hint = size)
            self.dialog.open()
            return
        self.dialog = MDDialog(title = title,text=text, buttons = buttons, size_hint = size)
        self.dialog.open()

    
    def close_dialog(self,instance):
        self.dialog.dismiss()
    
    
    def ss(self):
        if not self.ble.BluetoothAdapter.getDefaultAdapter().isEnabled():
            self.ble.EnableBluetooth()   
            self.open_dialogbox(title="Bluetooth Connection", text="Bluetooth Connection Success",size_hint = (0.8,0.8))
            return 
        else:
            items = [Item(
                text = device.get('Name'),
                secondary_text = device.get('Address'),
                source = 'bluetooth-connect',
                on_release = self.connect) for device in self.ble.getAllPairedDevices()]
            self.open_dialogbox(title="Paired Devices", text="Paired Devices",Items = items,size_hint = (0.8,0.8))
    
    
    def connect(self,instance):
        self.close_dialog(instance)
        self.device = instance.text
        self.ble.getAndroidBluetoothSocket(instance.text)        

    def on_start(self): 
        #request_permissions([Permission.RECORD_AUDIO,Permission.BLUETOOTH,Permission.BLUETOOTH_ADMIN,Permission.ACCESS_FINE_LOCATION,Permission.INTERNET])
        pass
    
    def on_pause(self):
        self.ble.BluetoothAdapter.getDefaultAdapter().disable()
        return True

if __name__ == "__main__":
    app = TestApp()
    app.run()